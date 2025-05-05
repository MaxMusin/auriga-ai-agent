import optuna
import numpy as np
import json
import logging
from datetime import datetime
from src.config.constants import CAR_SETUP_PARAMETERS, SETUP_STATUS, SETUP_SOURCE
from src.storage.repository import SetupRepository, OptimizationRepository
from src.core.scoring import SetupScorer

logger = logging.getLogger(__name__)

class SetupOptimizer:
    """Classe gérant l'optimisation des setups via Optuna"""
    
    def __init__(self, car_id, track_id, optimization_params=None):
        """
        Initialise l'optimiseur pour une voiture et une piste spécifiques
        
        Args:
            car_id (str): Identifiant de la voiture (ex: "mx5")
            track_id (str): Identifiant du circuit (ex: "spa")
            optimization_params (dict): Paramètres d'optimisation personnalisés
        """
        self.car_id = car_id
        self.track_id = track_id
        
        # Paramètres d'optimisation par défaut
        self.default_params = {
            "n_trials": 30,               # Nombre d'essais à effectuer
            "timeout": 86400,             # Timeout en secondes (24h)
            "sampler": "tpe",             # TPE, CMA-ES, Random, etc.
            "pruner": "hyperband",        # Méthode d'élagage
            "direction": "maximize",      # Direction d'optimisation (maximize pour le score)
            "seed": 42,                   # Graine aléatoire
            "initial_setups": 5,          # Nombre de setups initiaux à tester
            "exploration_weight": 0.3,    # Poids pour l'exploration (vs exploitation)
        }
        
        # Utilise les paramètres fournis ou les paramètres par défaut
        self.params = optimization_params if optimization_params else self.default_params
        
        # Vérifie si les paramètres de la voiture existent
        if car_id not in CAR_SETUP_PARAMETERS:
            raise ValueError(f"Configuration non trouvée pour la voiture: {car_id}")
            
        self.car_params = CAR_SETUP_PARAMETERS[car_id]
        self.study = None
        self.session_id = None
        self.scorer = SetupScorer()
        
    def _create_parameter_space(self, trial):
        """
        Crée l'espace des paramètres pour Optuna
        
        Args:
            trial: Instance de trial Optuna
            
        Returns:
            dict: Paramètres du setup générés par Optuna
        """
        setup_params = {}
        
        # Pour chaque paramètre défini pour cette voiture
        for param_name, param_config in self.car_params.items():
            min_val = param_config["min"]
            max_val = param_config["max"]
            step = param_config.get("step", None)
            
            # Traite différemment selon le type de paramètre
            if isinstance(min_val, int) and isinstance(max_val, int):
                # Paramètre entier
                setup_params[param_name] = trial.suggest_int(param_name, min_val, max_val, step)
            else:
                # Paramètre flottant
                setup_params[param_name] = trial.suggest_float(param_name, min_val, max_val, step=step)
                
        return setup_params
    
    def _objective(self, trial):
        """
        Fonction objectif pour Optuna. Cette fonction est appelée pour chaque essai.
        
        Args:
            trial: Instance de trial Optuna
            
        Returns:
            float: Score du setup (plus élevé = meilleur)
        """
        # Génère les paramètres du setup
        setup_params = self._create_parameter_space(trial)
        
        # Sauvegarde le setup dans la base de données
        setup_id = SetupRepository.create_setup(
            car_id=self.car_id,
            track_id=self.track_id,
            setup_parameters=setup_params,
            status=SETUP_STATUS["PENDING"],
            source=SETUP_SOURCE["OPTIMIZED"],
            optimization_session_id=self.session_id
        )
        
        if setup_id is None:
            logger.error("Erreur lors de la création du setup")
            return 0.0
        
        # Stocke l'ID du setup dans le trial pour référence future
        trial.set_user_attr("setup_id", setup_id)
        
        # En mode asynchrone, on retourne une valeur fictive
        # Le vrai score sera mis à jour plus tard via callback
        return 0.0
    
    def update_trial_score(self, setup_id, telemetry_data):
        """
        Met à jour le score d'un trial après réception des données de télémétrie
        
        Args:
            setup_id (int): ID du setup testé
            telemetry_data (dict): Données de télémétrie
            
        Returns:
            float: Score calculé
        """
        if self.study is None:
            logger.error("Aucune étude d'optimisation active")
            return None
            
        # Calcule le score
        score = self.scorer.calculate_score(telemetry_data)
        
        # Met à jour le statut et le score du setup
        SetupRepository.update_setup_status(
            setup_id=setup_id,
            status=SETUP_STATUS["TESTED"],
            score=score
        )
        
        # Cherche le trial correspondant et met à jour son score
        for trial in self.study.trials:
            if trial.user_attrs.get("setup_id") == setup_id:
                self.study.tell(trial.number, score)
                break
        
        # Vérifie si c'est le meilleur setup jusqu'à présent
        best_trial = self.study.best_trial
        if best_trial and best_trial.user_attrs.get("setup_id") == setup_id:
            OptimizationRepository.update_best_setup(
                session_id=self.session_id,
                best_setup_id=setup_id
            )
        
        return score
    
    def start_optimization(self):
        """
        Démarre une nouvelle session d'optimisation
        
        Returns:
            int: ID de la session créée
        """
        # Crée la session d'optimisation
        self.session_id = OptimizationRepository.create_session(
            car_id=self.car_id,
            track_id=self.track_id,
            optimization_parameters=self.params
        )
        
        if self.session_id is None:
            logger.error("Erreur lors de la création de la session d'optimisation")
            return None
        
        # Configure le sampler Optuna
        if self.params["sampler"] == "tpe":
            sampler = optuna.samplers.TPESampler(seed=self.params["seed"])
        elif self.params["sampler"] == "cmaes":
            sampler = optuna.samplers.CmaEsSampler(seed=self.params["seed"])
        elif self.params["sampler"] == "random":
            sampler = optuna.samplers.RandomSampler(seed=self.params["seed"])
        else:
            sampler = optuna.samplers.TPESampler(seed=self.params["seed"])
        
        # Configure le pruner Optuna
        if self.params["pruner"] == "hyperband":
            pruner = optuna.pruners.HyperbandPruner()
        elif self.params["pruner"] == "median":
            pruner = optuna.pruners.MedianPruner()
        else:
            pruner = None
        
        # Crée l'étude Optuna
        self.study = optuna.create_study(
            sampler=sampler,
            pruner=pruner,
            direction=self.params["direction"],
            study_name=f"{self.car_id}_{self.track_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Lance les premiers trials
        self.study.optimize(
            self._objective,
            n_trials=self.params["initial_setups"],
            timeout=self.params["timeout"],
            n_jobs=1  # Asynchrone, donc limité à 1 job
        )
        
        return self.session_id
    
    def generate_next_setup(self):
        """
        Génère le prochain setup à tester en utilisant Optuna
        
        Returns:
            int: ID du setup généré
        """
        if self.study is None or self.session_id is None:
            logger.error("Aucune optimisation active")
            return None
        
        # Lance un nouveau trial
        trial = self.study.ask()
        
        # Génère les paramètres du setup
        setup_params = self._create_parameter_space(trial)
        
        # Sauvegarde le setup
        setup_id = SetupRepository.create_setup(
            car_id=self.car_id,
            track_id=self.track_id,
            setup_parameters=setup_params,
            status=SETUP_STATUS["PENDING"],
            source=SETUP_SOURCE["OPTIMIZED"],
            optimization_session_id=self.session_id
        )
        
        if setup_id is None:
            logger.error("Erreur lors de la création du setup")
            return None
        
        # Stocke l'ID du setup dans le trial
        trial.set_user_attr("setup_id", setup_id)
        
        return setup_id
    
    def stop_optimization(self):
        """
        Arrête la session d'optimisation en cours
        
        Returns:
            bool: True si succès, False sinon
        """
        if self.session_id is None:
            logger.error("Aucune optimisation active")
            return False
        
        # Ferme la session
        success = OptimizationRepository.close_session(self.session_id)
        
        if success:
            self.session_id = None
            self.study = None
            
        return success

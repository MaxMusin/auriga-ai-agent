import numpy as np
from src.config.constants import PERFORMANCE_METRICS

class SetupScorer:
    """Classe responsable de l'évaluation des performances d'un setup"""
    
    def __init__(self, weight_config=None):
        """
        Initialise le scoreur avec une configuration de poids
        
        Args:
            weight_config (dict): Configuration des poids pour chaque métrique
                                 Si None, utilise une configuration par défaut
        """
        # Configuration par défaut des poids (priorité au temps au tour)
        self.default_weights = {
            "lap_time": 10.0,                # Le plus important
            "tire_avg_temp_fl": 1.0,
            "tire_avg_temp_fr": 1.0,
            "tire_avg_temp_rl": 1.0,
            "tire_avg_temp_rr": 1.0,
            "tire_wear_fl": 2.0,
            "tire_wear_fr": 2.0,
            "tire_wear_rl": 2.0,
            "tire_wear_rr": 2.0,
            "car_stability": 3.0,
            "corner_entry_stability": 2.0,
            "corner_exit_stability": 2.0,
            "traction": 3.0,
            "braking_stability": 2.0,
        }
        
        # Utilise les poids fournis ou la configuration par défaut
        self.weights = weight_config if weight_config else self.default_weights
        
        # Normalisation et orientation des métriques
        # 1 = higher is better (ex: stability), -1 = lower is better (ex: lap_time)
        self.metric_orientation = {
            "lap_time": -1.0,                # Plus bas est meilleur
            "tire_avg_temp_fl": self._temp_orientation,  # Fonction spéciale
            "tire_avg_temp_fr": self._temp_orientation,
            "tire_avg_temp_rl": self._temp_orientation,
            "tire_avg_temp_rr": self._temp_orientation,
            "tire_wear_fl": -1.0,            # Plus bas est meilleur
            "tire_wear_fr": -1.0,
            "tire_wear_rl": -1.0,
            "tire_wear_rr": -1.0,
            "car_stability": 1.0,            # Plus haut est meilleur
            "corner_entry_stability": 1.0,
            "corner_exit_stability": 1.0,
            "traction": 1.0,
            "braking_stability": 1.0,
        }
        
        # Plages idéales pour certaines métriques
        self.ideal_ranges = {
            "tire_avg_temp_fl": (80, 90),    # Plage idéale en °C
            "tire_avg_temp_fr": (80, 90),
            "tire_avg_temp_rl": (80, 90),
            "tire_avg_temp_rr": (80, 90),
        }
        
        # Historique des métriques pour la normalisation
        self.metric_history = {metric: [] for metric in PERFORMANCE_METRICS}
    
    def _temp_orientation(self, value, tire_position):
        """Calcule l'orientation de la température (pénalise l'écart à la plage idéale)"""
        min_temp, max_temp = self.ideal_ranges[f"tire_avg_temp_{tire_position}"]
        
        if min_temp <= value <= max_temp:
            return 1.0  # Dans la plage idéale
        elif value < min_temp:
            # Pénalité légère pour température trop basse
            return 1.0 - 0.1 * (min_temp - value)
        else:
            # Pénalité plus forte pour température trop élevée
            return 1.0 - 0.2 * (value - max_temp)
    
    def update_history(self, telemetry_data):
        """Met à jour l'historique des métriques avec de nouvelles données"""
        for metric in PERFORMANCE_METRICS:
            if metric in telemetry_data:
                self.metric_history[metric].append(telemetry_data[metric])
    
    def normalize_metric(self, metric_name, value):
        """Normalise une métrique en fonction de son historique"""
        history = self.metric_history.get(metric_name, [])
        
        if not history:
            return value  # Pas d'historique, retourne la valeur brute
        
        if metric_name.startswith("tire_avg_temp_"):
            # Pour les températures, utilise une fonction spéciale
            tire_position = metric_name[-2:]  # ex: 'fl', 'fr', etc.
            return self._temp_orientation(value, tire_position)
            
        # Pour les autres métriques, normalise par rapport à min/max
        min_val = min(history)
        max_val = max(history)
        
        if min_val == max_val:
            return 0.5  # Évite division par zéro
            
        # Normalisation entre 0 et 1
        normalized = (value - min_val) / (max_val - min_val)
        
        # Applique l'orientation (-1 pour inverser si lower is better)
        orientation = self.metric_orientation.get(metric_name, 1.0)
        if isinstance(orientation, float) and orientation < 0:
            normalized = 1.0 - normalized
            
        return normalized
    
    def calculate_score(self, telemetry_data):
        """
        Calcule un score global pour un setup basé sur les données de télémétrie
        
        Args:
            telemetry_data (dict): Données de télémétrie
            
        Returns:
            float: Score global (plus élevé = meilleur)
        """
        # Mise à jour de l'historique
        self.update_history(telemetry_data)
        
        # Calcul du score pour chaque métrique
        scores = {}
        total_weight = 0
        
        for metric in PERFORMANCE_METRICS:
            if metric in telemetry_data and metric in self.weights:
                # Normalise la métrique
                normalized_value = self.normalize_metric(metric, telemetry_data[metric])
                
                # Applique le poids
                weight = self.weights[metric]
                scores[metric] = normalized_value * weight
                total_weight += weight
        
        # Calcul du score global (moyenne pondérée)
        if total_weight == 0:
            return 0.0
            
        global_score = sum(scores.values()) / total_weight
        
        return global_score

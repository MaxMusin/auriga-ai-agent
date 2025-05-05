from flask import Blueprint, request, jsonify
import json
from src.api.schemas import TelemetryData, OptimizationParameters, SetupResponse, OptimizationStatus
from src.storage.repository import SetupRepository, TelemetryRepository, OptimizationRepository
from src.core.optimizer import SetupOptimizer
from src.core.scoring import SetupScorer
from src.core.setup_generator import SetupGenerator
from src.config.constants import SETUP_STATUS, SETUP_SOURCE

# Création du Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Optimiseur global pour l'application
optimizer = None
scorer = SetupScorer()

@api_bp.route('/telemetry', methods=['POST'])
def receive_telemetry():
    """
    Endpoint pour recevoir les données de télémétrie
    
    POST /api/v1/telemetry
    """
    try:
        data = request.json
        telemetry = TelemetryData(**data)
        
        # Enregistre les données de télémétrie
        telemetry_id = TelemetryRepository.save_telemetry(
            setup_id=telemetry.setup_id,
            lap_time=telemetry.lap_time,
            telemetry_data=telemetry.telemetry_data,
            weather_conditions=telemetry.weather_conditions,
            driver_notes=telemetry.driver_notes
        )
        
        if telemetry_id is None:
            return jsonify({"error": "Erreur lors de l'enregistrement de la télémétrie"}), 500
        
        # Calcule le score et met à jour le setup
        global optimizer
        if optimizer is not None:
            score = optimizer.update_trial_score(
                setup_id=telemetry.setup_id,
                telemetry_data=telemetry.telemetry_data
            )
        else:
            # Utilise le scoreur si l'optimiseur n'est pas initialisé
            score = scorer.calculate_score(telemetry.telemetry_data)
            SetupRepository.update_setup_status(
                setup_id=telemetry.setup_id,
                status=SETUP_STATUS["TESTED"],
                score=score
            )
        
        # Génère un nouveau setup si nécessaire
        next_setup_id = None
        if optimizer is not None:
            next_setup_id = optimizer.generate_next_setup()
        
        return jsonify({
            "success": True,
            "telemetry_id": telemetry_id,
            "score": score,
            "next_setup_id": next_setup_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/setup/next', methods=['GET'])
def get_next_setup():
    """
    Endpoint pour récupérer le prochain setup à tester
    
    GET /api/v1/setup/next
    """
    try:
        # Récupère le prochain setup en attente
        setup = SetupRepository.get_pending_setup()
        
        if setup is None:
            return jsonify({"error": "Aucun setup en attente"}), 404
        
        # Génère le fichier de setup
        file_path = SetupGenerator.generate_setup_file(setup.id)
        
        # Prépare la réponse
        response = {
            "id": setup.id,
            "car_id": setup.car_id,
            "track_id": setup.track_id,
            "setup_parameters": setup.setup_parameters,
            "generation_time": setup.generation_time.isoformat(),
            "status": setup.status,
            "source": setup.source,
            "file_path": file_path
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/setup/current', methods=['GET'])
def get_current_setup():
    """
    Endpoint pour récupérer le setup actuellement testé
    
    GET /api/v1/setup/current
    """
    try:
        setup_id = request.args.get('id')
        
        if setup_id is None:
            return jsonify({"error": "ID de setup requis"}), 400
        
        # Récupère le setup
        setup = SetupRepository.get_setup_by_id(int(setup_id))
        
        if setup is None:
            return jsonify({"error": "Setup non trouvé"}), 404
        
        # Prépare la réponse
        response = {
            "id": setup.id,
            "car_id": setup.car_id,
            "track_id": setup.track_id,
            "setup_parameters": setup.setup_parameters,
            "generation_time": setup.generation_time.isoformat(),
            "status": setup.status,
            "source": setup.source,
            "score": setup.score
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/optimization/start', methods=['POST'])
def start_optimization():
    """
    Endpoint pour démarrer une nouvelle session d'optimisation
    
    POST /api/v1/optimization/start
    """
    try:
        data = request.json
        params = OptimizationParameters(**data)
        
        # Vérifie s'il y a déjà une optimisation active
        active_session = OptimizationRepository.get_active_session()
        if active_session:
            return jsonify({
                "error": "Une session d'optimisation est déjà active",
                "session_id": active_session.id
            }), 400
        
        # Initialise l'optimiseur global
        global optimizer
        optimizer = SetupOptimizer(
            car_id=params.car_id,
            track_id=params.track_id,
            optimization_params=params.params
        )
        
        # Démarre l'optimisation
        session_id = optimizer.start_optimization()
        
        if session_id is None:
            return jsonify({"error": "Erreur lors du démarrage de l'optimisation"}), 500
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Optimisation démarrée"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/optimization/stop', methods=['POST'])
def stop_optimization():
    """
    Endpoint pour arrêter l'optimisation en cours
    
    POST /api/v1/optimization/stop
    """
    try:
        global optimizer
        if optimizer is None:
            return jsonify({"error": "Aucune optimisation active"}), 400
        
        # Arrête l'optimisation
        success = optimizer.stop_optimization()
        
        if not success:
            return jsonify({"error": "Erreur lors de l'arrêt de l'optimisation"}), 500
        
        # Réinitialise l'optimiseur global
        optimizer = None
        
        return jsonify({
            "success": True,
            "message": "Optimisation arrêtée"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/optimization/status', methods=['GET'])
def get_optimization_status():
    """
    Endpoint pour récupérer le statut de l'optimisation
    
    GET /api/v1/optimization/status
    """
    try:
        # Récupère la session active
        active_session = OptimizationRepository.get_active_session()
        
        status = OptimizationStatus()
        
        if active_session:
            # Compte le nombre de setups testés et en attente
            db = SetupRepository.get_session()
            from src.models.setup import SetupConfiguration
            
            trials_completed = db.query(SetupConfiguration).filter(
                SetupConfiguration.optimization_session_id == active_session.id,
                SetupConfiguration.status == SETUP_STATUS["TESTED"]
            ).count()
            
            trials_pending = db.query(SetupConfiguration).filter(
                SetupConfiguration.optimization_session_id == active_session.id,
                SetupConfiguration.status == SETUP_STATUS["PENDING"]
            ).count()
            
            db.close()
            
            # Récupère les meilleurs setups
            best_setups = SetupRepository.get_best_setups(
                car_id=active_session.car_id,
                track_id=active_session.track_id,
                limit=5
            )
            
            best_score = best_setups[0].score if best_setups else None
            
            # Construit la réponse
            status.session_id = active_session.id
            status.car_id = active_session.car_id
            status.track_id = active_session.track_id
            status.start_time = active_session.start_time
            status.trials_completed = trials_completed
            status.trials_pending = trials_pending
            status.best_score = best_score
            status.best_setup_id = active_session.best_setup_id
            status.is_active = True
        
        return jsonify(status.dict())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/history', methods=['GET'])
def get_history():
    """
    Endpoint pour récupérer l'historique des setups
    
    GET /api/v1/history?car_id=X&track_id=Y&page=1&page_size=10
    """
    try:
        car_id = request.args.get('car_id')
        track_id = request.args.get('track_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        if not car_id or not track_id:
            return jsonify({"error": "car_id et track_id sont requis"}), 400
        
        # Récupère les setups depuis la base de données
        db = SetupRepository.get_session()
        from src.models.setup import SetupConfiguration
        
        query = db.query(SetupConfiguration).filter(
            SetupConfiguration.car_id == car_id,
            SetupConfiguration.track_id == track_id
        ).order_by(SetupConfiguration.generation_time.desc())
        
        # Pagination
        total = query.count()
        setups = query.offset((page - 1) * page_size).limit(page_size).all()
        
        db.close()
        
        # Construit la réponse
        setup_list = [
            SetupResponse(
                id=setup.id,
                car_id=setup.car_id,
                track_id=setup.track_id,
                setup_parameters=setup.setup_parameters,
                generation_time=setup.generation_time,
                status=setup.status,
                source=setup.source,
                score=setup.score
            ).dict()
            for setup in setups
        ]
        
        return jsonify({
            "setups": setup_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

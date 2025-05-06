from flask import Blueprint, render_template, jsonify, request
from src.storage.repository import SetupRepository, OptimizationRepository
from src.models.setup import SetupConfiguration, TelemetryResult, OptimizationSession
from src.config.constants import SETUP_STATUS, SETUP_SOURCE
import json

# Création du Blueprint
web_bp = Blueprint('web', __name__, template_folder='templates', static_folder='static')

@web_bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@web_bp.route('/dashboard')
def dashboard():
    """Tableau de bord principal"""
    return render_template('dashboard.html')

@web_bp.route('/setup/<int:setup_id>')
def setup_details(setup_id):
    """Détails d'un setup spécifique"""
    return render_template('setup_details.html', setup_id=setup_id)

@web_bp.route('/api/web/optimization/status')
def get_optimization_status():
    """Obtient le statut de l'optimisation en cours"""
    active_session = OptimizationRepository.get_active_session()
    
    if active_session:
        # Compte le nombre de setups testés et en attente
        db = SetupRepository.get_session()
        
        trials_completed = db.query(SetupConfiguration).filter(
            SetupConfiguration.optimization_session_id == active_session.id,
            SetupConfiguration.status == SETUP_STATUS["TESTED"]
        ).count()
        
        trials_pending = db.query(SetupConfiguration).filter(
            SetupConfiguration.optimization_session_id == active_session.id,
            SetupConfiguration.status == SETUP_STATUS["PENDING"]
        ).count()
        
        # Récupère les meilleurs setups
        best_setups = SetupRepository.get_best_setups(
            car_id=active_session.car_id,
            track_id=active_session.track_id,
            limit=5
        )
        
        best_score = best_setups[0].score if best_setups else None
        
        db.close()
        
        return jsonify({
            "is_active": True,
            "session_id": active_session.id,
            "car_id": active_session.car_id,
            "track_id": active_session.track_id,
            "start_time": active_session.start_time.isoformat(),
            "trials_completed": trials_completed,
            "trials_pending": trials_pending,
            "best_score": best_score,
            "best_setup_id": active_session.best_setup_id
        })
    else:
        return jsonify({
            "is_active": False
        })

@web_bp.route('/api/web/setups')
def get_setups():
    """Obtient la liste des setups pour une voiture et un circuit"""
    car_id = request.args.get('car_id')
    track_id = request.args.get('track_id')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    if not car_id or not track_id:
        return jsonify({"error": "car_id et track_id sont requis"}), 400
    
    # Récupère les setups depuis la base de données
    db = SetupRepository.get_session()
    
    query = db.query(SetupConfiguration).filter(
        SetupConfiguration.car_id == car_id,
        SetupConfiguration.track_id == track_id
    ).order_by(SetupConfiguration.generation_time.desc())
    
    # Pagination
    total = query.count()
    setups = query.offset((page - 1) * page_size).limit(page_size).all()
    
    db.close()
    
    # Construit la réponse
    setup_list = []
    for setup in setups:
        setup_dict = {
            "id": setup.id,
            "car_id": setup.car_id,
            "track_id": setup.track_id,
            "setup_parameters": setup.setup_parameters,
            "generation_time": setup.generation_time.isoformat(),
            "status": setup.status,
            "source": setup.source,
            "score": setup.score
        }
        setup_list.append(setup_dict)
    
    return jsonify({
        "setups": setup_list,
        "total": total,
        "page": page,
        "page_size": page_size
    })

@web_bp.route('/api/web/setup/<int:setup_id>')
def get_setup(setup_id):
    """Obtient les détails d'un setup spécifique"""
    setup = SetupRepository.get_setup_by_id(setup_id)
    
    if not setup:
        return jsonify({"error": "Setup non trouvé"}), 404
    
    # Récupère les résultats de télémétrie associés
    db = SetupRepository.get_session()
    telemetry_results = db.query(TelemetryResult).filter(
        TelemetryResult.setup_id == setup_id
    ).all()
    
    telemetry_list = []
    for result in telemetry_results:
        telemetry_dict = {
            "id": result.id,
            "lap_time": result.lap_time,
            "telemetry_data": result.telemetry_data,
            "submission_time": result.submission_time.isoformat(),
            "weather_conditions": result.weather_conditions,
            "driver_notes": result.driver_notes
        }
        telemetry_list.append(telemetry_dict)
    
    db.close()
    
    # Construit la réponse
    setup_dict = {
        "id": setup.id,
        "car_id": setup.car_id,
        "track_id": setup.track_id,
        "setup_parameters": setup.setup_parameters,
        "generation_time": setup.generation_time.isoformat(),
        "status": setup.status,
        "source": setup.source,
        "score": setup.score,
        "telemetry_results": telemetry_list
    }
    
    return jsonify(setup_dict)

@web_bp.route('/api/web/cars')
def get_cars():
    """Obtient la liste des voitures disponibles"""
    db = SetupRepository.get_session()
    
    # Récupère les voitures uniques
    cars = db.query(SetupConfiguration.car_id).distinct().all()
    car_list = [car[0] for car in cars]
    
    db.close()
    
    return jsonify(car_list)

@web_bp.route('/api/web/tracks')
def get_tracks():
    """Obtient la liste des circuits disponibles pour une voiture"""
    car_id = request.args.get('car_id')
    
    if not car_id:
        return jsonify({"error": "car_id est requis"}), 400
    
    db = SetupRepository.get_session()
    
    # Récupère les circuits uniques pour cette voiture
    tracks = db.query(SetupConfiguration.track_id).filter(
        SetupConfiguration.car_id == car_id
    ).distinct().all()
    
    track_list = [track[0] for track in tracks]
    
    db.close()
    
    return jsonify(track_list)

@web_bp.route('/api/web/performance')
def get_performance_data():
    """Obtient les données de performance pour les graphiques"""
    car_id = request.args.get('car_id')
    track_id = request.args.get('track_id')
    
    if not car_id or not track_id:
        return jsonify({"error": "car_id et track_id sont requis"}), 400
    
    db = SetupRepository.get_session()
    
    # Récupère les setups testés
    setups = db.query(SetupConfiguration).filter(
        SetupConfiguration.car_id == car_id,
        SetupConfiguration.track_id == track_id,
        SetupConfiguration.status == SETUP_STATUS["TESTED"],
        SetupConfiguration.score.isnot(None)
    ).order_by(SetupConfiguration.generation_time).all()
    
    # Prépare les données pour les graphiques
    lap_times = []
    scores = []
    setup_ids = []
    
    for setup in setups:
        # Récupère le temps au tour associé
        telemetry = db.query(TelemetryResult).filter(
            TelemetryResult.setup_id == setup.id
        ).first()
        
        if telemetry:
            lap_times.append(telemetry.lap_time)
            scores.append(setup.score)
            setup_ids.append(setup.id)
    
    db.close()
    
    return jsonify({
        "setup_ids": setup_ids,
        "lap_times": lap_times,
        "scores": scores
    })

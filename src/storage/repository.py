from sqlalchemy.exc import SQLAlchemyError
from src.models.setup import SetupConfiguration, TelemetryResult, OptimizationSession
from src.storage.database import get_session
from src.config.constants import SETUP_STATUS
import logging

logger = logging.getLogger(__name__)

class SetupRepository:
    @staticmethod
    def create_setup(car_id, track_id, setup_parameters, status, source, optimization_session_id=None):
        """Crée un nouveau setup dans la base de données"""
        db = get_session()
        try:
            setup = SetupConfiguration(
                car_id=car_id,
                track_id=track_id,
                setup_parameters=setup_parameters,
                status=status,
                source=source,
                optimization_session_id=optimization_session_id
            )
            db.add(setup)
            db.commit()
            return setup.id
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de la création du setup: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_setup_by_id(setup_id):
        """Récupère un setup par son ID"""
        db = get_session()
        try:
            return db.query(SetupConfiguration).filter(SetupConfiguration.id == setup_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération du setup: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_setup_status(setup_id, status, score=None):
        """Met à jour le statut et le score d'un setup"""
        db = get_session()
        try:
            setup = db.query(SetupConfiguration).filter(SetupConfiguration.id == setup_id).first()
            if setup:
                setup.status = status
                if score is not None:
                    setup.score = score
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de la mise à jour du setup: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_pending_setup():
        """Récupère le prochain setup en attente de test"""
        db = get_session()
        try:
            return db.query(SetupConfiguration)\
                .filter(SetupConfiguration.status == SETUP_STATUS["PENDING"])\
                .order_by(SetupConfiguration.generation_time)\
                .first()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération du setup en attente: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_best_setups(car_id, track_id, limit=5):
        """Récupère les meilleurs setups pour une voiture et une piste données"""
        db = get_session()
        try:
            return db.query(SetupConfiguration)\
                .filter(SetupConfiguration.car_id == car_id,
                        SetupConfiguration.track_id == track_id,
                        SetupConfiguration.status == SETUP_STATUS["TESTED"],
                        SetupConfiguration.score.isnot(None))\
                .order_by(SetupConfiguration.score.desc())\
                .limit(limit)\
                .all()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération des meilleurs setups: {str(e)}")
            return []
        finally:
            db.close()


class TelemetryRepository:
    @staticmethod
    def save_telemetry(setup_id, lap_time, telemetry_data, weather_conditions=None, driver_notes=None):
        """Enregistre les données de télémétrie pour un setup"""
        db = get_session()
        try:
            telemetry = TelemetryResult(
                setup_id=setup_id,
                lap_time=lap_time,
                telemetry_data=telemetry_data,
                weather_conditions=weather_conditions,
                driver_notes=driver_notes
            )
            db.add(telemetry)
            db.commit()
            return telemetry.id
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de l'enregistrement de la télémétrie: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_telemetry_for_setup(setup_id):
        """Récupère la télémétrie pour un setup donné"""
        db = get_session()
        try:
            return db.query(TelemetryResult).filter(TelemetryResult.setup_id == setup_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération de la télémétrie: {str(e)}")
            return []
        finally:
            db.close()


class OptimizationRepository:
    @staticmethod
    def create_session(car_id, track_id, optimization_parameters):
        """Crée une nouvelle session d'optimisation"""
        db = get_session()
        try:
            session = OptimizationSession(
                car_id=car_id,
                track_id=track_id,
                optimization_parameters=optimization_parameters
            )
            db.add(session)
            db.commit()
            return session.id
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de la création de la session d'optimisation: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_best_setup(session_id, best_setup_id):
        """Met à jour le meilleur setup pour une session d'optimisation"""
        db = get_session()
        try:
            session = db.query(OptimizationSession).filter(OptimizationSession.id == session_id).first()
            if session:
                session.best_setup_id = best_setup_id
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de la mise à jour du meilleur setup: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def close_session(session_id):
        """Ferme une session d'optimisation"""
        db = get_session()
        try:
            from datetime import datetime
            session = db.query(OptimizationSession).filter(OptimizationSession.id == session_id).first()
            if session:
                session.end_time = datetime.utcnow()
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erreur lors de la fermeture de la session: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_active_session():
        """Récupère la session d'optimisation active (si elle existe)"""
        db = get_session()
        try:
            return db.query(OptimizationSession)\
                .filter(OptimizationSession.end_time.is_(None))\
                .order_by(OptimizationSession.start_time.desc())\
                .first()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération de la session active: {str(e)}")
            return None
        finally:
            db.close()

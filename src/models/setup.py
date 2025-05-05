from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SetupConfiguration(Base):
    __tablename__ = "setup_configurations"
    
    id = Column(Integer, primary_key=True)
    car_id = Column(String, nullable=False)
    track_id = Column(String, nullable=False)
    setup_parameters = Column(JSON, nullable=False)
    generation_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
    source = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    optimization_session_id = Column(Integer, ForeignKey('optimization_sessions.id'))
    
    telemetry_results = relationship("TelemetryResult", back_populates="setup")
    optimization_session = relationship("OptimizationSession", back_populates="setups")
    
    def to_dict(self):
        return {
            "id": self.id,
            "car_id": self.car_id,
            "track_id": self.track_id,
            "setup_parameters": self.setup_parameters,
            "generation_time": self.generation_time.isoformat(),
            "status": self.status,
            "source": self.source,
            "score": self.score
        }
    
    def to_iracing_format(self):
        """Convertit le setup en format compatible avec iRacing"""
        # Cette fonction devrait transformer les paramètres internes
        # en format attendu par iRacing (format .json spécifique)
        # La structure exacte dépend des attentes d'iRacing
        return {
            "car": self.car_id,
            "track": self.track_id,
            "settings": self.setup_parameters,
            "generated": self.generation_time.isoformat(),
            "version": "1.0"
        }


class TelemetryResult(Base):
    __tablename__ = "telemetry_results"
    
    id = Column(Integer, primary_key=True)
    setup_id = Column(Integer, ForeignKey('setup_configurations.id'))
    lap_time = Column(Float, nullable=False)  # en secondes
    telemetry_data = Column(JSON, nullable=False)
    submission_time = Column(DateTime, default=datetime.utcnow)
    weather_conditions = Column(JSON, nullable=True)
    driver_notes = Column(String, nullable=True)
    
    setup = relationship("SetupConfiguration", back_populates="telemetry_results")
    
    def to_dict(self):
        return {
            "id": self.id,
            "setup_id": self.setup_id,
            "lap_time": self.lap_time,
            "telemetry_data": self.telemetry_data,
            "submission_time": self.submission_time.isoformat(),
            "weather_conditions": self.weather_conditions,
            "driver_notes": self.driver_notes
        }


class OptimizationSession(Base):
    __tablename__ = "optimization_sessions"
    
    id = Column(Integer, primary_key=True)
    car_id = Column(String, nullable=False)
    track_id = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    optimization_parameters = Column(JSON, nullable=False)
    best_setup_id = Column(Integer, ForeignKey('setup_configurations.id'), nullable=True)
    
    setups = relationship("SetupConfiguration", back_populates="optimization_session", 
                          foreign_keys=[SetupConfiguration.optimization_session_id])
    best_setup = relationship("SetupConfiguration", foreign_keys=[best_setup_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "car_id": self.car_id,
            "track_id": self.track_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "optimization_parameters": self.optimization_parameters,
            "best_setup_id": self.best_setup_id
        }

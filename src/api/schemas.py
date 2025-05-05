from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class TelemetryData(BaseModel):
    """Schéma pour les données de télémétrie"""
    setup_id: int
    lap_time: float
    telemetry_data: Dict[str, Union[float, int, str, Dict]]
    weather_conditions: Optional[Dict[str, Any]] = None
    driver_notes: Optional[str] = None

class OptimizationParameters(BaseModel):
    """Schéma pour les paramètres d'optimisation"""
    car_id: str
    track_id: str
    params: Optional[Dict[str, Any]] = None

class SetupResponse(BaseModel):
    """Schéma pour la réponse contenant un setup"""
    id: int
    car_id: str
    track_id: str
    setup_parameters: Dict[str, Any]
    generation_time: datetime
    status: str
    source: str
    score: Optional[float] = None
    file_path: Optional[str] = None

class OptimizationStatus(BaseModel):
    """Schéma pour le statut d'une optimisation"""
    session_id: Optional[int] = None
    car_id: Optional[str] = None
    track_id: Optional[str] = None
    start_time: Optional[datetime] = None
    trials_completed: int = 0
    trials_pending: int = 0
    best_score: Optional[float] = None
    best_setup_id: Optional[int] = None
    is_active: bool = False

class HistoryResponse(BaseModel):
    """Schéma pour l'historique des setups"""
    setups: List[SetupResponse]
    total: int
    page: int
    page_size: int

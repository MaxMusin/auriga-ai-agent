import json
import os
from pathlib import Path
from src.config.settings import SETUPS_DIR
from src.storage.repository import SetupRepository

class SetupGenerator:
    """Classe responsable de la génération de fichiers de setup au format iRacing"""
    
    @staticmethod
    def generate_setup_file(setup_id):
        """
        Génère un fichier de setup JSON au format iRacing
        
        Args:
            setup_id (int): ID du setup à générer
            
        Returns:
            str: Chemin du fichier généré ou None si erreur
        """
        # Récupère le setup depuis la base de données
        setup = SetupRepository.get_setup_by_id(setup_id)
        
        if setup is None:
            return None
        
        # Convertit le setup au format iRacing
        iracing_setup = setup.to_iracing_format()
        
        # Crée le répertoire spécifique pour cette voiture et ce circuit si nécessaire
        car_track_dir = SETUPS_DIR / setup.car_id / setup.track_id
        car_track_dir.mkdir(parents=True, exist_ok=True)
        
        # Génère un nom de fichier unique basé sur l'ID et la date
        filename = f"setup_{setup.id}_{setup.generation_time.strftime('%Y%m%d_%H%M%S')}.json"
        setup_path = car_track_dir / filename
        
        # Écrit le fichier
        with open(setup_path, 'w') as f:
            json.dump(iracing_setup, f, indent=2)
        
        return str(setup_path)
    
    @staticmethod
    def get_latest_setup(car_id, track_id):
        """
        Récupère le chemin du dernier fichier de setup généré pour une voiture et un circuit
        
        Args:
            car_id (str): ID de la voiture
            track_id (str): ID du circuit
            
        Returns:
            str: Chemin du dernier fichier de setup ou None si aucun trouvé
        """
        # Chemin du répertoire contenant les setups pour cette voiture et ce circuit
        car_track_dir = SETUPS_DIR / car_id / track_id
        
        if not car_track_dir.exists():
            return None
        
        # Liste tous les fichiers de setup et trie par date de modification (dernier en premier)
        setup_files = sorted(
            car_track_dir.glob("setup_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not setup_files:
            return None
        
        return str(setup_files[0])

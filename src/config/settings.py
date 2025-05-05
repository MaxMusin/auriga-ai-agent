import os
from pathlib import Path
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SETUPS_DIR = DATA_DIR / "setups"
HISTORY_DIR = DATA_DIR / "history"

# Création des répertoires s'ils n'existent pas
for dir_path in [DATA_DIR, SETUPS_DIR, HISTORY_DIR]:
    dir_path.mkdir(exist_ok=True)

# Configuration de l'API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Configuration de la base de données
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/optimization.db")

# Configuration de l'optimisation
DEFAULT_OPTIMIZATION_ITERATIONS = int(os.getenv("DEFAULT_OPTIMIZATION_ITERATIONS", 50))
OPTIMIZATION_TIMEOUT = int(os.getenv("OPTIMIZATION_TIMEOUT", 3600))  # 1 heure

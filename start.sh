#!/bin/bash

# Activation de l'environnement virtuel
source venv/bin/activate

# Définition des variables d'environnement
export API_PORT=8080
export API_HOST=0.0.0.0
export DEBUG_MODE=True

# Démarrage de l'application
python3 -m src.app

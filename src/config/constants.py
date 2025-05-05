# Limites des paramètres de setup pour différentes voitures
# Ces valeurs sont fictives, à ajuster selon les spécifications réelles des voitures dans iRacing
CAR_SETUP_PARAMETERS = {
    "mx5": {  # Mazda MX-5
        "front_tire_pressure": {"min": 20.0, "max": 32.0, "step": 0.5, "unit": "psi"},
        "rear_tire_pressure": {"min": 20.0, "max": 32.0, "step": 0.5, "unit": "psi"},
        "front_camber": {"min": -5.0, "max": -0.5, "step": 0.1, "unit": "deg"},
        "rear_camber": {"min": -5.0, "max": -0.5, "step": 0.1, "unit": "deg"},
        "front_toe": {"min": -0.5, "max": 0.5, "step": 0.01, "unit": "deg"},
        "rear_toe": {"min": -0.5, "max": 0.5, "step": 0.01, "unit": "deg"},
        "front_arb": {"min": 1, "max": 6, "step": 1, "unit": "position"},
        "rear_arb": {"min": 1, "max": 6, "step": 1, "unit": "position"},
    },
    "f3": {  # Formula 3
        "front_wing": {"min": 1, "max": 40, "step": 1, "unit": "position"},
        "rear_wing": {"min": 1, "max": 40, "step": 1, "unit": "position"},
        "front_tire_pressure": {"min": 17.0, "max": 25.0, "step": 0.1, "unit": "psi"},
        "rear_tire_pressure": {"min": 17.0, "max": 25.0, "step": 0.1, "unit": "psi"},
        "front_camber": {"min": -5.0, "max": -1.0, "step": 0.1, "unit": "deg"},
        "rear_camber": {"min": -5.0, "max": -1.0, "step": 0.1, "unit": "deg"},
        # ... autres paramètres spécifiques à F3
    },
    # ... autres voitures
}

# Métriques utilisées pour l'évaluation des performances
PERFORMANCE_METRICS = [
    "lap_time",               # Temps au tour (secondes)
    "tire_avg_temp_fl",       # Température moyenne du pneu avant gauche (°C)
    "tire_avg_temp_fr",       # Température moyenne du pneu avant droit (°C)
    "tire_avg_temp_rl",       # Température moyenne du pneu arrière gauche (°C)
    "tire_avg_temp_rr",       # Température moyenne du pneu arrière droit (°C)
    "tire_wear_fl",           # Usure du pneu avant gauche (%)
    "tire_wear_fr",           # Usure du pneu avant droit (%)
    "tire_wear_rl",           # Usure du pneu arrière gauche (%)
    "tire_wear_rr",           # Usure du pneu arrière droit (%)
    "car_stability",          # Stabilité de la voiture (1-10)
    "corner_entry_stability", # Stabilité à l'entrée des virages (1-10)
    "corner_exit_stability",  # Stabilité à la sortie des virages (1-10)
    "traction",               # Traction (1-10)
    "braking_stability",      # Stabilité au freinage (1-10)
]

# Définition des statuts pour les setups
SETUP_STATUS = {
    "PENDING": "pending",     # En attente de test
    "TESTED": "tested",       # Testé avec résultats
    "DISCARDED": "discarded"  # Écarté (non testé ou problématique)
}

# Sources des setups
SETUP_SOURCE = {
    "INITIAL": "initial",     # Setup initial
    "OPTIMIZED": "optimized", # Généré par l'optimiseur
    "MANUAL": "manual"        # Créé manuellement par l'utilisateur
}

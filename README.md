# Auriga AI Agent - Optimisation de Setup iRacing

## Description

Auriga AI Agent est un système d'optimisation automatique des réglages de voiture pour iRacing. Il utilise des techniques d'optimisation bayésienne pour suggérer les meilleurs setups en fonction des données de télémétrie collectées après chaque test.

## Fonctionnalités

- Réception des données de télémétrie via une API HTTP
- Évaluation des performances de chaque setup testé
- Optimisation intelligente des paramètres de setup avec Optuna
- Stockage de l'historique des setups et de leurs performances
- Génération de fichiers de setup au format compatible avec iRacing

## Architecture

```
[iRacing + SimHub (Windows)] <---> [Backend IA (Serveur Linux)]
       |                                |
       v                                v
[Plugin SimHub]                  [API Flask + Optimiseur]
       |                                |
       v                                v
[Envoi données HTTP POST] ---> [Stockage + Optimisation]
                                        |
                                        v
                                [Génération setup.json]
```

## Prérequis

- Python 3.8+
- Base de données SQLite (incluse)
- Plugin SimHub pour l'envoi des données de télémétrie (à développer séparément)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-username/auriga-ai-agent.git
cd auriga-ai-agent
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sous Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer l'environnement :
```bash
cp .env.example .env
# Modifier les paramètres dans .env si nécessaire
```

## Utilisation

### Démarrer le serveur

```bash
python -m src.app
```

Le serveur sera accessible à l'adresse http://localhost:5000.

### Endpoints API

- `POST /api/v1/telemetry` : Recevoir les données de télémétrie
- `GET /api/v1/setup/next` : Obtenir le prochain setup à tester
- `GET /api/v1/setup/current?id=X` : Obtenir les détails d'un setup spécifique
- `POST /api/v1/optimization/start` : Démarrer une nouvelle session d'optimisation
- `POST /api/v1/optimization/stop` : Arrêter l'optimisation en cours
- `GET /api/v1/optimization/status` : Obtenir le statut de l'optimisation
- `GET /api/v1/history` : Consulter l'historique des setups

### Exemple d'utilisation

1. Démarrer une session d'optimisation :
```bash
curl -X POST http://localhost:5000/api/v1/optimization/start \
  -H "Content-Type: application/json" \
  -d '{"car_id": "mx5", "track_id": "spa", "params": {"n_trials": 30, "sampler": "tpe"}}'
```

2. Récupérer le prochain setup à tester :
```bash
curl -X GET http://localhost:5000/api/v1/setup/next
```

3. Envoyer les résultats de télémétrie après un test :
```bash
curl -X POST http://localhost:5000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "setup_id": 1,
    "lap_time": 120.456,
    "telemetry_data": {
      "tire_avg_temp_fl": 85.2,
      "tire_avg_temp_fr": 87.1,
      "tire_avg_temp_rl": 83.5,
      "tire_avg_temp_rr": 84.8,
      "tire_wear_fl": 0.5,
      "tire_wear_fr": 0.7,
      "tire_wear_rl": 0.4,
      "tire_wear_rr": 0.6,
      "car_stability": 7.5,
      "corner_entry_stability": 8.0,
      "corner_exit_stability": 7.0,
      "traction": 8.5,
      "braking_stability": 7.8
    },
    "weather_conditions": {
      "track_temp": 28.5,
      "air_temp": 22.3,
      "humidity": 65,
      "wind_speed": 3.2,
      "wind_direction": 180
    },
    "driver_notes": "Sous-virage en entrée de virage 5, survirage en sortie de virage 10"
  }'
```

## Configuration du plugin SimHub

Pour que le système fonctionne, vous devez développer un plugin SimHub qui envoie les données de télémétrie après chaque test. Le plugin doit :

1. Collecter les données de télémétrie pertinentes (temps au tour, températures des pneus, etc.)
2. Formater ces données au format JSON attendu par l'API
3. Envoyer les données via une requête HTTP POST à l'endpoint `/api/v1/telemetry`

## Personnalisation

### Ajouter une nouvelle voiture

Pour ajouter une nouvelle voiture, modifiez le fichier `src/config/constants.py` et ajoutez les paramètres de setup spécifiques à cette voiture dans le dictionnaire `CAR_SETUP_PARAMETERS`.

### Modifier les métriques d'évaluation

Les métriques utilisées pour évaluer les performances d'un setup sont définies dans le fichier `src/config/constants.py` dans la liste `PERFORMANCE_METRICS`. Vous pouvez ajouter, supprimer ou modifier ces métriques selon vos besoins.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

FROM python:3.10-slim

WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste de l'application
COPY . .

# Création des répertoires de données
RUN mkdir -p data/setups data/history

# Exposition du port
EXPOSE 5000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:create_app()"]

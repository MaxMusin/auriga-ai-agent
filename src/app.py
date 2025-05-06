from flask import Flask
from flask_cors import CORS
import logging
from datetime import datetime
from src.api.routes import api_bp
from src.web.routes import web_bp
from src.storage.database import init_db
from src.config.settings import API_HOST, API_PORT, DEBUG_MODE

def create_app():
    """Crée et configure l'application Flask"""
    # Initialisation de l'application
    app = Flask(__name__)
    
    # Configuration du logging
    if DEBUG_MODE:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Active CORS pour permettre les requêtes cross-origin
    CORS(app)
    
    # Initialise la base de données
    with app.app_context():
        init_db()
    
    # Ajoute la date actuelle au contexte des templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Enregistre les blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    
    # Route de test pour vérifier que l'API est en ligne
    @app.route('/health', methods=['GET'])
    def health_check():
        return {"status": "ok", "version": "1.0"}
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)

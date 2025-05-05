from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from src.config.settings import DB_URL
from src.models.setup import Base

# Création du moteur de base de données
engine = create_engine(DB_URL)

# Création de la session
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Création des tables si elles n'existent pas
def init_db():
    Base.metadata.create_all(engine)

def get_session():
    """Renvoie une session de base de données"""
    db = Session()
    try:
        return db
    finally:
        db.close()

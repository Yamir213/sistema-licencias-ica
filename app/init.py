# Este archivo hace que Python reconozca 'app' como un paquete
from .database.connection import Base, engine, SessionLocal, get_db
from .config import settings

__all__ = [
    "Base",
    "engine", 
    "SessionLocal",
    "get_db",
    "settings"
]

__version__ = "1.0.0"
__author__ = "Municipalidad Provincial de Ica"
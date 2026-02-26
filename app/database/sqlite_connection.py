from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Crear carpeta para la base de datos
os.makedirs("app/database/data", exist_ok=True)

# URL de SQLite - el archivo se creará automáticamente
SQLITE_URL = "sqlite:///./app/database/data/licencias_ica.db"

print("=" * 60)
print("🗄️  CONECTANDO A SQLITE")
print("=" * 60)
print(f"📁 Base de datos: {SQLITE_URL}")
print("=" * 60)

# Crear motor de SQLite
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},  # Necesario para desarrollo
    echo=False  # Cambia a True si quieres ver las consultas SQL
)

# Crear sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
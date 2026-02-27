from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Obtener la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/database/data/licencias_ica.db")

# Configuración para PostgreSQL (SSL requerido por Render)
connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Para PostgreSQL, necesitamos SSL
    connect_args = {"sslmode": "require"}
    print("📦 Conectando a PostgreSQL en Render")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
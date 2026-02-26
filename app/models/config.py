from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base

class Rubro(Base):
    """Rubros comerciales - Versión SQLite"""
    
    __tablename__ = "rubros"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    nivel_riesgo = Column(String(20), nullable=False)  # bajo, medio, alto, muy_alto
    requiere_itse_previa = Column(Boolean, default=False)
    requiere_defensa_civil = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Tarifa(Base):
    """Tarifas por nivel de riesgo"""
    
    __tablename__ = "tarifas"
    
    id = Column(Integer, primary_key=True, index=True)
    nivel_riesgo = Column(String(20), unique=True, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=True)
    vigente_desde = Column(DateTime, nullable=False)
    vigente_hasta = Column(DateTime, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class Zona(Base):
    """Zonificación urbana"""
    
    __tablename__ = "zonas"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
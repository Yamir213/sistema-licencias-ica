from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

class EstadoInspeccion(str, enum.Enum):
    PROGRAMADA = "programada"
    EN_CURSO = "en_curso"
    REALIZADA = "realizada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"

class Inspeccion(Base):
    """Modelo para programación y realización de inspecciones ITSE"""
    
    __tablename__ = "inspecciones"
    
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False)
    solicitud = relationship("Solicitud", foreign_keys=[solicitud_id])
    
    inspector_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    inspector = relationship("User", foreign_keys=[inspector_id])
    
    # Fechas
    fecha_programada = Column(DateTime, nullable=False)
    fecha_realizada = Column(DateTime, nullable=True)
    
    # Estado y resultado
    estado = Column(String(50), default=EstadoInspeccion.PROGRAMADA.value)
    resultado = Column(String(50), nullable=True)  # aprobado, observado, rechazado
    
    # Datos de la inspección
    observaciones = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)
    
    # Checklist de seguridad
    extintores = Column(Boolean, default=False)
    luces_emergencia = Column(Boolean, default=False)
    señalizacion = Column(Boolean, default=False)
    sistema_electrico = Column(Boolean, default=False)
    via_evacuacion = Column(Boolean, default=False)
    
    # Documentos
    fotos_antes = Column(Text, nullable=True)  # JSON con rutas de fotos
    fotos_despues = Column(Text, nullable=True)
    informe_pdf = Column(String(500), nullable=True)
    
    # Fechas de control
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    fecha_vencimiento = Column(DateTime, nullable=True)  # Para cuando aprueba
    
    def __repr__(self):
        return f"<Inspeccion {self.id} - Solicitud {self.solicitud_id}>"
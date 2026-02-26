from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

class TipoNotificacion(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"

class EstadoNotificacion(str, enum.Enum):
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    FALLIDO = "fallido"
    LEIDO = "leido"

class Notificacion(Base):
    """Registro de notificaciones enviadas"""
    
    __tablename__ = "notificaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Destinatario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    destinatario = Column(String(255), nullable=False)  # email o teléfono
    tipo = Column(Enum(TipoNotificacion), nullable=False)
    
    # Contenido
    asunto = Column(String(255), nullable=True)
    mensaje = Column(Text, nullable=False)
    plantilla = Column(String(100), nullable=True)
    
    # Estado
    estado = Column(Enum(EstadoNotificacion), default=EstadoNotificacion.PENDIENTE)
    fecha_envio = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    
    # Relación con solicitud (opcional)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Notificacion {self.tipo}: {self.destinatario}>"
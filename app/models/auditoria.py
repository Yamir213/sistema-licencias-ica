from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    tipo_accion = Column(String(50), nullable=False)
    entidad = Column(String(100), nullable=False)
    entidad_id = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=False)
    
    # 👇 RELACIONES CORREGIDAS
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=True)
    solicitud = relationship("Solicitud", back_populates="auditorias")
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("User", foreign_keys=[usuario_id])
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
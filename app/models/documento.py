from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Documento(Base):
    __tablename__ = "documentos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False)
    
    # 👇 RELACIÓN CORREGIDA
    solicitud = relationship("Solicitud", back_populates="documentos")
    
    tipo = Column(String(50), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    ruta_archivo = Column(String(500), nullable=False)
    nombre_original = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    tamaño_bytes = Column(Integer, nullable=False)
    
    es_obligatorio = Column(Boolean, default=True)
    esta_validado = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)
    validado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_validacion = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
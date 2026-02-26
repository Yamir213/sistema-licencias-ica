from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    REEMBOLSADO = "reembolsado"

class MetodoPago(str, enum.Enum):
    CULQI = "culqi"
    NIU_BIZ = "niubiz"
    PAGO_EFECTIVO = "pago_efectivo"
    TRANSFERENCIA = "transferencia"
    YAPE = "yape"
    PLIN = "plin"

class Pago(Base):
    """Modelo de pagos - VERSIÓN CORREGIDA"""
    
    __tablename__ = "pagos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False)
    
    # 👇 RELACIÓN CORREGIDA - back_populates debe coincidir con Solicitud.pagos
    solicitud = relationship("Solicitud", back_populates="pagos")
    
    # Información del pago
    codigo_pago = Column(String(50), unique=True, nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), default="PEN")
    metodo_pago = Column(String(50), nullable=False)
    estado = Column(String(50), default="pendiente")
    
    # Información de transacción
    codigo_transaccion = Column(String(100), nullable=True)
    fecha_transaccion = Column(DateTime, nullable=True)
    datos_transaccion = Column(JSON, nullable=True)
    
    # Comprobante
    comprobante_url = Column(String(500), nullable=True)
    comprobante_numero = Column(String(50), nullable=True)
    comprobante_pdf = Column(String(500), nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    def generar_numero_comprobante(self):
        """Genera número de comprobante automático"""
        from datetime import datetime
        fecha = datetime.now().strftime("%Y%m%d")
        return f"B{self.solicitud_id:06d}-{fecha}"
    
    def __repr__(self):
        return f"<Pago {self.codigo_pago} - {self.estado}>"
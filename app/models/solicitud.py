from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

class EstadoSolicitud(str, enum.Enum):
    """Estados posibles de una solicitud de licencia"""
    BORRADOR = "borrador"
    PENDIENTE_PAGO = "pendiente_pago"
    PAGADO = "pagado"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    REQUIERE_ITSE = "requiere_itse"
    PENDIENTE_ITSE = "pendiente_itse"
    ITSE_APROBADO = "itse_aprobado"
    LICENCIA_EMITIDA = "licencia_emitida"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"

class Solicitud(Base):
    """Solicitudes de licencia de funcionamiento"""
    
    __tablename__ = "solicitudes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    numero_expediente = Column(String(50), unique=True, index=True)
    
    # Relaciones
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("User", foreign_keys=[usuario_id])
    
    rubro_id = Column(Integer, ForeignKey("rubros.id"), nullable=False)
    rubro = relationship("Rubro", foreign_keys=[rubro_id])
    
    zona_id = Column(Integer, ForeignKey("zonas.id"), nullable=True)
    zona = relationship("Zona", foreign_keys=[zona_id])
    
    # Relaciones con otros modelos
    pagos = relationship("Pago", back_populates="solicitud", cascade="all, delete-orphan")
    documentos = relationship("Documento", back_populates="solicitud", cascade="all, delete-orphan")
    auditorias = relationship("Auditoria", back_populates="solicitud", cascade="all, delete-orphan")
    
    # Información del negocio
    nombre_negocio = Column(String(200), nullable=False)
    direccion_negocio = Column(String(255), nullable=False)
    referencia = Column(String(255), nullable=True)
    distrito = Column(String(100), nullable=False, default="Ica")
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    area_local = Column(String(50), nullable=True)
    telefono_contacto = Column(String(20), nullable=True)
    
    # Clasificación y estado
    nivel_riesgo = Column(String(20), nullable=False)
    estado = Column(String(50), default=EstadoSolicitud.BORRADOR.value)  # Usamos el valor del enum
    
    # ITSE
    requiere_itse_previa = Column(Boolean, default=False)
    itse_aprobado = Column(Boolean, default=False)
    fecha_itse = Column(DateTime, nullable=True)
    numero_itse = Column(String(50), nullable=True)
    vencimiento_itse = Column(DateTime, nullable=True)
    
    # Zonificación
    compatible_zonificacion = Column(Boolean, default=True)
    observaciones_zonificacion = Column(Text, nullable=True)
    
    # Pago
    monto_pago = Column(Float, nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    comprobante_pago = Column(String(255), nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    
    # Licencia
    numero_licencia = Column(String(50), unique=True, nullable=True)
    fecha_emision = Column(DateTime, nullable=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    codigo_verificador = Column(String(20), nullable=True)
    licencia_pdf_url = Column(String(500), nullable=True)
    
    # Fiscalización
    fecha_ultima_inspeccion = Column(DateTime, nullable=True)
    proxima_inspeccion = Column(DateTime, nullable=True)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    fecha_presentacion = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Solicitud {self.numero_expediente or self.id}>"
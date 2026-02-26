from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class User(Base):
    """Modelo de usuarios - Versión SQLite"""
    
    __tablename__ = "usuarios"
    
    # ===== COLUMNAS BÁSICAS =====
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # ===== TIPOS (usamos String en lugar de Enum) =====
    tipo_usuario = Column(String(50), default="ciudadano")  # ciudadano, funcionario, administrador
    tipo_persona = Column(String(50), nullable=True)  # natural, juridica
    
    # ===== PERSONA NATURAL =====
    dni = Column(String(8), unique=True, nullable=True, index=True)
    nombres = Column(String(100), nullable=True)
    apellido_paterno = Column(String(50), nullable=True)
    apellido_materno = Column(String(50), nullable=True)
    fecha_nacimiento = Column(DateTime, nullable=True)
    
    # ===== PERSONA JURÍDICA =====
    ruc = Column(String(11), unique=True, nullable=True, index=True)
    razon_social = Column(String(200), nullable=True)
    nombre_comercial = Column(String(200), nullable=True)
    representante_legal = Column(String(150), nullable=True)
    
    # ===== DIRECCIÓN =====
    direccion = Column(String(255), nullable=True)
    distrito = Column(String(100), nullable=True)
    provincia = Column(String(100), nullable=True, default="Ica")
    departamento = Column(String(100), nullable=True, default="Ica")
    
    # ===== ESTADO =====
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(100), nullable=True)
    
    # ===== FUNCIONARIOS =====
    cargo = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    
    # ===== AUDITORÍA =====
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def nombre_completo(self):
        """Devuelve el nombre completo"""
        if self.tipo_persona == "natural":
            return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}".strip()
        elif self.tipo_persona == "juridica":
            return self.razon_social or self.nombre_comercial or ""
        return ""
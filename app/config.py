import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    # Configuración de la aplicación
    APP_NAME: str = "Sistema de Licencias - Municipalidad de Ica"
    APP_VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/licencias_ica")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "clave_secreta_para_desarrollo_cambiar_en_produccion")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@muniica.gob.pe")
    
    # Pagos
    CULQI_PUBLIC_KEY: str = os.getenv("CULQI_PUBLIC_KEY", "")
    CULQI_SECRET_KEY: str = os.getenv("CULQI_SECRET_KEY", "")
    
    # URLs
    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Archivos
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
    ALLOWED_EXTENSIONS: list = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png,doc,docx").split(",")
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    
    class Config:
        env_file = ".env"

# Instancia global de configuración
settings = Settings()
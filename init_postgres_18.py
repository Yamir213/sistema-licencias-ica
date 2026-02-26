import subprocess
import os

def setup_postgres_18():
    """Configurar PostgreSQL 18 para el proyecto"""
    
    print("=" * 60)
    print("CONFIGURACIÓN POSTGRESQL 18 - SISTEMA LICENCIAS ICA")
    print("=" * 60)
    
    # Configuración
    pg_path = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
    pg_user = "postgres"
    pg_pass = "postgres"  # Cambia si usaste otra
    pg_host = "localhost"
    pg_port = "5432"
    pg_db = "licencias_ica"
    
    print(f"\n📁 Ruta PostgreSQL: {pg_path}")
    print(f"👤 Usuario: {pg_user}")
    print(f"🔑 Contraseña: {pg_pass}")
    print(f"🌐 Host: {pg_host}:{pg_port}")
    print(f"🗄️  Base de datos: {pg_db}")
    
    # 1. Verificar conexión
    print("\n1️⃣  Verificando conexión a PostgreSQL 18...")
    cmd_test = f'"{pg_path}" -h {pg_host} -p {pg_port} -U {pg_user} -c "SELECT version();"'
    
    try:
        result = subprocess.run(cmd_test, shell=True, capture_output=True, text=True, input=f"{pg_pass}\n")
        
        if result.returncode == 0:
            print("✅ Conexión exitosa!")
            print(f"📄 Versión: {result.stdout.strip()}")
        else:
            print("❌ Error de conexión")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 2. Crear base de datos si no existe
    print("\n2️⃣  Creando base de datos...")
    cmd_create_db = f'"{pg_path}" -h {pg_host} -p {pg_port} -U {pg_user} -c "CREATE DATABASE {pg_db};"'
    
    try:
        result = subprocess.run(cmd_create_db, shell=True, capture_output=True, text=True, input=f"{pg_pass}\n")
        
        if result.returncode == 0:
            print("✅ Base de datos creada exitosamente")
        else:
            if "already exists" in result.stderr:
                print("ℹ️  La base de datos ya existe")
            else:
                print(f"⚠️  Error al crear base de datos: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # 3. Mostrar DATABASE_URL final
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    
    database_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    print(f"\n📋 COPIA ESTA LÍNEA en tu archivo .env:")
    print(f"\nDATABASE_URL={database_url}")
    
    print(f"\n📋 Configuración completa para .env:")
    print(f"""
DATABASE_URL={database_url}
SECRET_KEY=clave_super_secreta_ica_2024_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_app
EMAIL_FROM=noreply@muniica.gob.pe

APP_URL=http://localhost:8000
    """)
    
    # 4. Crear archivo .env automáticamente
    env_content = f"""# CONFIGURACIÓN POSTGRESQL 18
DATABASE_URL={database_url}

# SEGURIDAD
SECRET_KEY=clave_super_secreta_ica_2024_cambiar_en_produccion_12345abc
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# EMAIL
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_app
EMAIL_FROM=noreply@muniica.gob.pe

# PAGOS
CULQI_PUBLIC_KEY=pk_test_xxxx
CULQI_SECRET_KEY=sk_test_xxxx

# URLs
APP_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# ARCHIVOS
MAX_FILE_SIZE_MB=10
UPLOAD_FOLDER=app/static/uploads
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,doc,docx
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"\n✅ Archivo .env creado/actualizado")
    print(f"📁 Ubicación: {os.path.abspath('.env')}")
    
    return True

if __name__ == "__main__":
    setup_postgres_18()
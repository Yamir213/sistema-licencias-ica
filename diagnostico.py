import os
import sys
import psycopg2
from dotenv import load_dotenv

print("=" * 60)
print("🔍 DIAGNÓSTICO COMPLETO - SISTEMA LICENCIAS ICA")
print("=" * 60)

# 1. Verificar Python
print("\n1️⃣  VERSIÓN DE PYTHON:")
print(f"   Python: {sys.version}")
print(f"   Directorio: {os.getcwd()}")

# 2. Cargar .env
print("\n2️⃣  ARCHIVO .env:")
load_dotenv()
db_url = os.getenv("DATABASE_URL")
print(f"   DATABASE_URL: {db_url}")

# 3. Verificar PostgreSQL
print("\n3️⃣  VERIFICANDO POSTGRESQL 18:")
try:
    # Intentar conexión sin base de datos específica
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        database="postgres"  # Base de datos por defecto
    )
    print("   ✅ Conexión a PostgreSQL EXITOSA!")
    
    cur = conn.cursor()
    
    # Verificar versión
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"   📊 Versión: {version[0][:60]}...")
    
    # Verificar si la base de datos existe
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'licencias_ica'")
    exists = cur.fetchone()
    
    if exists:
        print("   ✅ Base de datos 'licencias_ica' EXISTE")
    else:
        print("   ❌ Base de datos 'licencias_ica' NO EXISTE")
        print("   🔧 Creando base de datos...")
        conn.autocommit = True
        cur.execute("CREATE DATABASE licencias_ica")
        print("   ✅ Base de datos 'licencias_ica' CREADA")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error conectando a PostgreSQL:")
    print(f"      {e}")
    print("\n   🔧 SOLUCIÓN RÁPIDA:")
    print("   1. Abre 'Servicios' (services.msc)")
    print("   2. Busca 'postgresql-x64-18'")
    print("   3. Click derecho -> Iniciar")
    print("   4. Espera 10 segundos y ejecuta este script otra vez")

# 4. Probar SQLAlchemy
print("\n4️⃣  VERIFICANDO SQLALCHEMY:")
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    
    # Usar la URL de tu .env
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("   ✅ SQLAlchemy conectó correctamente")
        
except Exception as e:
    print(f"   ❌ Error con SQLAlchemy:")
    print(f"      {e}")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
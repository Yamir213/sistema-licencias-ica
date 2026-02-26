import psycopg2
import os
import sys

print("=" * 60)
print("🔧 PRUEBA DE CONEXIÓN POSTGRESQL - CODIFICACIÓN FORZADA")
print("=" * 60)

# 1. Forzar codificación UTF-8 en Windows
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["LANG"] = "en_US.UTF-8"

print("\n1️⃣  Configuración:")
print(f"   📁 Directorio: {os.getcwd()}")
print(f"   🐍 Python: {sys.version}")
print(f"   🔤 Encoding forzado: UTF-8")

# 2. Intentar conexión con diferentes métodos
print("\n2️⃣  Probando conexiones...")

# Método 1: Sin base de datos específica
try:
    print("\n   📌 Método 1: Conectando a 'postgres'...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        database="postgres",
        client_encoding='UTF8'
    )
    print("   ✅ CONEXIÓN EXITOSA!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"   📊 PostgreSQL: {version[0][:80]}...")
    
    # Crear base de datos con UTF8
    print("\n   📌 Creando base de datos 'licencias_ica'...")
    conn.autocommit = True
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'licencias_ica'")
    exists = cur.fetchone()
    
    if not exists:
        cur.execute("CREATE DATABASE licencias_ica ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C';")
        print("   ✅ Base de datos 'licencias_ica' CREADA con UTF8")
    else:
        print("   ✅ Base de datos 'licencias_ica' YA EXISTE")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Método 2: Conectar directamente a licencias_ica
try:
    print("\n   📌 Método 2: Conectando a 'licencias_ica'...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        database="licencias_ica",
        client_encoding='UTF8',
        options='-c client_encoding=UTF8'
    )
    print("   ✅ CONEXIÓN EXITOSA!")
    
    cur = conn.cursor()
    cur.execute("SELECT current_database();")
    db_name = cur.fetchone()
    print(f"   📊 Conectado a: {db_name[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Método 3: Usando URL
try:
    print("\n   📌 Método 3: Usando DATABASE_URL...")
    from sqlalchemy import create_engine, text
    
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/licencias_ica"
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            'client_encoding': 'UTF8',
            'options': '-c client_encoding=UTF8'
        }
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print("   ✅ SQLAlchemy CONECTÓ!")
        print(f"   📊 {version[:80]}...")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Método 4: Sin especificar base de datos
try:
    print("\n   📌 Método 4: Sin especificar base de datos...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="postgres",
        client_encoding='UTF8'
    )
    print("   ✅ CONEXIÓN EXITOSA!")
    
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = cur.fetchall()
    print("   📊 Bases de datos disponibles:")
    for db in databases:
        print(f"      • {db[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)

# Instrucciones según resultado
print("\n📋 INSTRUCCIONES:")
print("-" * 40)
print("Si NINGUNA conexión funcionó:")
print("1. Ve a: Services.msc")
print("2. Busca 'postgresql-x64-18'")
print("3. Click derecho → Iniciar")
print("4. Espera 10 segundos")
print("5. Ejecuta este script otra vez")
print("\nSi ALGUNA conexión funcionó:")
print("1. Tu PostgreSQL está bien configurado")
print("2. El problema es solo de codificación")
print("3. Usa la configuración que funcionó")
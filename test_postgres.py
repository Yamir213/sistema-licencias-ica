import sys
import subprocess

print("=" * 60)
print("🐘 PRUEBA DE CONEXIÓN POSTGRESQL")
print("=" * 60)

# 1. Verificar si psycopg2 está instalado
print("\n1️⃣ Verificando psycopg2...")
try:
    import psycopg2
    print(f"   ✅ psycopg2 {psycopg2.__version__}")
except ImportError:
    print("   ❌ psycopg2 no instalado")
    print("   📦 Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    print("   ✅ Instalado!")

# 2. Probar conexión
print("\n2️⃣ Probando conexión a PostgreSQL...")
try:
    # Intentar conexión
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgres"
    )
    print("   ✅ ¡CONEXIÓN EXITOSA!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"   📊 PostgreSQL: {version[0][:60]}...")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n🔧 POSIBLES SOLUCIONES:")
    print("   1. PostgreSQL no está instalado")
    print("   2. PostgreSQL no está corriendo")
    print("   3. Contraseña incorrecta")
    print("\n   📌 Para verificar servicios:")
    print("   • Abre Services.msc")
    print("   • Busca 'postgresql'")
    print("   • Debe estar 'Running'")

print("\n" + "=" * 60)
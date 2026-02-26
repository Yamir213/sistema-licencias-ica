print("=" * 50)
print("🔍 VERIFICANDO INSTALACIÓN")
print("=" * 50)

# 1. Verificar que Python funciona
print("\n1️⃣ Python:", end=" ")
import sys
print(f"✅ {sys.version.split()[0]}")

# 2. Verificar pip
print("\n2️⃣ Pip:", end=" ")
try:
    import pip
    print(f"✅ {pip.__version__}")
except:
    print("❌ No instalado")

# 3. Verificar psycopg2
print("\n3️⃣ psycopg2:", end=" ")
try:
    import psycopg2
    print(f"✅ {psycopg2.__version__}")
except ImportError as e:
    print(f"❌ No instalado")
    print("   Instalando ahora...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    print("   ✅ Instalado!")

# 4. Verificar SQLAlchemy
print("\n4️⃣ SQLAlchemy:", end=" ")
try:
    import sqlalchemy
    print(f"✅ {sqlalchemy.__version__}")
except:
    print("❌ No instalado")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy"])
    print("   ✅ Instalado!")

print("\n" + "=" * 50)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 50)

print("\n📋 Ahora prueba: python test_postgres.py")
from app.database.connection import SessionLocal
from app.services.auth_service import AuthService

db = SessionLocal()

print("🔐 PROBANDO LOGIN DE FUNCIONARIO")
print("=" * 50)

email = "funcionario@muniica.gob.pe"
password = "123456"

result, message = AuthService.login_user(db, email, password)

if result:
    print(f"✅ LOGIN EXITOSO!")
    print(f"   Token: {result['access_token'][:30]}...")
    print(f"   Usuario: {result['user']['email']}")
    print(f"   Tipo: {result['user']['tipo']}")
    print(f"   Nombre: {result['user']['nombre']}")
else:
    print(f"❌ LOGIN FALLIDO: {message}")

db.close()
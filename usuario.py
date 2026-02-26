# Crea el archivo crear_funcionario_corregido.py
from app.database.connection import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash
from datetime import datetime

db = SessionLocal()

# Verificar si ya existe
existente = db.query(User).filter(User.email == "funcionario@muniica.gob.pe").first()
if existente:
    print("❌ Ya existe un usuario con ese email")
else:
    # Crear funcionario con todos los campos
    funcionario = User(
        email="funcionario@muniica.gob.pe",
        password_hash=get_password_hash("123456"),
        telefono="987654321",
        tipo_usuario="funcionario",  # 👈 ESTO ES CRÍTICO
        tipo_persona="natural",
        nombres="Carlos",
        apellido_paterno="Funcionario",
        apellido_materno="Municipal",
        dni="12345678",
        direccion="Palacio Municipal",
        distrito="Ica",
        cargo="Especialista en Licencias",
        area="Desarrollo Económico",
        is_active=True,
        is_verified=True,
        created_at=datetime.now()
    )
    
    db.add(funcionario)
    db.commit()
    print("✅ Funcionario creado correctamente:")
    print("   Email: funcionario@muniica.gob.pe")
    print("   Password: 123456")
    print(f"   Tipo: {funcionario.tipo_usuario}")

db.close()
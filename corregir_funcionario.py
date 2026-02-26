# Crea el archivo corregir_funcionario.py
from app.database.connection import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()

# Buscar el funcionario
funcionario = db.query(User).filter(User.email == "funcionario@muniica.gob.pe").first()

if funcionario:
    print(f"🔍 Funcionario encontrado:")
    print(f"   Email: {funcionario.email}")
    print(f"   Tipo actual: {funcionario.tipo_usuario}")
    
    # Corregir el tipo si es necesario
    if funcionario.tipo_usuario != "funcionario":
        funcionario.tipo_usuario = "funcionario"
        print(f"✅ Tipo corregido a: funcionario")
    
    # Asegurar que tenga área y cargo
    if not funcionario.area:
        funcionario.area = "Desarrollo Económico"
    if not funcionario.cargo:
        funcionario.cargo = "Especialista en Licencias"
    
    db.commit()
    print(f"✅ Funcionario actualizado correctamente")
    
else:
    print("❌ No se encontró el funcionario. Creando uno nuevo...")
    
    # Crear funcionario nuevo
    nuevo = User(
        email="funcionario@muniica.gob.pe",
        password_hash=get_password_hash("123456"),
        telefono="987654321",
        tipo_usuario="funcionario",  # 👈 EXPLÍCITAMENTE funcionario
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
        is_verified=True
    )
    db.add(nuevo)
    db.commit()
    print(f"✅ Nuevo funcionario creado")

# Verificar el resultado final
funcionario_verificado = db.query(User).filter(User.email == "funcionario@muniica.gob.pe").first()
print(f"\n📊 VERIFICACIÓN FINAL:")
print(f"   Email: {funcionario_verificado.email}")
print(f"   Tipo: {funcionario_verificado.tipo_usuario}")
print(f"   Área: {funcionario_verificado.area}")
print(f"   Cargo: {funcionario_verificado.cargo}")

db.close()
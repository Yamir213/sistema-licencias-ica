import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, Base, SessionLocal
from app.models.user import User
from app.models.config import Rubro, Tarifa, Zona
from app.models.solicitud import Solicitud
from datetime import datetime

print("=" * 60)
print("🗄️  INICIALIZANDO BASE DE DATOS SQLITE")
print("=" * 60)

try:
    # 1. CREAR TABLAS
    print("\n1️⃣ Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")
    
    # 2. DATOS INICIALES
    print("\n2️⃣ Insertando datos iniciales...")
    db = SessionLocal()
    
    # Verificar si ya hay datos
    if db.query(Rubro).count() == 0:
        print("   📝 Rubros comerciales...")
        rubros = [
            Rubro(codigo="C101", nombre="Bodega / Minimarket", nivel_riesgo="bajo"),
            Rubro(codigo="C102", nombre="Restaurante", nivel_riesgo="medio"),
            Rubro(codigo="C103", nombre="Farmacia", nivel_riesgo="medio"),
            Rubro(codigo="C104", nombre="Peluquería", nivel_riesgo="bajo"),
            Rubro(codigo="C105", nombre="Discoteca", nivel_riesgo="alto", requiere_itse_previa=True),
            Rubro(codigo="C106", nombre="Gasolinera", nivel_riesgo="muy_alto", requiere_itse_previa=True),
            Rubro(codigo="C107", nombre="Librería", nivel_riesgo="bajo"),
            Rubro(codigo="C108", nombre="Gimnasio", nivel_riesgo="medio"),
            Rubro(codigo="C109", nombre="Taller mecánico", nivel_riesgo="medio"),
            Rubro(codigo="C110", nombre="Panadería", nivel_riesgo="bajo"),
        ]
        db.add_all(rubros)
        
        print("   💰 Tarifas...")
        tarifas = [
            Tarifa(nivel_riesgo="bajo", monto=140.00, vigente_desde=datetime.now()),
            Tarifa(nivel_riesgo="medio", monto=150.00, vigente_desde=datetime.now()),
            Tarifa(nivel_riesgo="alto", monto=170.00, vigente_desde=datetime.now()),
            Tarifa(nivel_riesgo="muy_alto", monto=192.00, vigente_desde=datetime.now()),
        ]
        db.add_all(tarifas)
        
        print("   🗺️  Zonas de Ica...")
        zonas = [
            Zona(codigo="ZR", nombre="Zona Residencial", descripcion="Áreas de vivienda"),
            Zona(codigo="ZC", nombre="Zona Comercial", descripcion="Centro de Ica, mercados"),
            Zona(codigo="ZI", nombre="Zona Industrial", descripcion="Parque Industrial"),
            Zona(codigo="ZT", nombre="Zona Turística", descripcion="Huacachina, bodegas"),
        ]
        db.add_all(zonas)
        
        db.commit()
        print("✅ Datos iniciales insertados correctamente")
    else:
        print("ℹ️  La base de datos ya contiene datos")
    
    # 3. RESUMEN
    print("\n3️⃣ Resumen:")
    print(f"   📊 Rubros: {db.query(Rubro).count()}")
    print(f"   💰 Tarifas: {db.query(Tarifa).count()}")
    print(f"   🗺️  Zonas: {db.query(Zona).count()}")
    print(f"   👤 Usuarios: {db.query(User).count()}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ BASE DE DATOS SQLITE INICIALIZADA")
    print("=" * 60)
    print(f"\n📁 Archivo: app/database/data/licencias_ica.db")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
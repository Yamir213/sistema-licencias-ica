import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, Base, SessionLocal, test_connection
from datetime import datetime
import traceback

def init_database():
    """Crear tablas y datos iniciales - VERSIÓN CORREGIDA"""
    print("=" * 60)
    print("INICIALIZANDO BASE DE DATOS - POSTGRESQL 18")
    print("=" * 60)
    
    # 1. PROBAR CONEXIÓN PRIMERO
    print("\n1️⃣  Probando conexión a PostgreSQL...")
    if not test_connection():
        print("\n❌ NO SE PUDO CONECTAR A LA BASE DE DATOS")
        print("🔧 SOLUCIÓN RÁPIDA:")
        print("1. Verifica que PostgreSQL 18 esté instalado")
        print("2. Abre 'Services' (servicios.msc) y busca 'postgresql-x64-18'")
        print("3. Si no está corriendo, haz clic derecho -> Iniciar")
        print("4. Verifica tu archivo .env - usa solo: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/licencias_ica")
        return
    
    try:
        # 2. IMPORTAR MODELOS
        print("\n2️⃣  Cargando modelos...")
        from app.models.user import User
        from app.models.config import Rubro, Tarifa, Zona, NivelRiesgo
        from app.models.solicitud import Solicitud, EstadoSolicitud
        from app.models.documento import Documento, TipoDocumento
        from app.models.pago import Pago, EstadoPago, MetodoPago
        from app.models.auditoria import Auditoria, TipoAccion
        
        print("✅ Modelos cargados correctamente")
        
        # 3. CREAR TABLAS
        print("\n3️⃣  Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        # 4. INSERTAR DATOS INICIALES
        print("\n4️⃣  Insertando datos iniciales...")
        db = SessionLocal()
        
        try:
            # Verificar si ya hay datos
            if db.query(Rubro).count() == 0:
                print("📝 Insertando rubros comerciales...")
                
                # RUBROS - Usar Enum correctamente
                rubros = [
                    Rubro(
                        codigo="C101", 
                        nombre="Bodega / Minimarket", 
                        nivel_riesgo="bajo",
                        requiere_itse_previa=False,
                        descripcion="Venta de abarrotes y productos basicos"
                    ),
                    Rubro(
                        codigo="C102", 
                        nombre="Restaurante", 
                        nivel_riesgo="medio",
                        requiere_itse_previa=False,
                        descripcion="Servicio de comidas y bebidas"
                    ),
                    Rubro(
                        codigo="C103", 
                        nombre="Farmacia", 
                        nivel_riesgo="medio",
                        requiere_itse_previa=False,
                        descripcion="Venta de medicamentos"
                    ),
                    Rubro(
                        codigo="C104", 
                        nombre="Peluqueria / Barberia", 
                        nivel_riesgo="bajo",
                        requiere_itse_previa=False,
                        descripcion="Servicios de estetica personal"
                    ),
                    Rubro(
                        codigo="C105", 
                        nombre="Discoteca", 
                        nivel_riesgo="alto",
                        requiere_itse_previa=True,
                        descripcion="Entretenimiento nocturno"
                    ),
                    Rubro(
                        codigo="C106", 
                        nombre="Gasolinera", 
                        nivel_riesgo="muy_alto",
                        requiere_itse_previa=True,
                        descripcion="Venta de combustibles"
                    ),
                ]
                
                for rubro in rubros:
                    db.add(rubro)
                
                # TARIFAS
                print("💰 Insertando tarifas...")
                tarifas = [
                    Tarifa(
                        nivel_riesgo="bajo",
                        monto=140.00,
                        descripcion="Licencia para negocios de bajo riesgo",
                        vigente_desde=datetime.now()
                    ),
                    Tarifa(
                        nivel_riesgo="medio",
                        monto=150.00,
                        descripcion="Licencia para negocios de riesgo medio",
                        vigente_desde=datetime.now()
                    ),
                    Tarifa(
                        nivel_riesgo="alto",
                        monto=170.00,
                        descripcion="Licencia para negocios de alto riesgo",
                        vigente_desde=datetime.now()
                    ),
                    Tarifa(
                        nivel_riesgo="muy_alto",
                        monto=192.00,
                        descripcion="Licencia para negocios de muy alto riesgo",
                        vigente_desde=datetime.now()
                    ),
                ]
                
                for tarifa in tarifas:
                    db.add(tarifa)
                
                # ZONAS
                print("🗺️  Insertando zonas de Ica...")
                zonas = [
                    Zona(
                        codigo="ZR", 
                        nombre="Zona Residencial",
                        descripcion="Areas destinadas principalmente a viviendas"
                    ),
                    Zona(
                        codigo="ZC",
                        nombre="Zona Comercial",
                        descripcion="Areas para comercio y servicios (Centro de Ica)"
                    ),
                    Zona(
                        codigo="ZI",
                        nombre="Zona Industrial",
                        descripcion="Areas para industria (Parque Industrial de Ica)"
                    ),
                    Zona(
                        codigo="ZT",
                        nombre="Zona Turistica",
                        descripcion="Areas de desarrollo turistico (Huacachina)"
                    ),
                ]
                
                for zona in zonas:
                    db.add(zona)
                
                db.commit()
                print("✅ Datos iniciales insertados correctamente")
            else:
                print("ℹ️  La base de datos ya contiene datos")
            
            # Mostrar resumen
            print("\n5️⃣  Resumen de datos:")
            print("-" * 40)
            print(f"📊 Rubros: {db.query(Rubro).count()}")
            print(f"💰 Tarifas: {db.query(Tarifa).count()}")
            print(f"🗺️  Zonas: {db.query(Zona).count()}")
            print(f"👤 Usuarios: {db.query(User).count()}")
                
        except Exception as e:
            db.rollback()
            print(f"❌ Error al insertar datos: {e}")
            traceback.print_exc()
        finally:
            db.close()
            
        print("\n" + "=" * 60)
        print("✨ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_database()
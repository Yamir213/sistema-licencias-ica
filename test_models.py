import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Intentar importar los modelos
try:
    from app.models.user import User
    from app.models.config import Rubro, Tarifa, Zona
    from app.models.solicitud import Solicitud
    from app.models.documento import Documento
    from app.models.pago import Pago
    from app.models.auditoria import Auditoria
    
    print("✅ ¡TODOS LOS MODELOS IMPORTADOS CORRECTAMENTE!")
    print("\n📋 Modelos disponibles:")
    print(f"1. User - Tabla: {User.__tablename__}")
    print(f"2. Rubro - Tabla: {Rubro.__tablename__}")
    print(f"3. Tarifa - Tabla: {Tarifa.__tablename__}")
    print(f"4. Zona - Tabla: {Zona.__tablename__}")
    print(f"5. Solicitud - Tabla: {Solicitud.__tablename__}")
    print(f"6. Documento - Tabla: {Documento.__tablename__}")
    print(f"7. Pago - Tabla: {Pago.__tablename__}")
    print(f"8. Auditoria - Tabla: {Auditoria.__tablename__}")
    
    print("\n🎉 ¡Modelos creados exitosamente!")
    
except ImportError as e:
    print(f"❌ Error al importar modelos: {e}")
    print("\n🔧 Verifica que:")
    print("1. Todos los archivos .py existan en app/models/")
    print("2. Los imports en los archivos sean correctos")
    print("3. El archivo app/database/connection.py exista")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
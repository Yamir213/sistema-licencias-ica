from app.database.connection import SessionLocal
from app.models.solicitud import Solicitud

db = SessionLocal()
solicitudes = db.query(Solicitud).all()
print(f"📊 Total solicitudes en BD: {len(solicitudes)}")
for s in solicitudes:
    print(f"   • {s.numero_expediente} - {s.nombre_negocio} - {s.estado}")
db.close()
exit()
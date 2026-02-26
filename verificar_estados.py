from app.models.solicitud import EstadoSolicitud

print("🔍 ESTADOS DE SOLICITUD DISPONIBLES:")
print("=" * 50)

for estado in EstadoSolicitud:
    print(f"✅ {estado.value}")

print(f"\n📊 Total: {len(list(EstadoSolicitud))} estados")
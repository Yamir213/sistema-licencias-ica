from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os

# ============ IMPORTACIONES LOCALES ============
from app.database.connection import get_db
from app.utils.security import decode_token
from app.utils.dependencies import get_current_user, get_current_funcionario
from app.routers import auth, solicitud
from app.models.user import User

# ============ CREAR APLICACIÓN FASTAPI ============
app = FastAPI(
    title="Sistema de Licencias de Funcionamiento - Municipalidad de Ica",
    description="Sistema 100% en línea para trámite de licencias de funcionamiento",
    version="1.0.0"
)

# ============ CONFIGURAR CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ CREAR CARPETAS NECESARIAS ============
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/static/images", exist_ok=True)
os.makedirs("app/templates/portal", exist_ok=True)
os.makedirs("app/templates/municipal", exist_ok=True)
os.makedirs("app/templates/solicitud", exist_ok=True)

# ============ CONFIGURAR ARCHIVOS ESTÁTICOS Y TEMPLATES ============
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ============ INCLUIR ROUTERS ============
app.include_router(auth.router)
app.include_router(solicitud.router)

# ============ RUTAS PÚBLICAS ============

@app.get("/")
async def home(request: Request):
    """Página de inicio - Portal Ciudadano"""
    return templates.TemplateResponse(
        "portal/index.html", 
        {
            "request": request,
            "title": "Licencias de Funcionamiento - Municipalidad de Ica",
            "year": 2024
        }
    )

@app.get("/municipal")
async def municipal_dashboard(request: Request):
    """Dashboard Municipal"""
    return templates.TemplateResponse(
        "municipal/dashboard.html",
        {
            "request": request,
            "title": "Back Office - Municipalidad de Ica"
        }
    )

@app.get("/health")
async def health_check():
    """Verificar estado del sistema"""
    return {
        "status": "healthy",
        "service": "Sistema de Licencias - Ica",
        "version": "1.0.0",
        "database": "SQLite"
    }

# ============ RUTAS PROTEGIDAS ============

@app.get("/portal/dashboard")
async def portal_dashboard(
    request: Request, 
    db: Session = Depends(get_db)
):
    """Dashboard del ciudadano con lista de solicitudes"""
    try:
        # Verificar token en cookie
        token = request.cookies.get("access_token")
        
        if not token:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Decodificar token
        token = token.replace("Bearer ", "")
        payload = decode_token(token)
        
        if not payload:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Obtener usuario
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Obtener nombre del usuario
        nombre = user.nombre_completo()
        if not nombre:
            nombre = user.email.split('@')[0]
        
        # 👇 OBTENER SOLICITUDES DEL USUARIO DESDE LA BD
        from app.models.solicitud import Solicitud
        
        solicitudes = db.query(Solicitud).filter(
            Solicitud.usuario_id == user.id
        ).order_by(
            Solicitud.created_at.desc()
        ).all()
        
        print(f"📊 Usuario {user.email} tiene {len(solicitudes)} solicitudes en BD")
        
        return templates.TemplateResponse(
            "portal/dashboard.html",
            {
                "request": request,
                "user": {
                    "nombre": nombre,
                    "email": user.email,
                    "tipo": user.tipo_usuario
                },
                "solicitudes": solicitudes  # 👈 PASAR SOLICITUDES AL TEMPLATE
            }
        )
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/auth/login", status_code=302)

# ============ RUTAS DE DEPURACIÓN ============

@app.get("/debug/cookies")
async def debug_cookies(request: Request):
    """Ver qué cookies hay guardadas"""
    cookies = dict(request.cookies)
    token = cookies.get("access_token", "No hay token")
    
    # Intentar decodificar el token si existe
    user_info = None
    token_preview = None
    
    if token != "No hay token" and token.startswith("Bearer "):
        token_value = token.replace("Bearer ", "")
        token_preview = token_value[:20] + "..." if len(token_value) > 20 else token_value
        
        # Decodificar payload
        payload = decode_token(token_value)
        if payload:
            user_info = {
                "email": payload.get("sub"),
                "exp": payload.get("exp")
            }
    else:
        token_preview = token[:30] + "..." if token != "No hay token" else token
    
    return {
        "cookies": cookies,
        "has_token": "access_token" in cookies,
        "token_preview": token_preview,
        "user_info": user_info,
        "headers": {
            "host": request.headers.get("host"),
            "user_agent": request.headers.get("user-agent")[:50] + "..." if request.headers.get("user-agent") else None
        }
    }

@app.get("/debug/auth")
async def debug_auth(request: Request):
    """Verificar estado de autenticación"""
    return await debug_cookies(request)
@app.get("/portal/documentos")
async def portal_documentos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Panel de documentos digitales"""
    
    from app.models.solicitud import Solicitud
    from app.models.pago import Pago
    from app.models.documento import Documento
    
    # Obtener solicitudes del usuario con licencias emitidas
    licencias = db.query(Solicitud).filter(
        Solicitud.usuario_id == current_user.id,
        Solicitud.estado == "licencia_emitida"
    ).all()
    
    # Obtener pagos del usuario
    vouchers = db.query(Pago).join(Solicitud).filter(
        Solicitud.usuario_id == current_user.id,
        Pago.estado == "completado"
    ).all()
    
    # Obtener documentos subidos
    documentos = db.query(Documento).join(Solicitud).filter(
        Solicitud.usuario_id == current_user.id
    ).all()
    
    return templates.TemplateResponse(
        "portal/documentos.html",
        {
            "request": request,
            "user": current_user,
            "licencias": licencias,
            "vouchers": vouchers,
            "documentos": documentos
        }
    )
# ============ EVENTOS DE INICIO ============

@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("🚀 SISTEMA DE LICENCIAS - MUNICIPALIDAD DE ICA")
    print("=" * 60)
    print("✅ FastAPI iniciado correctamente")
    print("✅ Base de datos: SQLite")
    print("✅ Archivos estáticos: /static")
    print("✅ Routers cargados: auth, solicitud")
    print(f"🌐 Servidor: http://localhost:8000")
    print("=" * 60 + "\n")

# ============ PUNTO DE ENTRADA ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

    # Importar router municipal
from app.routers import auth, solicitud, municipal

# Incluir router
app.include_router(auth.router)
app.include_router(solicitud.router)
app.include_router(municipal.router)  # 👈 NUEVO
    
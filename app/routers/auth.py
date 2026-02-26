from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_token
from app.utils.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.services.notificacion_service import NotificacionService
from datetime import datetime
import re

router = APIRouter(prefix="/auth", tags=["Autenticación"])
templates = Jinja2Templates(directory="app/templates")

# ============ PÁGINAS WEB ============

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse(
        "portal/login.html",
        {"request": request, "title": "Iniciar Sesión - Municipalidad de Ica", "error": None}
    )

@router.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request):
    """Página de registro"""
    return templates.TemplateResponse(
        "portal/registro.html",
        {"request": request, "title": "Registro - Municipalidad de Ica", "error": None}
    )

@router.get("/logout")
async def logout():
    """Cerrar sesión"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token", path="/")
    return response

# ============ API ENDPOINTS ============

@router.post("/api/registro")
async def registro(
    request: Request,
    db: Session = Depends(get_db)
):
    """API para registro de usuarios - CON NOTIFICACIÓN DE BIENVENIDA"""
    
    try:
        form = await request.form()
        
        # Validar contraseñas
        password = form.get("password")
        confirm_password = form.get("confirm_password")
        
        if password != confirm_password:
            return templates.TemplateResponse(
                "portal/registro.html",
                {
                    "request": request,
                    "title": "Registro - Municipalidad de Ica",
                    "error": "Las contraseñas no coinciden"
                }
            )
        
        user_data = {
            "email": form.get("email"),
            "password": password,
            "telefono": form.get("telefono"),
            "tipo_usuario": "ciudadano",
            "tipo_persona": form.get("tipo_persona"),
        }
        
        # Datos según tipo de persona
        if form.get("tipo_persona") == "natural":
            user_data.update({
                "dni": form.get("dni"),
                "nombres": form.get("nombres"),
                "apellido_paterno": form.get("apellido_paterno"),
                "apellido_materno": form.get("apellido_materno"),
            })
        else:
            user_data.update({
                "ruc": form.get("ruc"),
                "razon_social": form.get("razon_social"),
                "nombre_comercial": form.get("nombre_comercial"),
                "representante_legal": form.get("representante_legal"),
            })
        
        user_data.update({
            "direccion": form.get("direccion"),
            "distrito": form.get("distrito"),
        })
        
        # Crear usuario usando AuthService
        user, message = AuthService.create_user(db, user_data)
        
        if not user:
            return templates.TemplateResponse(
                "portal/registro.html",
                {
                    "request": request,
                    "title": "Registro - Municipalidad de Ica",
                    "error": message
                }
            )
        
        # Notificación de bienvenida
        print(f"📧 Enviando email de bienvenida a: {user.email}")
        await NotificacionService.notificar_bienvenida(db, user)
        
        # Login automático después de registro
        result, _ = AuthService.login_user(db, user_data["email"], user_data["password"])
        
        response = RedirectResponse(url="/portal/dashboard", status_code=302)
        if result:
            response.set_cookie(
                key="access_token",
                value=f"Bearer {result['access_token']}",
                httponly=True,
                max_age=86400,
                path="/",
                secure=False,
                samesite="lax"
            )
        
        return response
        
    except Exception as e:
        print(f"❌ Error en registro: {str(e)}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "portal/registro.html",
            {
                "request": request,
                "title": "Registro - Municipalidad de Ica",
                "error": f"Error en el registro: {str(e)}"
            }
        )

@router.post("/api/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """API para login de usuarios - VERSIÓN CORREGIDA Y LIMPIA"""
    try:
        form = await request.form()
        
        email = form.get("email")
        password = form.get("password")
        
        if not email or not password:
            return templates.TemplateResponse(
                "portal/login.html",
                {
                    "request": request,
                    "title": "Iniciar Sesión - Municipalidad de Ica",
                    "error": "Email y contraseña son obligatorios"
                }
            )
        
        result, message = AuthService.login_user(db, email, password)
        
        if not result:
            return templates.TemplateResponse(
                "portal/login.html",
                {
                    "request": request,
                    "title": "Iniciar Sesión - Municipalidad de Ica",
                    "error": message
                }
            )
        
        # Crear respuesta con redirect
        response = RedirectResponse(url="/portal/dashboard", status_code=302)
        
        # Establecer cookie correctamente
        response.set_cookie(
            key="access_token",
            value=f"Bearer {result['access_token']}",
            httponly=True,
            max_age=86400,  # 24 horas
            path="/",       # Importante: disponible en todo el sitio
            secure=False,   # False para desarrollo local
            samesite="lax"  # Protección CSRF
        )
        
        print(f"✅ Login exitoso: {email}")
        print(f"🔑 Token guardado en cookie")
        print(f"📍 Path de cookie: /")
        print(f"⏰ Expira: 24 horas")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "portal/login.html",
            {
                "request": request,
                "title": "Iniciar Sesión - Municipalidad de Ica",
                "error": f"Error en el login: {str(e)}"
            }
        )

@router.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": current_user.nombre_completo(),
        "tipo_usuario": current_user.tipo_usuario,
        "tipo_persona": current_user.tipo_persona
    }
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.utils.security import decode_token

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene el usuario actual a partir del token JWT en cookie - VERSIÓN CORREGIDA"""
    
    print("🔍 Verificando autenticación...")
    
    # 1. Intentar obtener token de cookie primero
    token = request.cookies.get("access_token")
    
    if token and token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
        print(f"✅ Token encontrado en cookie")
    else:
        print("❌ No hay token en cookie")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado - Inicia sesión primero"
        )
    
    # 2. Decodificar token
    payload = decode_token(token)
    if not payload:
        print("❌ Token inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # 3. Obtener email del payload
    email = payload.get("sub")
    if not email:
        print("❌ Token sin email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # 4. Buscar usuario en BD
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ Usuario no encontrado: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    print(f"✅ Usuario autenticado: {user.email}")
    return user

async def get_current_funcionario(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario sea funcionario o administrador"""
    if current_user.tipo_usuario not in ["funcionario", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de funcionario"
        )
    return current_user
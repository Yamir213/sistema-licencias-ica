from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.utils.security import decode_token

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """VERSIÓN DEMO - Siempre devuelve un usuario"""
    
    # Buscar o crear usuario demo
    demo_user = db.query(User).filter(User.email == "demo@funcionario.com").first()
    
    if not demo_user:
        from app.utils.security import get_password_hash
        demo_user = User(
            email="demo@funcionario.com",
            password_hash=get_password_hash("demo"),
            tipo_usuario="funcionario",
            nombres="Usuario",
            apellido_paterno="Demo",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    
    return demo_user

async def get_current_funcionario(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario sea funcionario o administrador"""
    if current_user.tipo_usuario not in ["funcionario", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de funcionario"
        )
    return current_user
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import verify_password, get_password_hash, create_access_token
from datetime import datetime

class AuthService:
    
    @staticmethod
    def create_user(db: Session, user_data: dict):
        """Crea nuevo usuario"""
        try:
            # Verificar email
            if db.query(User).filter(User.email == user_data["email"]).first():
                return None, "Email ya registrado"
            
            # Hash contraseña
            hashed_password = get_password_hash(user_data["password"])
            
            # Crear usuario
            user = User(
                email=user_data["email"],
                password_hash=hashed_password,
                telefono=user_data.get("telefono", ""),
                tipo_usuario=user_data.get("tipo_usuario", "ciudadano"),
                tipo_persona=user_data.get("tipo_persona", "natural"),
                direccion=user_data.get("direccion", ""),
                distrito=user_data.get("distrito", "Ica"),
                is_active=True,
                is_verified=False
            )
            
            # Datos adicionales
            if user_data.get("dni"):
                user.dni = user_data["dni"]
                user.nombres = user_data.get("nombres", "")
                user.apellido_paterno = user_data.get("apellido_paterno", "")
                user.apellido_materno = user_data.get("apellido_materno", "")
            
            if user_data.get("ruc"):
                user.ruc = user_data["ruc"]
                user.razon_social = user_data.get("razon_social", "")
                user.nombre_comercial = user_data.get("nombre_comercial", "")
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user, "Usuario creado exitosamente"
            
        except Exception as e:
            db.rollback()
            return None, f"Error: {str(e)}"
    
    @staticmethod
    def login_user(db: Session, email: str, password: str):
        """Login de usuario - VERSIÓN CORREGIDA CON TIPO"""
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user or not verify_password(password, user.password_hash):
                return None, "Email o contraseña incorrectos"
            
            user.last_login = datetime.now()
            db.commit()
            
            # Crear token con información del usuario
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "tipo": user.tipo_usuario,  # 👈 IMPORTANTE: Incluir tipo en el token
                "nombre": user.nombre_completo()
            }
            
            token = create_access_token(token_data)
            
            # 👇 ESTRUCTURA CORREGIDA - Incluye 'tipo' explícitamente
            result = {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nombre": user.nombre_completo() or user.email,
                    "tipo": user.tipo_usuario,  # 👈 CAMPO TIPO EXPLÍCITO
                    "tipo_persona": user.tipo_persona
                }
            }
            
            print(f"✅ Login exitoso - Usuario: {email}, Tipo: {user.tipo_usuario}")
            
            return result, "Login exitoso"
            
        except Exception as e:
            print(f"❌ Error en login_user: {e}")
            import traceback
            traceback.print_exc()
            return None, f"Error en el servidor: {str(e)}"
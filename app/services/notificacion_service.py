from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion, TipoNotificacion, EstadoNotificacion
from app.models.user import User
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class NotificacionService:
    """Servicio de notificaciones - VERSIÓN ULTRA SIMPLE SIN CARACTERES ESPECIALES"""
    
    @classmethod
    async def enviar_email(cls, db: Session, destinatario: str, asunto: str, mensaje: str, 
                          usuario_id: int = None, solicitud_id: int = None):
        """Solo simulación - Sin errores de codificación"""
        
        # Registrar notificación
        notificacion = Notificacion(
            usuario_id=usuario_id,
            destinatario=destinatario,
            tipo="email",
            asunto=asunto,
            mensaje=mensaje,
            solicitud_id=solicitud_id,
            estado="enviado"
        )
        db.add(notificacion)
        db.commit()
        
        # SOLO SIMULACIÓN - SIN INTENTAR ENVIAR EMAIL REAL
        print(f"\n{'='*60}")
        print(f"📧 NOTIFICACIÓN SIMULADA")
        print(f"{'='*60}")
        print(f"   Para: {destinatario}")
        print(f"   Asunto: {asunto}")
        print(f"   Mensaje: [HTML omitido - {len(mensaje)} caracteres]")
        print(f"{'='*60}\n")
        
        return True, "Email simulado exitosamente"
    
    @classmethod
    async def enviar_sms(cls, db: Session, telefono: str, mensaje: str,
                        usuario_id: int = None, solicitud_id: int = None):
        """Simulación de SMS"""
        
        notificacion = Notificacion(
            usuario_id=usuario_id,
            destinatario=telefono,
            tipo="sms",
            mensaje=mensaje,
            solicitud_id=solicitud_id,
            estado="enviado"
        )
        db.add(notificacion)
        db.commit()
        
        print(f"\n📱 SMS SIMULADO")
        print(f"   Teléfono: {telefono}")
        print(f"   Mensaje: {mensaje}\n")
        
        return True, "SMS simulado exitosamente"
    
    @classmethod
    async def notificar_bienvenida(cls, db: Session, user: User):
        """Email de bienvenida - VERSIÓN SIN HTML COMPLEJO"""
        
        nombre = user.email.split('@')[0]  # Usar solo la parte local del email
        
        mensaje = f"""
        Hola {nombre},
        
        Tu cuenta ha sido creada exitosamente.
        
        Ya puedes iniciar el tramite de tu licencia de funcionamiento en:
        http://localhost:8000/solicitud/paso1
        
        Saludos,
        Municipalidad de Ica
        """
        
        await cls.enviar_email(
            db=db,
            destinatario=user.email,
            asunto="Bienvenido al Sistema de Licencias - Ica",
            mensaje=mensaje,
            usuario_id=user.id
        )
@classmethod
async def notificar_cambio_estado(cls, db: Session, user: User, solicitud, nuevo_estado: str, mensaje: str):
    """Notificar cambio de estado en la solicitud - VERSIÓN SIMPLIFICADA"""
    
    try:
        nombre = user.nombre_completo() or user.email
        
        # Mensaje simple para email
        email_mensaje = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #0B3B5C; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Municipalidad de Ica</h1>
            </div>
            <div style="background: white; padding: 30px; border: 1px solid #e0e0e0;">
                <h2>Estimado/a {nombre},</h2>
                <p>Le informamos que su solicitud ha cambiado de estado:</p>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>Expediente:</strong> {solicitud.numero_expediente}</p>
                    <p><strong>Nuevo estado:</strong> {nuevo_estado.upper()}</p>
                    <p><strong>Mensaje:</strong> {mensaje}</p>
                </div>
                <p>Puede ver el detalle en su dashboard.</p>
            </div>
        </div>
        """
        
        await cls.enviar_email(
            db=db,
            destinatario=user.email,
            asunto=f"Actualización de solicitud - {solicitud.numero_expediente}",
            mensaje=email_mensaje,
            usuario_id=user.id,
            solicitud_id=solicitud.id
        )
        
        print(f"📧 Notificación de cambio de estado enviada a {user.email}")
        
    except Exception as e:
        print(f"❌ Error en notificar_cambio_estado: {e}")
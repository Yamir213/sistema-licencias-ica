from sqlalchemy.orm import Session
from app.models.inspeccion import Inspeccion, EstadoInspeccion
from app.models.solicitud import Solicitud
from app.models.user import User
from datetime import datetime, timedelta
import json

class InspeccionService:
    
    @staticmethod
    def programar_inspeccion(db: Session, solicitud_id: int, fecha_programada: datetime, inspector_id: int = None):
        """Programar una nueva inspección"""
        
        inspeccion = Inspeccion(
            solicitud_id=solicitud_id,
            inspector_id=inspector_id,
            fecha_programada=fecha_programada,
            estado=EstadoInspeccion.PROGRAMADA.value
        )
        
        db.add(inspeccion)
        db.commit()
        db.refresh(inspeccion)
        
        # Actualizar estado de la solicitud
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if solicitud:
            solicitud.estado = "pendiente_itse"
            db.commit()
        
        return inspeccion
    
    @staticmethod
    def iniciar_inspeccion(db: Session, inspeccion_id: int):
        """Marcar inspección como en curso"""
        
        inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
        if inspeccion:
            inspeccion.estado = EstadoInspeccion.EN_CURSO.value
            db.commit()
        
        return inspeccion
    
    @staticmethod
    def finalizar_inspeccion(db: Session, inspeccion_id: int, datos: dict):
        """Finalizar inspección y guardar resultados"""
        
        inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
        if not inspeccion:
            return None
        
        # Actualizar datos de la inspección
        inspeccion.estado = EstadoInspeccion.REALIZADA.value
        inspeccion.fecha_realizada = datetime.now()
        inspeccion.observaciones = datos.get("observaciones")
        inspeccion.recomendaciones = datos.get("recomendaciones")
        
        # Checklist
        inspeccion.extintores = datos.get("extintores", False)
        inspeccion.luces_emergencia = datos.get("luces_emergencia", False)
        inspeccion.señalizacion = datos.get("señalizacion", False)
        inspeccion.sistema_electrico = datos.get("sistema_electrico", False)
        inspeccion.via_evacuacion = datos.get("via_evacuacion", False)
        
        # Determinar resultado
        items_ok = sum([
            inspeccion.extintores,
            inspeccion.luces_emergencia,
            inspeccion.señalizacion,
            inspeccion.sistema_electrico,
            inspeccion.via_evacuacion
        ])
        
        if items_ok >= 4:
            inspeccion.resultado = "aprobado"
            # Actualizar solicitud
            solicitud = inspeccion.solicitud
            solicitud.itse_aprobado = True
            solicitud.fecha_itse = datetime.now()
            solicitud.estado = "itse_aprobado"
        elif items_ok >= 2:
            inspeccion.resultado = "observado"
        else:
            inspeccion.resultado = "rechazado"
        
        db.commit()
        
        return inspeccion
    
    @staticmethod
    def get_inspecciones_pendientes(db: Session, limite: int = 10):
        """Obtener inspecciones programadas"""
        
        return db.query(Inspeccion).filter(
            Inspeccion.estado.in_(["programada", "en_curso"])
        ).order_by(Inspeccion.fecha_programada).limit(limite).all()
    
    @staticmethod
    def get_inspecciones_por_inspector(db: Session, inspector_id: int):
        """Obtener inspecciones asignadas a un inspector"""
        
        return db.query(Inspeccion).filter(
            Inspeccion.inspector_id == inspector_id
        ).order_by(Inspeccion.fecha_programada).all()
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.solicitud import Solicitud
from app.models.pago import Pago
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

class ReporteService:
    
    @staticmethod
    def get_estadisticas_generales(db: Session, fecha_desde: datetime = None, fecha_hasta: datetime = None):
        """Obtener estadísticas generales del sistema"""
        
        if not fecha_desde:
            fecha_desde = datetime.now() - timedelta(days=365)
        if not fecha_hasta:
            fecha_hasta = datetime.now()
        
        # Consulta base
        query = db.query(Solicitud).filter(
            Solicitud.created_at >= fecha_desde,
            Solicitud.created_at <= fecha_hasta
        )
        
        # Totales
        total = query.count()
        
        # Solicitudes por estado - ✅ AGREGADO 'pendientes_pago'
        pendientes_pago = query.filter(Solicitud.estado == "pendiente_pago").count()
        pagadas = query.filter(Solicitud.estado == "pagado").count()
        aprobadas = query.filter(Solicitud.estado == "aprobado").count()
        rechazadas = query.filter(Solicitud.estado == "rechazado").count()
        emitidas = query.filter(Solicitud.estado == "licencia_emitida").count()
        
        # Ingresos
        ingresos = db.query(func.sum(Solicitud.monto_pago)).filter(
            Solicitud.created_at >= fecha_desde,
            Solicitud.created_at <= fecha_hasta,
            Solicitud.estado.in_(["pagado", "aprobado", "licencia_emitida"])
        ).scalar() or 0
        
        # Tiempo promedio de aprobación (en días)
        solicitudes_aprobadas = query.filter(
            Solicitud.estado == "licencia_emitida",
            Solicitud.fecha_emision.isnot(None)
        ).all()
        
        tiempo_promedio = 0
        if solicitudes_aprobadas:
            tiempos = [(s.fecha_emision - s.created_at).days for s in solicitudes_aprobadas]
            tiempo_promedio = sum(tiempos) / len(tiempos)
        
        # Distribución por riesgo
        riesgo_bajo = query.filter(Solicitud.nivel_riesgo == "bajo").count()
        riesgo_medio = query.filter(Solicitud.nivel_riesgo == "medio").count()
        riesgo_alto = query.filter(Solicitud.nivel_riesgo == "alto").count()
        riesgo_muy_alto = query.filter(Solicitud.nivel_riesgo == "muy_alto").count()
        
        # ✅ DEVOLVER TODAS LAS CLAVES, INCLUYENDO 'pendientes_pago'
        return {
            "total": total,
            "pendientes_pago": pendientes_pago,  # 👈 ESTA ES LA CLAVE QUE FALTABA
            "pagadas": pagadas,
            "aprobadas": aprobadas,
            "rechazadas": rechazadas,
            "emitidas": emitidas,
            "ingresos": ingresos,
            "tiempo_promedio": round(tiempo_promedio, 1),
            "riesgo_bajo": riesgo_bajo,
            "riesgo_medio": riesgo_medio,
            "riesgo_alto": riesgo_alto,
            "riesgo_muy_alto": riesgo_muy_alto,
            "tasa_aprobacion": round((aprobadas / total * 100) if total > 0 else 0, 1)
        }
    
    @staticmethod
    def get_solicitudes_por_mes(db: Session, anio: int = None):
        """Obtener solicitudes agrupadas por mes"""
        
        if not anio:
            anio = datetime.now().year
        
        meses = []
        solicitudes_data = []
        ingresos_data = []
        
        for mes in range(1, 13):
            nombre_mes = calendar.month_name[mes][:3]  # Ene, Feb, etc.
            meses.append(nombre_mes)
            
            # Solicitudes del mes
            count = db.query(Solicitud).filter(
                extract('year', Solicitud.created_at) == anio,
                extract('month', Solicitud.created_at) == mes
            ).count()
            solicitudes_data.append(count)
            
            # Ingresos del mes
            ingresos = db.query(func.sum(Solicitud.monto_pago)).filter(
                extract('year', Solicitud.created_at) == anio,
                extract('month', Solicitud.created_at) == mes,
                Solicitud.estado.in_(["pagado", "aprobado", "licencia_emitida"])
            ).scalar() or 0
            ingresos_data.append(float(ingresos))
        
        return {
            "meses": meses,
            "solicitudes": solicitudes_data,
            "ingresos": ingresos_data
        }
    
    @staticmethod
    def get_detalle_mensual(db: Session, anio: int = None):
        """Obtener detalle completo por mes"""
        
        if not anio:
            anio = datetime.now().year
        
        detalle = []
        
        for mes in range(1, 13):
            query = db.query(Solicitud).filter(
                extract('year', Solicitud.created_at) == anio,
                extract('month', Solicitud.created_at) == mes
            )
            
            total = query.count()
            pagadas = query.filter(Solicitud.estado == "pagado").count()
            aprobadas = query.filter(Solicitud.estado == "aprobado").count()
            rechazadas = query.filter(Solicitud.estado == "rechazado").count()
            
            ingresos = db.query(func.sum(Solicitud.monto_pago)).filter(
                extract('year', Solicitud.created_at) == anio,
                extract('month', Solicitud.created_at) == mes,
                Solicitud.estado.in_(["pagado", "aprobado", "licencia_emitida"])
            ).scalar() or 0
            
            # Tiempo promedio del mes
            aprobadas_mes = query.filter(
                Solicitud.estado == "licencia_emitida",
                Solicitud.fecha_emision.isnot(None)
            ).all()
            
            tiempo_promedio = 0
            if aprobadas_mes:
                tiempos = [(s.fecha_emision - s.created_at).days for s in aprobadas_mes]
                tiempo_promedio = sum(tiempos) / len(tiempos)
            
            detalle.append({
                "mes": calendar.month_name[mes][:3].upper(),
                "total": total,
                "pagadas": pagadas,
                "aprobadas": aprobadas,
                "rechazadas": rechazadas,
                "ingresos": ingresos,
                "tiempo_promedio": round(tiempo_promedio, 1)
            })
        
        return detalle
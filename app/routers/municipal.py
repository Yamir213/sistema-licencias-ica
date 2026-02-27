from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import json
from app.utils.security import create_access_token, get_password_hash
from app.database.connection import get_db
from app.utils.dependencies import get_current_funcionario
from app.models.user import User
from app.models.solicitud import Solicitud, EstadoSolicitud
from app.models.config import Rubro, Tarifa, Zona
from app.models.pago import Pago
from app.models.inspeccion import Inspeccion, EstadoInspeccion
from app.services.notificacion_service import NotificacionService
from app.services.auth_service import AuthService
from app.services.inspeccion_service import InspeccionService
from app.services.reporte_service import ReporteService

router = APIRouter(prefix="/municipal", tags=["Back-Office Municipal"])
templates = Jinja2Templates(directory="app/templates")

# ============ LOGIN FUNCIONARIOS ============

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login para funcionarios"""
    return templates.TemplateResponse(
        "municipal/login.html",
        {"request": request, "error": None}
    )

@router.post("/api/login")
async def login_funcionario(
    request: Request,
    db: Session = Depends(get_db)
):
    """Login de funcionarios"""
    try:
        form = await request.form()
        email = form.get("email")
        password = form.get("password")
        
        print(f"🔐 Intento de login funcionario: {email}")
        
        result, message = AuthService.login_user(db, email, password)
        
        if not result:
            print(f"❌ Login fallido: {message}")
            return templates.TemplateResponse(
                "municipal/login.html",
                {"request": request, "error": "Credenciales incorrectas"}
            )
        
        user_tipo = result['user'].get('tipo')
        print(f"👤 Usuario: {result['user']['email']}, Tipo: {user_tipo}")
        
        if user_tipo not in ['funcionario', 'administrador', 'inspector']:
            print(f"❌ Usuario no autorizado: {user_tipo}")
            return templates.TemplateResponse(
                "municipal/login.html",
                {"request": request, "error": "Usuario no autorizado para el back-office"}
            )
        
        print(f"✅ Login exitoso: {email}")
        
        response = RedirectResponse(url="/municipal/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {result['access_token']}",
            httponly=True,
            path="/",
            max_age=86400
        )
        return response
        
    except Exception as e:
        print(f"❌ Error en login funcionario: {str(e)}")
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "municipal/login.html",
            {"request": request, "error": f"Error en el servidor: {str(e)}"}
        )

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/municipal/login", status_code=302)
    response.delete_cookie("access_token", path="/")
    return response

# ============ DASHBOARD ============

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Dashboard municipal con estadísticas"""
    
    try:
        print(f"📊 Accediendo a dashboard municipal - Usuario: {current_user.email}")
        
        # Estadísticas de solicitudes
        total_solicitudes = db.query(Solicitud).count()
        pendientes_pago = db.query(Solicitud).filter(Solicitud.estado == "pendiente_pago").count()
        pagadas = db.query(Solicitud).filter(Solicitud.estado == "pagado").count()
        en_revision = db.query(Solicitud).filter(Solicitud.estado == "en_revision").count()
        aprobadas = db.query(Solicitud).filter(Solicitud.estado == "aprobado").count()
        rechazadas = db.query(Solicitud).filter(Solicitud.estado == "rechazado").count()
        emitidas = db.query(Solicitud).filter(Solicitud.estado == "licencia_emitida").count()
        
        # Estadísticas por riesgo
        bajo = db.query(Solicitud).filter(Solicitud.nivel_riesgo == "bajo").count()
        medio = db.query(Solicitud).filter(Solicitud.nivel_riesgo == "medio").count()
        alto = db.query(Solicitud).filter(Solicitud.nivel_riesgo.in_(["alto", "muy_alto"])).count()
        
        # Estadísticas de inspecciones
        inspecciones_programadas = db.query(Inspeccion).filter(Inspeccion.estado == "programada").count()
        inspecciones_realizadas = db.query(Inspeccion).filter(Inspeccion.estado == "realizada").count()
        
        stats = {
            "total": total_solicitudes,
            "pendientes_pago": pendientes_pago,
            "pagadas": pagadas,
            "en_revision": en_revision,
            "aprobadas": aprobadas,
            "rechazadas": rechazadas,
            "emitidas": emitidas,
            "bajo": bajo,
            "medio": medio,
            "alto": alto,
            "inspecciones_programadas": inspecciones_programadas,
            "inspecciones_realizadas": inspecciones_realizadas,
        }
        
        total_riesgo = bajo + medio + alto
        stats['bajo_porcentaje'] = (bajo / total_riesgo * 100) if total_riesgo > 0 else 0
        stats['medio_porcentaje'] = (medio / total_riesgo * 100) if total_riesgo > 0 else 0
        stats['alto_porcentaje'] = (alto / total_riesgo * 100) if total_riesgo > 0 else 0
        
        # Solicitudes recientes
        solicitudes = db.query(Solicitud).order_by(Solicitud.created_at.desc()).limit(5).all()
        
        # Inspecciones próximas
        inspecciones = db.query(Inspeccion).filter(
            Inspeccion.estado.in_(["programada", "en_curso"])
        ).order_by(Inspeccion.fecha_programada).limit(5).all()
        
        # Tarifas vigentes
        tarifas = db.query(Tarifa).filter(Tarifa.is_active == True).all()
        
        print(f"✅ Dashboard cargado - Total solicitudes: {total_solicitudes}")
        
        return templates.TemplateResponse(
            "municipal/dashboard.html",
            {
                "request": request,
                "user": current_user,
                "stats": stats,
                "solicitudes": solicitudes,
                "inspecciones": inspecciones,
                "tarifas": tarifas,
                "now": datetime.now
            }
        )
        
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/municipal/login", status_code=302)

# ============ GESTIÓN DE SOLICITUDES ============

@router.get("/solicitudes", response_class=HTMLResponse)
async def lista_solicitudes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario),
    estado: str = None,
    riesgo: str = None,
    distrito: str = None,
    buscar: str = None,
    page: int = 1
):
    """Lista de todas las solicitudes con filtros y paginación"""
    
    try:
        # Consulta base
        query = db.query(Solicitud)
        
        # Aplicar filtros
        if estado:
            query = query.filter(Solicitud.estado == estado)
        if riesgo:
            if riesgo == "alto":
                query = query.filter(Solicitud.nivel_riesgo.in_(["alto", "muy_alto"]))
            else:
                query = query.filter(Solicitud.nivel_riesgo == riesgo)
        if distrito:
            query = query.filter(Solicitud.distrito == distrito)
        if buscar:
            query = query.filter(
                (Solicitud.numero_expediente.contains(buscar)) |
                (Solicitud.nombre_negocio.contains(buscar))
            )
        
        # Total de registros (para paginación)
        total = query.count()
        
        # Paginación (20 por página)
        items_por_pagina = 20
        offset = (page - 1) * items_por_pagina
        solicitudes = query.order_by(Solicitud.created_at.desc()).offset(offset).limit(items_por_pagina).all()
        
        # Cargar relaciones para evitar N+1 queries
        for s in solicitudes:
            db.query(User).filter(User.id == s.usuario_id).first()
            db.query(Rubro).filter(Rubro.id == s.rubro_id).first()
        
        paginas = (total + items_por_pagina - 1) // items_por_pagina
        
        return templates.TemplateResponse(
            "municipal/solicitudes.html",
            {
                "request": request,
                "user": current_user,
                "solicitudes": solicitudes,
                "total_solicitudes": total,
                "pagina_actual": page,
                "paginas": paginas,
                "filtros": {
                    "estado": estado,
                    "riesgo": riesgo,
                    "distrito": distrito,
                    "buscar": buscar
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Error en lista_solicitudes: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/municipal/dashboard", status_code=302)

@router.get("/solicitud/{solicitud_id}", response_class=HTMLResponse)
async def detalle_solicitud(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Detalle de solicitud para funcionarios"""
    
    try:
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Cargar relaciones
        usuario = db.query(User).filter(User.id == solicitud.usuario_id).first()
        rubro = db.query(Rubro).filter(Rubro.id == solicitud.rubro_id).first()
        
        # Verificar si tiene inspecciones
        inspecciones = db.query(Inspeccion).filter(Inspeccion.solicitud_id == solicitud_id).all()
        
        return templates.TemplateResponse(
            "municipal/detalle_solicitud.html",
            {
                "request": request,
                "user": current_user,
                "solicitud": solicitud,
                "usuario": usuario,
                "rubro": rubro,
                "inspecciones": inspecciones
            }
        )
        
    except Exception as e:
        print(f"❌ Error en detalle_solicitud: {e}")
        return RedirectResponse(url="/municipal/solicitudes", status_code=302)

@router.post("/solicitud/{solicitud_id}/emitir")
async def emitir_licencia(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Emitir licencia de funcionamiento"""
    
    try:
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar que la solicitud esté aprobada
        if solicitud.estado not in ["aprobado", "itse_aprobado"]:
            raise HTTPException(status_code=400, detail="La solicitud debe estar aprobada para emitir la licencia")
        
        # Generar número de licencia
        numero_licencia = f"LIC-{datetime.now().strftime('%Y%m%d')}-{solicitud_id:06d}"
        codigo_verificador = str(uuid.uuid4())[:8].upper()
        
        solicitud.estado = "licencia_emitida"
        solicitud.numero_licencia = numero_licencia
        solicitud.fecha_emision = datetime.now()
        solicitud.fecha_vencimiento = datetime.now().replace(year=datetime.now().year + 2)
        solicitud.codigo_verificador = codigo_verificador
        db.commit()
        
        print(f"✅ Licencia emitida: {numero_licencia}")
        
        # Notificar al ciudadano
        try:
            await NotificacionService.notificar_licencia_emitida(db, solicitud.usuario, solicitud)
        except Exception as e:
            print(f"⚠️ Error en notificación: {e}")
        
        return RedirectResponse(url=f"/municipal/solicitud/{solicitud_id}", status_code=302)
        
    except Exception as e:
        print(f"❌ Error emitiendo licencia: {e}")
        db.rollback()
        return RedirectResponse(url=f"/municipal/solicitud/{solicitud_id}", status_code=302)

# ============ REVISIÓN DE SOLICITUDES ============

@router.post("/solicitud/{solicitud_id}/revisar")
async def iniciar_revision(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Cambiar estado a 'en_revision'"""
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if solicitud:
        solicitud.estado = "en_revision"
        db.commit()
        
        # Notificar al ciudadano
        await NotificacionService.notificar_cambio_estado(
            db, 
            solicitud.usuario, 
            solicitud, 
            "en_revision",
            "Su solicitud está siendo revisada por nuestros funcionarios."
        )
    
    return RedirectResponse(url=f"/municipal/solicitud/{solicitud_id}", status_code=302)

@router.post("/solicitud/{solicitud_id}/aprobar")
async def aprobar_solicitud(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Aprobar solicitud"""
    
    form = await request.form()
    comentarios = form.get("comentarios", "")
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if solicitud:
        solicitud.estado = "aprobado"
        db.commit()
        
        # Notificar al ciudadano
        mensaje = f"Su solicitud ha sido APROBADA. {comentarios}"
        await NotificacionService.notificar_cambio_estado(
            db, 
            solicitud.usuario, 
            solicitud, 
            "aprobado",
            mensaje
        )
    
    return RedirectResponse(url="/municipal/solicitudes", status_code=302)

@router.post("/solicitud/{solicitud_id}/rechazar")
async def rechazar_solicitud(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Rechazar solicitud con motivo"""
    
    form = await request.form()
    motivo = form.get("motivo", "Sin especificar")
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if solicitud:
        solicitud.estado = "rechazado"
        solicitud.observaciones_zonificacion = motivo  # Usamos este campo para guardar el motivo
        db.commit()
        
        # Notificar al ciudadano
        mensaje = f"Su solicitud ha sido RECHAZADA. Motivo: {motivo}"
        await NotificacionService.notificar_cambio_estado(
            db, 
            solicitud.usuario, 
            solicitud, 
            "rechazado",
            mensaje
        )
    
    return RedirectResponse(url="/municipal/solicitudes", status_code=302)

# ============ INSPECCIONES ITSE ============

@router.get("/inspecciones", response_class=HTMLResponse)
async def lista_inspecciones(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Lista de todas las inspecciones"""
    
    # Filtros
    estado = request.query_params.get("estado", "todos")
    
    query = db.query(Inspeccion)
    if estado != "todos":
        query = query.filter(Inspeccion.estado == estado)
    
    inspecciones = query.order_by(Inspeccion.fecha_programada).all()
    
    return templates.TemplateResponse(
        "municipal/inspecciones.html",
        {
            "request": request,
            "user": current_user,
            "inspecciones": inspecciones,
            "filtro_actual": estado
        }
    )

@router.get("/inspecciones/programar/{solicitud_id}", response_class=HTMLResponse)
async def programar_inspeccion_form(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Formulario para programar inspección"""
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Obtener inspectores disponibles
    inspectores = db.query(User).filter(User.tipo_usuario == "inspector").all()
    
    return templates.TemplateResponse(
        "municipal/programar_inspeccion.html",
        {
            "request": request,
            "user": current_user,
            "solicitud": solicitud,
            "inspectores": inspectores,
            "fecha_minima": datetime.now().strftime("%Y-%m-%dT%H:%M")
        }
    )

@router.post("/inspecciones/programar/{solicitud_id}")
async def programar_inspeccion(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Guardar programación de inspección"""
    
    form = await request.form()
    fecha_str = form.get("fecha")
    inspector_id = form.get("inspector_id")
    
    fecha = datetime.fromisoformat(fecha_str)
    
    inspeccion = InspeccionService.programar_inspeccion(
        db, 
        solicitud_id, 
        fecha, 
        int(inspector_id) if inspector_id else None
    )
    
    return RedirectResponse(url=f"/municipal/inspeccion/{inspeccion.id}", status_code=302)

@router.get("/inspeccion/{inspeccion_id}", response_class=HTMLResponse)
async def detalle_inspeccion(
    inspeccion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Detalle de una inspección"""
    
    inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    return templates.TemplateResponse(
        "municipal/detalle_inspeccion.html",
        {
            "request": request,
            "user": current_user,
            "inspeccion": inspeccion
        }
    )

@router.get("/inspeccion/{inspeccion_id}/realizar", response_class=HTMLResponse)
async def realizar_inspeccion_form(
    inspeccion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Formulario para realizar inspección"""
    
    inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    # Asignar inspector si no tiene
    if not inspeccion.inspector_id:
        inspeccion.inspector_id = current_user.id
        inspeccion.estado = "en_curso"
        db.commit()
    
    return templates.TemplateResponse(
        "municipal/realizar_inspeccion.html",
        {
            "request": request,
            "user": current_user,
            "inspeccion": inspeccion
        }
    )

@router.post("/inspeccion/{inspeccion_id}/finalizar")
async def finalizar_inspeccion(
    inspeccion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Guardar resultados de la inspección"""
    
    form = await request.form()
    
    datos = {
        "observaciones": form.get("observaciones"),
        "recomendaciones": form.get("recomendaciones"),
        "extintores": form.get("extintores") == "on",
        "luces_emergencia": form.get("luces_emergencia") == "on",
        "señalizacion": form.get("señalizacion") == "on",
        "sistema_electrico": form.get("sistema_electrico") == "on",
        "via_evacuacion": form.get("via_evacuacion") == "on",
    }
    
    inspeccion = InspeccionService.finalizar_inspeccion(db, inspeccion_id, datos)
    
    return RedirectResponse(url=f"/municipal/inspeccion/{inspeccion_id}", status_code=302)

# ============ APROBACIÓN/RECHAZO DE INSPECCIONES ============

@router.post("/inspeccion/{inspeccion_id}/aprobar")
async def aprobar_inspeccion(
    inspeccion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Aprobar una inspección y generar certificado ITSE"""
    
    inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    # Cambiar estado
    inspeccion.estado = "aprobada"
    inspeccion.resultado = "aprobado"
    db.commit()
    
    # Actualizar solicitud
    solicitud = inspeccion.solicitud
    solicitud.itse_aprobado = True
    solicitud.estado = "itse_aprobado"
    db.commit()
    
    # Notificar al ciudadano
    await NotificacionService.notificar_cambio_estado(
        db,
        solicitud.usuario,
        solicitud,
        "itse_aprobado",
        "¡Felicitaciones! Su inspección ITSE ha sido APROBADA. Puede continuar con el trámite de su licencia."
    )
    
    return RedirectResponse(url=f"/municipal/inspeccion/{inspeccion_id}", status_code=302)

@router.post("/inspeccion/{inspeccion_id}/rechazar")
async def rechazar_inspeccion(
    inspeccion_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Rechazar una inspección con motivo"""
    
    form = await request.form()
    motivo = form.get("motivo", "No cumple con los requisitos de seguridad")
    
    inspeccion = db.query(Inspeccion).filter(Inspeccion.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    # Cambiar estado
    inspeccion.estado = "rechazada"
    inspeccion.resultado = "rechazado"
    inspeccion.observaciones = motivo
    db.commit()
    
    # Actualizar solicitud
    solicitud = inspeccion.solicitud
    solicitud.estado = "rechazado"
    solicitud.observaciones_zonificacion = f"INSPECCIÓN RECHAZADA: {motivo}"
    db.commit()
    
    # Notificar al ciudadano
    await NotificacionService.notificar_cambio_estado(
        db,
        solicitud.usuario,
        solicitud,
        "rechazado",
        f"Su inspección ITSE ha sido RECHAZADA. Motivo: {motivo}"
    )
    
    return RedirectResponse(url=f"/municipal/inspeccion/{inspeccion_id}", status_code=302)

# ============ REPORTES Y ESTADÍSTICAS ============

@router.get("/reportes", response_class=HTMLResponse)
async def reportes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario),
    desde: str = None,
    hasta: str = None,
    periodo: str = "mensual"
):
    """Página de reportes y estadísticas"""
    
    # Procesar fechas
    fecha_desde = datetime.strptime(desde, "%Y-%m-%d") if desde else None
    fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d") if hasta else None
    
    # Obtener estadísticas
    stats = ReporteService.get_estadisticas_generales(db, fecha_desde, fecha_hasta)
    
    # VERIFICAR QUE TODAS LAS CLAVES EXISTAN
    # Si falta 'pendientes_pago', la agregamos con valor 0
    if 'pendientes_pago' not in stats:
        stats['pendientes_pago'] = 0
    
    # Datos por mes (para gráficos)
    datos_mensuales = ReporteService.get_solicitudes_por_mes(db)
    
    # Detalle mensual para tabla
    detalle_mensual = ReporteService.get_detalle_mensual(db)
    
    # Datos para gráficos
    riesgo_data = [
        stats.get('riesgo_bajo', 0),
        stats.get('riesgo_medio', 0),
        stats.get('riesgo_alto', 0),
        stats.get('riesgo_muy_alto', 0)
    ]
    
    estados_data = [
        stats.get('pendientes_pago', 0),
        stats.get('pagadas', 0),
        stats.get('aprobadas', 0),
        stats.get('rechazadas', 0),
        stats.get('emitidas', 0)
    ]
    
    # Valores de tendencia (simulados por ahora)
    stats['trend_solicitudes'] = 12
    stats['trend_ingresos'] = 8
    
    # Formatear fechas para el template
    fecha_desde_str = (fecha_desde or datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    fecha_hasta_str = (fecha_hasta or datetime.now()).strftime("%Y-%m-%d")
    
    return templates.TemplateResponse(
        "municipal/reportes.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "meses": json.dumps(datos_mensuales['meses']),
            "solicitudes_data": json.dumps(datos_mensuales['solicitudes']),
            "ingresos_data": json.dumps(datos_mensuales['ingresos']),
            "riesgo_data": json.dumps(riesgo_data),
            "estados_data": json.dumps(estados_data),
            "detalle_mensual": detalle_mensual,
            "fecha_desde": fecha_desde_str,
            "fecha_hasta": fecha_hasta_str,
            "periodo_actual": periodo
        }
    )

@router.get("/reportes/pdf")
async def reportes_pdf(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Exportar reportes a PDF"""
    # Implementar con ReportLab
    return {"mensaje": "Exportar a PDF - En desarrollo"}

@router.get("/reportes/excel")
async def reportes_excel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Exportar reportes a Excel"""
    # Implementar con openpyxl
    return {"mensaje": "Exportar a Excel - En desarrollo"}

# ============ CONFIGURACIÓN Y TABLAS MAESTRAS ============

@router.get("/configuracion", response_class=HTMLResponse)
async def configuracion(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Página de configuración del sistema"""
    
    # Obtener datos para las tablas maestras
    rubros = db.query(Rubro).all()
    tarifas = db.query(Tarifa).all()
    zonas = db.query(Zona).all()
    
    return templates.TemplateResponse(
        "municipal/configuracion.html",
        {
            "request": request,
            "user": current_user,
            "rubros": rubros,
            "tarifas": tarifas,
            "zonas": zonas
        }
    )

# ============ CRUD DE RUBROS ============

@router.post("/configuracion/rubros/crear")
async def crear_rubro(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Crear un nuevo rubro"""
    
    form = await request.form()
    
    nuevo_rubro = Rubro(
        codigo=form.get("codigo"),
        nombre=form.get("nombre"),
        descripcion=form.get("descripcion"),
        nivel_riesgo=form.get("nivel_riesgo"),
        requiere_itse_previa=form.get("requiere_itse_previa") == "on"
    )
    
    db.add(nuevo_rubro)
    db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)

@router.post("/configuracion/rubros/{rubro_id}/editar")
async def editar_rubro(
    rubro_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Editar un rubro existente"""
    
    form = await request.form()
    
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if rubro:
        rubro.codigo = form.get("codigo")
        rubro.nombre = form.get("nombre")
        rubro.descripcion = form.get("descripcion")
        rubro.nivel_riesgo = form.get("nivel_riesgo")
        rubro.requiere_itse_previa = form.get("requiere_itse_previa") == "on"
        db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)

@router.post("/configuracion/rubros/{rubro_id}/eliminar")
async def eliminar_rubro(
    rubro_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Eliminar un rubro (desactivar)"""
    
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if rubro:
        rubro.is_active = False
        db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)

# ============ CRUD DE TARIFAS ============

@router.post("/configuracion/tarifas/crear")
async def crear_tarifa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Crear una nueva tarifa"""
    
    form = await request.form()
    
    nueva_tarifa = Tarifa(
        nivel_riesgo=form.get("nivel_riesgo"),
        monto=float(form.get("monto")),
        descripcion=form.get("descripcion"),
        vigente_desde=datetime.now()
    )
    
    db.add(nueva_tarifa)
    db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)

@router.post("/configuracion/tarifas/{tarifa_id}/editar")
async def editar_tarifa(
    tarifa_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Editar una tarifa existente"""
    
    form = await request.form()
    
    tarifa = db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()
    if tarifa:
        tarifa.monto = float(form.get("monto"))
        tarifa.descripcion = form.get("descripcion")
        db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)

# ============ CRUD DE ZONAS ============

@router.post("/configuracion/zonas/crear")
async def crear_zona(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_funcionario)
):
    """Crear una nueva zona"""
    
    form = await request.form()
    
    nueva_zona = Zona(
        codigo=form.get("codigo"),
        nombre=form.get("nombre"),
        descripcion=form.get("descripcion")
    )
    
    db.add(nueva_zona)
    db.commit()
    
    return RedirectResponse(url="/municipal/configuracion", status_code=302)
# ============ DEMO - ACCESO RÁPIDO ============

@router.get("/demo-login")
async def demo_login(
    request: Request,
    db: Session = Depends(get_db)
):
    """Login automático para demostración"""
    
    try:
        print("🎯 Acceso rápido de demostración")
        
        # Buscar si ya existe el usuario demo
        demo_user = db.query(User).filter(User.email == "demo@funcionario.com").first()
        
        # Si no existe, crearlo
        if not demo_user:
            print("👤 Creando usuario de demostración...")
            demo_user = User(
                email="demo@funcionario.com",
                password_hash=get_password_hash("demo123"),
                telefono="999888777",
                tipo_usuario="funcionario",
                tipo_persona="natural",
                nombres="Usuario",
                apellido_paterno="Demostración",
                dni="12345678",
                direccion="Palacio Municipal",
                distrito="Ica",
                cargo="Administrador Demo",
                area="Desarrollo Económico",
                is_active=True,
                is_verified=True,
                created_at=datetime.now()
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("✅ Usuario demo creado")
        else:
            print("✅ Usuario demo ya existía")
        
        # Crear token de acceso
        access_token = create_access_token({
            "sub": demo_user.email,
            "user_id": demo_user.id,
            "tipo": demo_user.tipo_usuario
        })
        
        print(f"🔑 Token generado para: {demo_user.email}")
        
        # Redirigir al dashboard
        response = RedirectResponse(url="/municipal/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            path="/",
            max_age=86400
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Error en demo-login: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/municipal/login", status_code=302)
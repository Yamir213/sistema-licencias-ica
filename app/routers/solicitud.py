from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import os
import json

from app.database.connection import get_db
from app.utils.dependencies import get_current_user, get_current_funcionario
from app.models.user import User
from app.models.solicitud import Solicitud
from app.models.config import Rubro, Tarifa, Zona
from app.services.riesgo_service import RiesgoService
from app.services.zonificacion_service import ZonificacionService
from app.services.notificacion_service import NotificacionService
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/solicitud", tags=["Solicitud de Licencia"])
templates = Jinja2Templates(directory="app/templates")

# Almacenamiento temporal para el formulario multipaso
temp_storage = {}

# ============ PASO 1: CLASIFICACIÓN DE RIESGO ============

@router.get("/paso1", response_class=HTMLResponse)
async def paso1_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 1: Selección de rubro y clasificación de riesgo"""
    
    print(f"📋 Accediendo a paso 1 - Usuario: {current_user.email}")
    
    # Obtener lista de rubros
    rubros = db.query(Rubro).filter(Rubro.is_active == True).all()
    
    # Inicializar sesión temporal
    session_id = str(uuid.uuid4())
    temp_storage[session_id] = {
        "user_id": current_user.id,
        "paso": 1
    }
    
    response = templates.TemplateResponse(
        "solicitud/paso1_riesgo.html",
        {
            "request": request,
            "rubros": rubros,
            "session_id": session_id,
            "user": current_user
        }
    )
    response.set_cookie(key="solicitud_session", value=session_id, path="/")
    return response

@router.post("/paso1")
async def paso1_procesar(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Procesar paso 1 y redirigir a paso 2"""
    
    try:
        print(f"📝 Procesando paso 1 - Usuario: {current_user.email}")
        
        form = await request.form()
        session_id = form.get("session_id")
        rubro_id = form.get("rubro_id")
        
        print(f"   Session ID: {session_id}")
        print(f"   Rubro ID: {rubro_id}")
        
        # Validar sesión
        if not session_id:
            session_id = str(uuid.uuid4())
            temp_storage[session_id] = {"user_id": current_user.id, "paso": 1}
        
        if session_id not in temp_storage:
            temp_storage[session_id] = {"user_id": current_user.id, "paso": 1}
        
        # Obtener rubro
        rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
        if not rubro:
            print("❌ Rubro no encontrado")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Clasificar riesgo
        clasificacion = RiesgoService.clasificar_riesgo(rubro.nombre)
        
        # Guardar en sesión
        temp_storage[session_id].update({
            "paso": 2,
            "rubro_id": rubro.id,
            "rubro_nombre": rubro.nombre,
            "nivel_riesgo": clasificacion["nivel_riesgo"],
            "requiere_itse_previa": clasificacion["requiere_itse_previa"],
            "monto": clasificacion["monto"],
            "anexos_requeridos": RiesgoService.get_anexos_requeridos(clasificacion["nivel_riesgo"])
        })
        
        print(f"✅ Paso 1 completado - Riesgo: {clasificacion['nivel_riesgo']}")
        
        # Redirigir a paso 2 con la cookie
        response = RedirectResponse(url="/solicitud/paso2", status_code=302)
        response.set_cookie(key="solicitud_session", value=session_id, path="/")
        return response
        
    except Exception as e:
        print(f"❌ Error en paso1_procesar: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso1", status_code=302)

# ============ PASO 2: DATOS DEL NEGOCIO ============

@router.get("/paso2", response_class=HTMLResponse)
async def paso2_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 2: Datos del negocio"""
    
    try:
        print(f"📋 Accediendo a paso 2 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        print(f"   Session ID: {session_id}")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar que el usuario sea el mismo
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        return templates.TemplateResponse(
            "solicitud/paso2_documentos.html",
            {
                "request": request,
                "session_id": session_id,
                "user": current_user,
                "data": data
            }
        )
        
    except Exception as e:
        print(f"❌ Error en paso2_form: {e}")
        return RedirectResponse(url="/solicitud/paso1", status_code=302)

@router.post("/paso2")
async def paso2_procesar(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Procesar paso 2 y redirigir a paso 3"""
    
    try:
        form = await request.form()
        session_id = form.get("session_id")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en POST paso2")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Guardar datos del negocio
        temp_storage[session_id].update({
            "paso": 3,
            "nombre_negocio": form.get("nombre_negocio"),
            "direccion_negocio": form.get("direccion_negocio"),
            "referencia": form.get("referencia"),
            "distrito": form.get("distrito"),
            "area_local": form.get("area_local"),
            "telefono_contacto": form.get("telefono_contacto")
        })
        
        print(f"✅ Paso 2 completado - Negocio: {form.get('nombre_negocio')}")
        print(f"➡️ Redirigiendo a paso 3")
        
        response = RedirectResponse(url="/solicitud/paso3", status_code=302)
        response.set_cookie(key="solicitud_session", value=session_id, path="/")
        return response
        
    except Exception as e:
        print(f"❌ Error en paso2_procesar: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso2", status_code=302)

# ============ PASO 3: ZONIFICACIÓN Y COMPATIBILIDAD ============

@router.get("/paso3", response_class=HTMLResponse)
async def paso3_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 3: Evaluación de zonificación"""
    
    try:
        print(f"📍 Accediendo a paso 3 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        print(f"   Session ID: {session_id}")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en paso 3")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar que el usuario sea el mismo
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Verificar que tenga los datos del paso 2
        if "nombre_negocio" not in data:
            print("❌ No hay datos del paso 2")
            return RedirectResponse(url="/solicitud/paso2", status_code=302)
        
        # Evaluar compatibilidad de zonificación
        evaluacion = ZonificacionService.evaluar_compatibilidad(
            rubro=data["rubro_nombre"],
            distrito=data.get("distrito", "Ica"),
            direccion=data.get("direccion_negocio", "")
        )
        
        temp_storage[session_id]["evaluacion_zonificacion"] = evaluacion
        
        print(f"✅ Paso 3 cargado - Compatible: {evaluacion['compatible']}")
        
        return templates.TemplateResponse(
            "solicitud/paso3_zonificacion.html",
            {
                "request": request,
                "session_id": session_id,
                "user": current_user,
                "data": data,
                "evaluacion": evaluacion,
                "now": datetime.now
            }
        )
        
    except Exception as e:
        print(f"❌ Error en paso3_form: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso2", status_code=302)

@router.post("/paso3")
async def paso3_procesar(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Procesar paso 3 y redirigir a paso 4"""
    
    try:
        print(f"📝 Procesando paso 3 - Usuario: {current_user.email}")
        
        form = await request.form()
        session_id = form.get("session_id")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en POST paso 3")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Guardar aceptación de condiciones
        temp_storage[session_id].update({
            "paso": 4,
            "acepta_condiciones": form.get("acepta_condiciones") == "on",
            "declaracion_1": form.get("declaracion_1") == "on",
            "declaracion_2": form.get("declaracion_2") == "on",
            "declaracion_3": form.get("declaracion_3") == "on"
        })
        
        print(f"✅ Paso 3 completado - Condiciones aceptadas")
        print(f"➡️ Redirigiendo a paso 4")
        
        response = RedirectResponse(url="/solicitud/paso4", status_code=302)
        response.set_cookie(key="solicitud_session", value=session_id, path="/")
        return response
        
    except Exception as e:
        print(f"❌ Error en paso3_procesar: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso3", status_code=302)
    # ============ PASO 4: REVISIÓN Y CONFIRMACIÓN ============

@router.get("/paso4", response_class=HTMLResponse)
async def paso4_revision(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 4: Revisión de datos antes del pago"""
    
    try:
        print(f"🔍 Accediendo a paso 4 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        print(f"   Session ID: {session_id}")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en paso 4")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Verificar que tenga todos los datos necesarios
        if "nombre_negocio" not in data or "evaluacion_zonificacion" not in data:
            print("❌ Faltan datos requeridos")
            return RedirectResponse(url="/solicitud/paso2", status_code=302)
        
        print(f"✅ Paso 4 cargado - Todo listo para pago")
        
        return templates.TemplateResponse(
            "solicitud/paso4_revision.html",
            {
                "request": request,
                "session_id": session_id,
                "user": current_user,
                "data": data
            }
        )
        
    except Exception as e:
        print(f"❌ Error en paso4_revision: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso3", status_code=302)

@router.post("/paso4")
async def paso4_confirmar(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirmar datos y crear solicitud"""
    
    try:
        print(f"📝 Confirmando paso 4 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en POST paso 4")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Crear número de expediente
        numero_expediente = f"EXP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Crear solicitud en base de datos
        nueva_solicitud = Solicitud(
            numero_expediente=numero_expediente,
            usuario_id=data["user_id"],
            nombre_negocio=data["nombre_negocio"],
            rubro_id=data["rubro_id"],
            direccion_negocio=data["direccion_negocio"],
            referencia=data.get("referencia"),
            distrito=data.get("distrito", "Ica"),
            latitud=data.get("latitud"),
            longitud=data.get("longitud"),
            nivel_riesgo=data["nivel_riesgo"],
            estado="pendiente_pago",
            requiere_itse_previa=data["requiere_itse_previa"],
            monto_pago=data["monto"],
            compatible_zonificacion=data.get("evaluacion_zonificacion", {}).get("compatible", True)
        )
        
        db.add(nueva_solicitud)
        db.commit()
        db.refresh(nueva_solicitud)
        
        print(f"✅ Solicitud creada - Expediente: {numero_expediente}")
        
        # Actualizar sesión
        temp_storage[session_id].update({
            "paso": 5,
            "solicitud_id": nueva_solicitud.id,
            "numero_expediente": numero_expediente
        })
        
        print(f"➡️ Redirigiendo a paso 5")
        
        response = RedirectResponse(url="/solicitud/paso5", status_code=302)
        response.set_cookie(key="solicitud_session", value=session_id, path="/")
        return response
        
    except Exception as e:
        print(f"❌ Error en paso4_confirmar: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso4", status_code=302)

# ============ PASO 5: PAGO EN LÍNEA ============

@router.get("/paso5", response_class=HTMLResponse)
async def paso5_pago(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 5: Pago en línea"""
    
    try:
        print(f"💳 Accediendo a paso 5 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en paso 5")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # Verificar que tenga solicitud creada
        if "solicitud_id" not in data:
            print("❌ No hay solicitud creada")
            return RedirectResponse(url="/solicitud/paso4", status_code=302)
        
        print(f"✅ Paso 5 cargado - Monto: S/ {data['monto']}")
        
        return templates.TemplateResponse(
            "solicitud/paso5_pago.html",
            {
                "request": request,
                "session_id": session_id,
                "user": current_user,
                "data": data
            }
        )
        
    except Exception as e:
        print(f"❌ Error en paso5_pago: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso4", status_code=302)

@router.post("/paso5/procesar_pago")
async def procesar_pago(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simular procesamiento de pago"""
    
    try:
        print(f"💰 Procesando pago - Usuario: {current_user.email}")
        
        form = await request.form()
        session_id = form.get("session_id")
        metodo_pago = form.get("metodo_pago")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en pago")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        # SIMULACIÓN DE PAGO EXITOSO
        solicitud = db.query(Solicitud).filter(Solicitud.id == data["solicitud_id"]).first()
        
        if solicitud:
            solicitud.estado = "pagado"
            solicitud.fecha_pago = datetime.now()
            solicitud.metodo_pago = metodo_pago
            solicitud.comprobante_pago = f"PAGO-{datetime.now().strftime('%Y%m%d')}-{session_id[:8].upper()}"
            db.commit()
            
            print(f"✅ Pago registrado - Solicitud ID: {solicitud.id}")
            
            # Enviar notificación de pago
            try:
                await NotificacionService.notificar_pago_confirmado(db, current_user, solicitud)
                print(f"📧 Notificación de pago enviada")
            except Exception as e:
                print(f"⚠️ Error en notificación: {e}")
        
        # Actualizar sesión
        temp_storage[session_id].update({
            "paso": 6,
            "pago_exitoso": True,
            "codigo_pago": f"P{session_id[:8].upper()}",
            "metodo_pago": metodo_pago,
            "fecha_pago": datetime.now().strftime('%d/%m/%Y')
        })
        
        print(f"✅ Pago completado exitosamente")
        print(f"➡️ Redirigiendo a paso 6")
        
        response = RedirectResponse(url="/solicitud/paso6", status_code=302)
        response.set_cookie(key="solicitud_session", value=session_id, path="/")
        return response
        
    except Exception as e:
        print(f"❌ Error en procesar_pago: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso5", status_code=302)

# ============ PASO 6: CONFIRMACIÓN Y SEGUIMIENTO ============

@router.get("/paso6", response_class=HTMLResponse)
async def paso6_confirmacion(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Paso 6: Confirmación final y seguimiento"""
    
    try:
        print(f"🎉 Accediendo a paso 6 - Usuario: {current_user.email}")
        
        session_id = request.cookies.get("solicitud_session")
        
        if not session_id or session_id not in temp_storage:
            print("❌ Sesión no encontrada en paso 6")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        data = temp_storage[session_id]
        
        # Verificar usuario
        if data.get("user_id") != current_user.id:
            print("❌ Usuario no coincide con la sesión")
            return RedirectResponse(url="/solicitud/paso1", status_code=302)
        
        print(f"✅ Paso 6 cargado - Trámite completado")
        
        return templates.TemplateResponse(
            "solicitud/paso6_confirmacion.html",
            {
                "request": request,
                "session_id": session_id,
                "user": current_user,
                "data": data,
                "now": datetime.now
            }
        )
        
    except Exception as e:
        print(f"❌ Error en paso6_confirmacion: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/solicitud/paso5", status_code=302)

# ============ DESCARGA DE LICENCIA ============

@router.get("/licencia/{solicitud_id}/descargar")
async def descargar_licencia(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Descargar licencia de funcionamiento en PDF"""
    
    try:
        print(f"📄 Descargando licencia - Solicitud ID: {solicitud_id}")
        
        # Buscar solicitud
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar que la licencia esté emitida
        if solicitud.estado != "licencia_emitida":
            raise HTTPException(status_code=400, detail="La licencia aún no ha sido emitida")
        
        # Obtener datos relacionados
        usuario = db.query(User).filter(User.id == solicitud.usuario_id).first()
        rubro = db.query(Rubro).filter(Rubro.id == solicitud.rubro_id).first()
        
        # Generar PDF
        pdf_buffer = PDFService.generar_licencia(solicitud, usuario, rubro)
        
        # Nombre del archivo
        filename = f"licencia_{solicitud.numero_licencia}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error descargando licencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

# ============ EMITIR LICENCIA (SOLO FUNCIONARIOS) ============

@router.post("/admin/solicitud/{solicitud_id}/emitir-licencia")
async def emitir_licencia(
    solicitud_id: int,
    db: Session = Depends(get_db),
    funcionario: User = Depends(get_current_funcionario)
):
    """Emitir licencia de funcionamiento (solo funcionarios)"""
    
    try:
        print(f"🏛️ Emitiendo licencia - Funcionario: {funcionario.email}")
        
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Generar número de licencia
        numero_licencia = f"LIC-{datetime.now().strftime('%Y%m%d')}-{solicitud_id:06d}"
        
        # Generar código verificador
        codigo_verificador = str(uuid.uuid4())[:8].upper()
        
        # Actualizar solicitud
        solicitud.estado = "licencia_emitida"
        solicitud.numero_licencia = numero_licencia
        solicitud.fecha_emision = datetime.now()
        solicitud.fecha_vencimiento = datetime.now() + timedelta(days=365*2)  # 2 años
        solicitud.codigo_verificador = codigo_verificador
        
        db.commit()
        
        print(f"✅ Licencia emitida - N°: {numero_licencia}")
        
        # Enviar notificación
        try:
            user = db.query(User).filter(User.id == solicitud.usuario_id).first()
            await NotificacionService.notificar_licencia_emitida(db, user, solicitud)
            print(f"📧 Notificación de licencia enviada")
        except Exception as e:
            print(f"⚠️ Error en notificación: {e}")
        
        return {
            "message": "Licencia emitida exitosamente",
            "numero_licencia": numero_licencia,
            "codigo_verificador": codigo_verificador
        }
        
    except Exception as e:
        print(f"❌ Error emitiendo licencia: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al emitir licencia: {str(e)}")

# ============ LIMPIAR SESIÓN ============

@router.get("/limpiar-sesion")
async def limpiar_sesion(request: Request):
    """Limpiar sesión después de completar trámite"""
    
    session_id = request.cookies.get("solicitud_session")
    if session_id and session_id in temp_storage:
        del temp_storage[session_id]
        print(f"🧹 Sesión eliminada: {session_id}")
    
    response = RedirectResponse(url="/portal/dashboard", status_code=302)
    response.delete_cookie("solicitud_session", path="/")
    return response

# ============ VER ESTADO DE SOLICITUD ============

@router.get("/estado/{solicitud_id}")
async def ver_estado_solicitud(
    solicitud_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ver estado detallado de una solicitud"""
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    # Verificar que el usuario sea el propietario o funcionario
    if solicitud.usuario_id != current_user.id and current_user.tipo_usuario not in ["funcionario", "administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    rubro = db.query(Rubro).filter(Rubro.id == solicitud.rubro_id).first()
    
    return templates.TemplateResponse(
        "solicitud/estado_solicitud.html",
        {
            "request": request,
            "solicitud": solicitud,
            "rubro": rubro,
            "user": current_user
        }
    )
# ============ VOUCHER DE PAGO ============

@router.get("/pago/{pago_id}/voucher")
async def descargar_voucher(
    pago_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Descargar voucher de pago en PDF"""
    
    try:
        from app.models.pago import Pago
        from app.services.voucher_service import VoucherService
        
        # Buscar pago
        pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        # Buscar solicitud
        solicitud = db.query(Solicitud).filter(Solicitud.id == pago.solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar autorización
        if solicitud.usuario_id != current_user.id and current_user.tipo_usuario not in ["funcionario", "administrador"]:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Generar voucher
        pdf_buffer = VoucherService.generar_voucher(solicitud, current_user, pago)
        
        filename = f"voucher_{pago.codigo_pago}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error generando voucher: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar voucher: {str(e)}")

# ============ CONSTANCIA DE TRÁMITE ============

@router.get("/solicitud/{solicitud_id}/constancia")
async def descargar_constancia(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Descargar constancia de trámite en PDF"""
    
    try:
        solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        if solicitud.usuario_id != current_user.id and current_user.tipo_usuario not in ["funcionario", "administrador"]:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Generar constancia simple (por ahora)
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("CONSTANCIA DE TRÁMITE", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Expediente: {solicitud.numero_expediente}", styles['Normal']))
        story.append(Paragraph(f"Fecha: {solicitud.created_at.strftime('%d/%m/%Y')}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=constancia_{solicitud.numero_expediente}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar constancia: {str(e)}")

# ============ LISTAR DOCUMENTOS DE SOLICITUD ============

@router.get("/solicitud/{solicitud_id}/documentos")
async def listar_documentos(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos los documentos de una solicitud"""
    
    from app.models.documento import Documento
    
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    if solicitud.usuario_id != current_user.id and current_user.tipo_usuario not in ["funcionario", "administrador"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    documentos = db.query(Documento).filter(Documento.solicitud_id == solicitud_id).all()
    pagos = db.query(Pago).filter(Pago.solicitud_id == solicitud_id).all()
    
    return {
        "solicitud": solicitud.numero_expediente,
        "documentos_subidos": [
            {
                "id": d.id,
                "tipo": d.tipo,
                "nombre": d.nombre_original,
                "fecha": d.created_at,
                "validado": d.esta_validado
            } for d in documentos
        ],
        "pagos": [
            {
                "id": p.id,
                "codigo": p.codigo_pago,
                "monto": p.monto,
                "fecha": p.fecha_transaccion,
                "comprobante": p.comprobante_numero
            } for p in pagos if p.estado == "completado"
        ]
    }
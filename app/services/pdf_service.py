from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from io import BytesIO
from datetime import datetime
import os

class PDFService:
    """Servicio para generar licencias de funcionamiento en PDF"""
    
    @staticmethod
    def generar_licencia(solicitud, usuario, rubro):
        """
        Genera PDF de licencia de funcionamiento
        Retorna: BytesIO con el PDF generado
        """
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        # Contenido del PDF
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para títulos
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Centrado
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # ========== ENCABEZADO ==========
        # Título
        story.append(Paragraph("MUNICIPALIDAD PROVINCIAL DE ICA", styles['TituloPrincipal']))
        story.append(Paragraph("Gerencia de Desarrollo Económico", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # LICENCIA DE FUNCIONAMIENTO
        story.append(Paragraph(
            f"LICENCIA DE FUNCIONAMIENTO N° {solicitud.numero_licencia or '---'}",
            styles['Heading1']
        ))
        story.append(Spacer(1, 30))
        
        # ========== DATOS DEL TITULAR ==========
        data = []
        
        # Encabezado de sección
        story.append(Paragraph("DATOS DEL TITULAR", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Tabla de datos
        if usuario.tipo_persona == "natural":
            data = [
                ["Tipo de persona:", "Natural"],
                ["DNI:", usuario.dni or "---"],
                ["Nombres:", usuario.nombres or "---"],
                ["Apellidos:", f"{usuario.apellido_paterno or ''} {usuario.apellido_materno or ''}"],
                ["Dirección:", usuario.direccion or "---"],
                ["Distrito:", usuario.distrito or "Ica"],
            ]
        else:
            data = [
                ["Tipo de persona:", "Jurídica"],
                ["RUC:", usuario.ruc or "---"],
                ["Razón Social:", usuario.razon_social or "---"],
                ["Nombre Comercial:", usuario.nombre_comercial or "---"],
                ["Representante Legal:", usuario.representante_legal or "---"],
                ["Dirección:", usuario.direccion or "---"],
                ["Distrito:", usuario.distrito or "Ica"],
            ]
        
        # Crear tabla
        t = Table(data, colWidths=[120, 300])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # ========== DATOS DEL ESTABLECIMIENTO ==========
        story.append(Paragraph("DATOS DEL ESTABLECIMIENTO", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        data_est = [
            ["Nombre del Negocio:", solicitud.nombre_negocio],
            ["Rubro:", rubro.nombre],
            ["Nivel de Riesgo:", rubro.nivel_riesgo.upper()],
            ["Dirección:", solicitud.direccion_negocio],
            ["Referencia:", solicitud.referencia or "---"],
            ["Distrito:", solicitud.distrito],
        ]
        
        t_est = Table(data_est, colWidths=[120, 300])
        t_est.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_est)
        story.append(Spacer(1, 20))
        
        # ========== VIGENCIA ==========
        story.append(Paragraph("VIGENCIA", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        data_vig = [
            ["Fecha de Emisión:", solicitud.fecha_emision.strftime('%d/%m/%Y')],
            ["Fecha de Vencimiento:", solicitud.fecha_vencimiento.strftime('%d/%m/%Y')],
            ["Código Verificador:", solicitud.codigo_verificador],
        ]
        
        t_vig = Table(data_vig, colWidths=[120, 300])
        t_vig.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_vig)
        story.append(Spacer(1, 30))
        
        # ========== GENERAR QR ==========
        qr_data = f"""
        Licencia de Funcionamiento
        N°: {solicitud.numero_licencia}
        Negocio: {solicitud.nombre_negocio}
        Titular: {usuario.nombre_completo()}
        Emisión: {solicitud.fecha_emision.strftime('%d/%m/%Y')}
        Verificar en: https://licencias.muniica.gob.pe/verificar/{solicitud.codigo_verificador}
        """
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir QR a BytesIO
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Agregar QR al PDF
        qr_image = Image(qr_buffer, width=1.5*inch, height=1.5*inch)
        story.append(qr_image)
        story.append(Spacer(1, 10))
        
        # ========== FIRMAS ==========
        story.append(Paragraph("FIRMA DIGITAL", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("__________________________________", styles['Normal']))
        story.append(Paragraph("Gerente de Desarrollo Económico", styles['Normal']))
        story.append(Paragraph("Municipalidad Provincial de Ica", styles['Normal']))
        story.append(Spacer(1, 30))
        
        story.append(Paragraph(
            "Documento emitido electrónicamente con validez legal según Ley N° 28976",
            styles['Italic']
        ))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
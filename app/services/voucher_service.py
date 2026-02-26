from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import qrcode

class VoucherService:
    """Servicio para generar vouchers de pago"""
    
    @staticmethod
    def generar_voucher(solicitud, usuario, pago):
        """
        Genera voucher de pago en PDF
        """
        buffer = BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado
        styles.add(ParagraphStyle(
            name='TituloVoucher',
            parent=styles['Heading1'],
            fontSize=20,
            alignment=1,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        # Título
        story.append(Paragraph("MUNICIPALIDAD PROVINCIAL DE ICA", styles['TituloVoucher']))
        story.append(Paragraph("VOUCHER DE PAGO ELECTRÓNICO", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Datos del voucher
        data = [
            ["N° de Operación:", pago.codigo_pago],
            ["Fecha y Hora:", datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            [" "],
            ["DATOS DEL CONTRIBUYENTE"],
            [" "],
            ["Tipo:", "Persona Natural" if usuario.tipo_persona == "natural" else "Persona Jurídica"],
            ["Documento:", usuario.dni or usuario.ruc or "---"],
            ["Nombre/Razón Social:", usuario.nombre_completo() or usuario.razon_social or usuario.email],
            [" "],
            ["DATOS DEL PAGO"],
            [" "],
            ["Concepto:", f"Licencia de Funcionamiento - {solicitud.nombre_negocio}"],
            ["N° Expediente:", solicitud.numero_expediente],
            ["Rubro:", solicitud.nombre_negocio],
            ["Nivel de Riesgo:", solicitud.nivel_riesgo.upper()],
            ["Monto:", f"S/ {pago.monto:.2f}"],
            ["Método de Pago:", pago.metodo_pago.upper() if pago.metodo_pago else "CULQI"],
            ["Estado:", "PAGADO"],
        ]
        
        # Crear tabla
        t = Table(data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('SPAN', (0,3), (1,3)),
            ('SPAN', (0,4), (1,4)),
            ('SPAN', (0,9), (1,9)),
            ('SPAN', (0,10), (1,10)),
            ('BACKGROUND', (0,3), (1,3), colors.lightgrey),
            ('BACKGROUND', (0,9), (1,9), colors.lightgrey),
            ('FONTWEIGHT', (0,3), (1,3), 'BOLD'),
            ('FONTWEIGHT', (0,9), (1,9), 'BOLD'),
            ('ALIGN', (1,13), (1,13), 'RIGHT'),
            ('FONTSIZE', (1,13), (1,13), 14),
            ('FONTWEIGHT', (1,13), (1,13), 'BOLD'),
            ('TEXTCOLOR', (1,13), (1,13), colors.HexColor('#27ae60')),
        ]))
        story.append(t)
        story.append(Spacer(1, 30))
        
        # Generar código QR
        qr_data = f"""
        COMPROBANTE DE PAGO
        Código: {pago.codigo_pago}
        Fecha: {datetime.now().strftime('%d/%m/%Y')}
        Monto: S/ {pago.monto:.2f}
        Expediente: {solicitud.numero_expediente}
        """
        
        qr = qrcode.QRCode(version=1, box_size=8, border=3)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = Image(qr_buffer, width=1.5*inch, height=1.5*inch)
        story.append(qr_image)
        story.append(Spacer(1, 20))
        
        # Texto legal
        story.append(Paragraph(
            "Este voucher es válido como comprobante de pago. "
            "Puede ser verificado en el portal de la Municipalidad Provincial de Ica.",
            styles['Italic']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
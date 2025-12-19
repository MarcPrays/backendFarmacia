"""
Generador de facturas en PDF
Genera facturas con formato profesional similar a la imagen proporcionada
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List, Optional
import os


def generate_invoice_pdf(sale_data: Dict[str, Any], pharmacy_info: Dict[str, Any] = None) -> bytes:
    """
    Genera un PDF de factura con todos los detalles de la venta
    
    Args:
        sale_data: Datos de la venta con cliente, productos, totales, etc.
        pharmacy_info: Información de la farmacia (nombre, dirección, logo, etc.)
    
    Returns:
        bytes: Contenido del PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Información de la farmacia (valores por defecto)
    pharmacy_name = pharmacy_info.get('name', 'Sistema Farmacia') if pharmacy_info else 'Sistema Farmacia'
    pharmacy_address = pharmacy_info.get('address', 'Dirección de la farmacia') if pharmacy_info else 'Dirección de la farmacia'
    pharmacy_logo_path = pharmacy_info.get('logo_path', None) if pharmacy_info else None
    
    # Header con logo y nombre de la farmacia
    header_data = []
    
    # Logo (si existe)
    if pharmacy_logo_path and os.path.exists(pharmacy_logo_path):
        try:
            logo = Image(pharmacy_logo_path, width=1.5*inch, height=1.5*inch)
            header_data.append(logo)
        except:
            header_data.append(Paragraph("", styles['Normal']))
    else:
        header_data.append(Paragraph("", styles['Normal']))
    
    # Nombre y dirección de la farmacia
    pharmacy_style = ParagraphStyle(
        'PharmacyName',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    address_style = ParagraphStyle(
        'PharmacyAddress',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_LEFT
    )
    
    pharmacy_info_text = Paragraph(pharmacy_name, pharmacy_style)
    pharmacy_address_text = Paragraph(pharmacy_address, address_style)
    
    header_table = Table([[header_data[0] if header_data else "", pharmacy_info_text, pharmacy_address_text]], 
                        colWidths=[2*inch, 3*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de facturación y envío
    client_name = sale_data.get('client_name', 'N/A')
    client_address = sale_data.get('client_address', 'N/A')
    client_phone = sale_data.get('client_phone', 'N/A')
    
    invoice_number = f"FAC-{sale_data.get('id', '0000'):04d}"
    sale_date = sale_data.get('sale_date', datetime.now())
    if isinstance(sale_date, str):
        sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
    
    # Formatear fecha
    formatted_date = sale_date.strftime("%d/%m/%Y")
    formatted_time = sale_date.strftime("%H:%M")
    
    billing_data = [
        ['FACTURAR A:', 'ENVIAR A:', 'N° DE FACTURA:'],
        [Paragraph(f"<b>{client_name}</b><br/>{client_address}<br/>Tel: {client_phone}", styles['Normal']),
         Paragraph(f"<b>{client_name}</b><br/>{client_address}<br/>Tel: {client_phone}", styles['Normal']),
         Paragraph(f"<b>{invoice_number}</b>", styles['Normal'])],
        ['', '', f'FECHA: {formatted_date}'],
        ['', '', f'HORA: {formatted_time}'],
    ]
    
    billing_table = Table(billing_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    billing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(billing_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de productos
    details = sale_data.get('details', [])
    
    products_data = [
        ['CANT.', 'DESCRIPCIÓN', 'PRECIO UNITARIO', 'IMPORTE']
    ]
    
    for detail in details:
        product_name = detail.get('product_name', 'N/A')
        product_presentation = detail.get('product_presentation', '')
        product_concentration = detail.get('product_concentration', '')
        
        description = f"{product_name}"
        if product_presentation:
            description += f" {product_presentation}"
        if product_concentration:
            description += f" {product_concentration}"
        
        quantity = detail.get('quantity', 0)
        unit_price = detail.get('unit_price', 0)
        subtotal = detail.get('subtotal', 0)
        
        products_data.append([
            str(quantity),
            description,
            f"${float(unit_price):,.2f}",
            f"${float(subtotal):,.2f}"
        ])
    
    products_table = Table(products_data, colWidths=[0.8*inch, 4*inch, 1.5*inch, 1.2*inch])
    products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # CANT. centrado
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # DESCRIPCIÓN izquierda
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # PRECIO UNITARIO derecha
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # IMPORTE derecha
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
    ]))
    
    elements.append(products_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Totales
    subtotal = sale_data.get('subtotal', sale_data.get('total', 0))
    tax_rate = sale_data.get('tax_rate', 0.21)  # IVA 21% por defecto
    tax_amount = float(subtotal) * tax_rate
    total = float(subtotal) + tax_amount
    
    totals_data = [
        ['Subtotal:', f"${float(subtotal):,.2f}"],
        [f'IVA {tax_rate*100:.1f}%:', f"${tax_amount:,.2f}"],
        ['Total Factura:', f"${total:,.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTSIZE', (0, 2), (1, 2), 14),  # Total más grande
        ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#4472C4')),
    ]))
    
    # Alinear a la derecha
    totals_wrapper = Table([['', totals_table]], colWidths=[4.5*inch, 2*inch])
    totals_wrapper.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    
    elements.append(totals_wrapper)
    elements.append(Spacer(1, 0.3*inch))
    
    # Condiciones y forma de pago
    payment_method = sale_data.get('payment_method', 'N/A')
    
    conditions_style = ParagraphStyle(
        'Conditions',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        alignment=TA_LEFT
    )
    
    conditions_text = f"""
    <b>CONDICIONES Y FORMA DE PAGO:</b><br/>
    Método de pago: {payment_method}<br/>
    El pago se realizará según el método seleccionado.<br/>
    <br/>
    <b>Gracias por su compra!</b>
    """
    
    elements.append(Paragraph(conditions_text, conditions_style))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener bytes del PDF
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    # Verificar que el PDF tenga la signatura correcta
    if not pdf_bytes.startswith(b'%PDF'):
        raise ValueError("El PDF generado no tiene la signatura correcta")
    
    return pdf_bytes



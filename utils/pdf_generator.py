"""
Generador de PDFs usando reportlab
Genera PDFs con formato tipo Excel/tabla
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List


def generate_sales_report_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    Genera un PDF del reporte de ventas con formato tipo Excel/tabla
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Contenedor para elementos del PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    # Título del reporte
    elements.append(Paragraph("REPORTE DE VENTAS", title_style))
    
    # Información del período
    period_text = ""
    if report_data.get('start_date'):
        period_text += f"Desde: {report_data['start_date']}"
    if report_data.get('end_date'):
        if period_text:
            period_text += " | "
        period_text += f"Hasta: {report_data['end_date']}"
    if not period_text:
        period_text = "Período: Todos los registros"
    
    elements.append(Paragraph(period_text, subtitle_style))
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de resumen
    summary_data = [
        ['RESUMEN GENERAL', ''],
        ['Total de Ventas', str(report_data.get('total_sales', 0))],
        ['Total Vendido', f"${report_data.get('total_amount', 0):,.2f}"],
        ['Total de Items', str(report_data.get('total_items', 0))],
        ['Promedio por Venta', f"${report_data.get('average_sale', 0):,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E7E6E6')])
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de métodos de pago
    if report_data.get('payment_methods'):
        payment_data = [['MÉTODO DE PAGO', 'CANTIDAD', 'TOTAL']]
        for method, data in report_data['payment_methods'].items():
            payment_data.append([
                method,
                str(data.get('count', 0)),
                f"${data.get('total', 0):,.2f}"
            ])
        
        payment_table = Table(payment_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E2EFDA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')])
        ]))
        
        elements.append(Paragraph("Métodos de Pago", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(payment_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de ventas diarias
    if report_data.get('daily_sales'):
        daily_data = [['FECHA', 'CANTIDAD', 'TOTAL']]
        for date, data in list(report_data['daily_sales'].items())[:30]:  # Limitar a 30 días
            daily_data.append([
                date,
                str(data.get('count', 0)),
                f"${data.get('total', 0):,.2f}"
            ])
        
        daily_table = Table(daily_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        daily_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFC000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF2CC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')])
        ]))
        
        elements.append(Paragraph("Ventas por Día", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(daily_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Tabla detallada de ventas (primeras 50)
    if report_data.get('sales'):
        sales_data = [['ID', 'FECHA', 'CLIENTE', 'MÉTODO', 'ITEMS', 'TOTAL']]
        for sale in report_data['sales'][:50]:  # Limitar a 50 ventas
            sales_data.append([
                str(sale.get('id', '')),
                sale.get('date', '').split('T')[0] if sale.get('date') else '',
                sale.get('client_name', '')[:20] if sale.get('client_name') else '',
                sale.get('payment_method', ''),
                str(sale.get('items_count', 0)),
                f"${sale.get('total', 0):,.2f}"
            ])
        
        sales_table = Table(sales_data, colWidths=[0.5*inch, 1*inch, 1.5*inch, 1*inch, 0.7*inch, 1*inch])
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7030A0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # ID alineado a la izquierda
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Total alineado a la derecha
        ]))
        
        elements.append(Paragraph("Detalle de Ventas", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(sales_table)
    
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


def generate_top_products_report_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    Genera un PDF del reporte de productos más vendidos con formato tipo Excel/tabla
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    # Título del reporte
    elements.append(Paragraph("PRODUCTOS MÁS VENDIDOS", title_style))
    
    # Información del período
    period_text = ""
    if report_data.get('start_date'):
        period_text += f"Desde: {report_data['start_date']}"
    if report_data.get('end_date'):
        if period_text:
            period_text += " | "
        period_text += f"Hasta: {report_data['end_date']}"
    if not period_text:
        period_text = "Período: Todos los registros"
    
    elements.append(Paragraph(period_text, subtitle_style))
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de resumen
    summary_data = [
        ['RESUMEN', ''],
        ['Total de Productos', str(report_data.get('total_products', 0))],
        ['Límite Mostrado', str(report_data.get('limit', 0))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D9E1F2')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E7E6E6')])
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de productos
    if report_data.get('products'):
        products_data = [
            ['#', 'PRODUCTO', 'PRESENTACIÓN', 'CANTIDAD VENDIDA', 'INGRESOS', 'VENTAS', 'PROMEDIO']
        ]
        
        for idx, product in enumerate(report_data['products'], 1):
            products_data.append([
                str(idx),
                product.get('product_name', '')[:25],
                product.get('presentation', '')[:15],
                str(product.get('total_quantity_sold', 0)),
                f"${product.get('total_revenue', 0):,.2f}",
                str(product.get('sales_count', 0)),
                f"${product.get('average_per_sale', 0):,.2f}"
            ])
        
        products_table = Table(
            products_data,
            colWidths=[0.4*inch, 1.8*inch, 1*inch, 1*inch, 1*inch, 0.7*inch, 1*inch]
        )
        products_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E2EFDA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Producto alineado a la izquierda
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Ingresos alineado a la derecha
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),  # Promedio alineado a la derecha
        ]))
        
        elements.append(Paragraph("Ranking de Productos", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(products_table)
    
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


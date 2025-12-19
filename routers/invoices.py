"""
Endpoints para facturas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from crud.sales import get_sale
from utils.auth import get_current_user_optional
from utils.invoice_generator import generate_invoice_pdf
from db.models import User, Client

routerInvoice = APIRouter(prefix="/invoices", tags=["Invoices"])


@routerInvoice.get("/{sale_id}")
def get_invoice_pdf(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Obtiene la factura en PDF de una venta específica
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver facturas"
        )
    
    try:
        sale = get_sale(db, sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        # Obtener datos del cliente
        client = db.query(Client).filter(Client.id == sale.client_id).first()
        
        # Preparar datos para la factura
        invoice_data = {
            "id": sale.id,
            "client_name": f"{client.first_name} {client.last_name}".strip() if client else "N/A",
            "client_address": f"{client.email or 'N/A'}" if client else "N/A",
            "client_phone": client.phone if client else "N/A",
            "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
            "payment_method": sale.payment_method,
            "total": float(sale.total),
            "subtotal": float(sale.total),
            "tax_rate": 0.21,
            "details": []
        }
        
        # Agregar detalles de productos
        for detail in sale.details:
            product_name = "N/A"
            product_presentation = ""
            product_concentration = ""
            
            if detail.batch and detail.batch.product:
                product_name = detail.batch.product.name
                product_presentation = detail.batch.product.presentation or ""
                product_concentration = detail.batch.product.concentration or ""
            
            invoice_data["details"].append({
                "product_name": product_name,
                "product_presentation": product_presentation,
                "product_concentration": product_concentration,
                "quantity": detail.quantity,
                "unit_price": float(detail.unit_price),
                "subtotal": float(detail.subtotal)
            })
        
        # Información de la farmacia
        pharmacy_info = {
            "name": "Sistema Farmacia",
            "address": "Dirección de la farmacia",
            "logo_path": None
        }
        
        # Generar PDF
        pdf_bytes = generate_invoice_pdf(invoice_data, pharmacy_info)
        
        filename = f"factura_FAC-{sale.id:04d}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f'inline; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar factura: {str(e)}")



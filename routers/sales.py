from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
from db.database import get_db
from db.schemas import SaleCreate, SaleResponse, SalesDetailResponse
from crud.sales import create_sale, get_sales, get_sale
from utils.auth import get_current_user, get_current_user_optional
from db.models import User, Sale, SalesDetail, Client
from utils.invoice_generator import generate_invoice_pdf
from utils.whatsapp_sender import send_whatsapp_message

routerSale = APIRouter(prefix="/sales", tags=["Sales"])


def enrich_sale_response(sale: Sale) -> Dict[str, Any]:
    """
    Enriquece la respuesta de la venta con información relacionada
    de cliente, usuario, productos y lotes
    """
    # Información del cliente
    client_name = None
    client_email = None
    if sale.client:
        client_name = f"{sale.client.first_name} {sale.client.last_name}".strip()
        client_email = sale.client.email
    
    # Información del usuario
    user_name = None
    user_email = None
    if sale.user:
        user_name = f"{sale.user.first_name} {sale.user.last_name}".strip()
        user_email = sale.user.email
    
    # Enriquecer detalles con información de productos y lotes
    enriched_details = []
    for detail in sale.details:
        detail_dict = {
            "id": detail.id,
            "batch_id": detail.batch_id,
            "quantity": detail.quantity,
            "unit_price": float(detail.unit_price),
            "subtotal": float(detail.subtotal),
            "batch_expiration_date": None,
            "batch_stock": None,
            "product_name": None,
            "product_presentation": None,
            "product_concentration": None
        }
        
        if detail.batch:
            detail_dict["batch_expiration_date"] = detail.batch.expiration_date
            detail_dict["batch_stock"] = detail.batch.stock
            
            if detail.batch.product:
                detail_dict["product_name"] = detail.batch.product.name
                detail_dict["product_presentation"] = detail.batch.product.presentation
                detail_dict["product_concentration"] = detail.batch.product.concentration
        
        enriched_details.append(detail_dict)
    
    return {
        "id": sale.id,
        "client_id": sale.client_id,
        "user_id": sale.user_id,
        "sale_date": sale.sale_date,
        "payment_method": sale.payment_method,
        "total": float(sale.total),
        "details": enriched_details,
        "client_name": client_name,
        "client_email": client_email,
        "user_name": user_name,
        "user_email": user_email
    }


def send_invoice_whatsapp(db: Session, sale: Sale, sale_response: Dict[str, Any]):
    """
    Genera la factura en PDF y la envía por WhatsApp al cliente automáticamente
    """
    # Obtener datos del cliente
    client = db.query(Client).filter(Client.id == sale.client_id).first()
    if not client or not client.phone:
        print(f"Cliente sin número de teléfono, no se envía WhatsApp")
        return
    
    # Preparar datos para la factura
    invoice_data = {
        "id": sale.id,
        "client_name": f"{client.first_name} {client.last_name}".strip(),
        "client_address": f"{client.email or 'N/A'}",
        "client_phone": client.phone,
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else datetime.now().isoformat(),
        "payment_method": sale.payment_method,
        "total": float(sale.total),
        "subtotal": float(sale.total),  # Se calculará IVA después
        "tax_rate": 0.21,  # IVA 21% por defecto
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
    
    # Información de la farmacia (puede venir de configuración)
    pharmacy_info = {
        "name": "Sistema Farmacia",
        "address": "Dirección de la farmacia",
        "logo_path": None  # Ruta al logo si existe
    }
    
    # Generar PDF de la factura
    try:
        pdf_bytes = generate_invoice_pdf(invoice_data, pharmacy_info)
        
        # Mensaje para WhatsApp
        invoice_number = f"FAC-{sale.id:04d}"
        sale_date_obj = sale.sale_date if sale.sale_date else datetime.now()
        message = f"""✅ *Factura de Venta*

N° de Factura: {invoice_number}
Fecha: {sale_date_obj.strftime('%d/%m/%Y')}
Hora: {sale_date_obj.strftime('%H:%M')}

Cliente: {invoice_data['client_name']}
Método de pago: {sale.payment_method}

*Productos:*
"""
        
        for detail in invoice_data["details"]:
            message += f"• {detail['product_name']} {detail['product_presentation']} - Cantidad: {detail['quantity']} - ${detail['subtotal']:.2f}\n"
        
        total_with_tax = invoice_data["total"] * 1.21
        message += f"""
*Total: ${total_with_tax:.2f}*

Gracias por su compra! 🏥💊
        """
        
        # Enviar por WhatsApp
        phone_number = client.phone
        if not phone_number:
            print(f"⚠️ Cliente {client.id} no tiene número de teléfono registrado")
            return
        
        # Normalizar número de teléfono usando la función del módulo
        from utils.whatsapp_sender import normalize_phone_number
        phone_number = normalize_phone_number(phone_number.strip())
        
        print(f"[VENTA] Enviando factura por WhatsApp a: {phone_number}")
        
        result = send_whatsapp_message(
            phone_number=phone_number,
            message=message.strip(),
            pdf_bytes=pdf_bytes,
            filename=f"factura_{invoice_number}.pdf"
        )
        
        if result.get("success"):
            print(f"✅ Factura enviada por WhatsApp a {phone_number}")
            if result.get("whatsapp_url"):
                print(f"📱 Enlace de WhatsApp: {result.get('whatsapp_url')}")
        else:
            error_msg = result.get('error', 'Error desconocido')
            print(f"⚠️ Error al enviar WhatsApp a {phone_number}: {error_msg}")
            # No fallar la venta si falla WhatsApp
            
    except Exception as e:
        print(f"⚠️ Error al generar/enviar factura: {e}")
        # No lanzar excepción para no fallar la venta


@routerSale.post("/")
def create(data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    RF14-RF16: Registrar una venta con cálculo automático de subtotales y control de stock
    Requiere autenticación obligatoria.
    
    RF14: Registrar una venta
    RF15: Calcular automáticamente subtotales (se calculan automáticamente)
    RF16: Controlar el stock después de cada venta (se reduce automáticamente)
    
    Automáticamente:
    - Genera factura en PDF
    - Envía factura por WhatsApp al cliente (si tiene número de teléfono)
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para registrar ventas"
        )
    
    try:
        sale = create_sale(db, data, current_user.id)
        sale_response = enrich_sale_response(sale)
        
        # Generar y enviar factura por WhatsApp automáticamente
        try:
            send_invoice_whatsapp(db, sale, sale_response)
        except Exception as whatsapp_error:
            # No fallar la venta si falla el WhatsApp, solo loguear
            print(f"Advertencia: No se pudo enviar WhatsApp: {whatsapp_error}")
        
        return sale_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la venta: {str(e)}")


@routerSale.get("/")
def list_all(
    client_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF17: Mostrar historial de ventas con filtros.
    Incluye información relacionada: cliente, usuario, productos y lotes.
    Si no hay token válido, retorna lista vacía en lugar de error 401.
    """
    if current_user is None:
        # Retornar lista vacía si no hay autenticación
        return []
    
    try:
        sales = get_sales(db, client_id=client_id, user_id=user_id, start_date=start_date, end_date=end_date)
        return [enrich_sale_response(sale) for sale in sales]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")


@routerSale.get("/{sale_id}")
def get(sale_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Obtener una venta por ID con toda la información relacionada.
    Incluye: cliente, usuario, detalles, productos y lotes.
    Si no hay token válido, retorna error 401.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver los detalles de la venta"
        )
    
    sale = get_sale(db, sale_id)
    if not sale:
        raise HTTPException(404, "Venta no encontrada")
    return enrich_sale_response(sale)

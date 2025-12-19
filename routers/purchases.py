from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any, List
from db.database import get_db
from db.schemas import PurchaseCreate, PurchaseResponse, PurchaseDetailCreate
from crud.purchases import create_purchase, get_purchases, get_purchase
from utils.auth import get_current_user, get_current_user_optional
from db.models import User, Purchase, PurchaseDetail
import json
import base64
import os
import uuid
import shutil

routerPurchase = APIRouter(prefix="/purchases", tags=["Purchases"])


def save_image_from_base64(base64_string: str, upload_dir: str = "uploads/products") -> Optional[str]:
    """
    Guarda una imagen desde base64 a un archivo
    Retorna la ruta del archivo guardado
    """
    if not base64_string:
        return None
    
    try:
        # Detectar si es base64 con prefijo (data:image/png;base64,...)
        if ',' in base64_string:
            header, data = base64_string.split(',', 1)
            # Extraer extensión del header
            if 'png' in header:
                extension = 'png'
            elif 'jpeg' in header or 'jpg' in header:
                extension = 'jpg'
            elif 'gif' in header:
                extension = 'gif'
            elif 'webp' in header:
                extension = 'webp'
            else:
                extension = 'jpg'
        else:
            data = base64_string
            extension = 'jpg'
        
        # Decodificar base64
        image_data = base64.b64decode(data)
        
        # Crear directorio si no existe
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        safe_filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return file_path
    except Exception as e:
        print(f"Error al guardar imagen base64: {e}")
        return None


def enrich_purchase_response(purchase: Purchase) -> Dict[str, Any]:
    """
    Enriquece la respuesta de la compra con información relacionada
    de proveedor, usuario, productos y lotes
    """
    # Información del proveedor
    supplier_name = None
    supplier_email = None
    if purchase.supplier:
        supplier_name = purchase.supplier.name
        supplier_email = purchase.supplier.email
    
    # Información del usuario
    user_name = None
    user_email = None
    if purchase.user:
        user_name = f"{purchase.user.first_name} {purchase.user.last_name}".strip()
        user_email = purchase.user.email
    
    # Enriquecer detalles con información de productos y lotes
    enriched_details = []
    for detail in purchase.details:
        detail_dict = {
            "id": detail.id,
            "batch_id": detail.batch_id,
            "quantity": detail.quantity,
            "unit_price": float(detail.unit_price),
            "subtotal": float(detail.subtotal),
            "batch_expiration_date": None,
            "batch_stock": None,
            "batch_purchase_price": None,
            "batch_sale_price": None,
            "product_name": None,
            "product_presentation": None,
            "product_concentration": None,
            "product_image": None
        }
        
        if detail.batch:
            detail_dict["batch_expiration_date"] = detail.batch.expiration_date.isoformat() if detail.batch.expiration_date else None
            detail_dict["batch_stock"] = detail.batch.stock
            detail_dict["batch_purchase_price"] = float(detail.batch.purchase_price) if detail.batch.purchase_price else None
            detail_dict["batch_sale_price"] = float(detail.batch.sale_price) if detail.batch.sale_price else None
            
            if detail.batch.product:
                detail_dict["product_name"] = detail.batch.product.name
                detail_dict["product_presentation"] = detail.batch.product.presentation
                detail_dict["product_concentration"] = detail.batch.product.concentration
                detail_dict["product_image"] = detail.batch.product.image
        
        enriched_details.append(detail_dict)
    
    return {
        "id": purchase.id,
        "user_id": purchase.user_id,
        "supplier_id": purchase.supplier_id,
        "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
        "payment_method": purchase.payment_method,
        "total": float(purchase.total),
        "details": enriched_details,
        "supplier_name": supplier_name,
        "supplier_email": supplier_email,
        "user_name": user_name,
        "user_email": user_email
    }


@routerPurchase.post("/")
def create(
    supplier_id: int = Form(...),
    payment_method: str = Form(...),
    purchase_date: Optional[datetime] = Form(None),
    details_json: str = Form(...),  # JSON string con los detalles
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    RF18-RF19: Registrar compras a proveedores y aumentar stock automáticamente
    Requiere autenticación obligatoria.
    
    RF18: Registrar compras a proveedores
    RF19: Aumentar stock automáticamente al registrar una compra
    
    NUEVO: Permite crear productos nuevos durante la compra con imagen.
    En los detalles (JSON), proporciona:
    - product_name, category_id, presentation, concentration (para crear producto nuevo)
    - product_image (base64 string opcional) - Imagen del producto
    - expiration_date, purchase_price, sale_price (para crear lote nuevo)
    - unit_price, quantity, subtotal
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para registrar compras"
        )
    
    try:
        # Parsear detalles desde JSON
        details_data = json.loads(details_json)
        
        # Procesar imágenes de los detalles
        processed_details = []
        for detail in details_data:
            image_path = None
            
            # Si hay imagen en base64, guardarla
            if detail.get('product_image'):
                image_path = save_image_from_base64(detail['product_image'])
            
            # Crear PurchaseDetailCreate
            detail_obj = PurchaseDetailCreate(
                batch_id=detail.get('batch_id'),
                product_name=detail.get('product_name'),
                product_description=detail.get('product_description'),
                category_id=detail.get('category_id'),
                presentation=detail.get('presentation'),
                concentration=detail.get('concentration'),
                product_image=image_path,  # Ruta del archivo guardado
                expiration_date=datetime.fromisoformat(detail['expiration_date'].replace('Z', '+00:00')).date() if detail.get('expiration_date') else None,
                purchase_price=float(detail.get('purchase_price', 0)) if detail.get('purchase_price') else None,
                sale_price=float(detail.get('sale_price', 0)) if detail.get('sale_price') else None,
                unit_price=float(detail['unit_price']),
                quantity=int(detail['quantity']),
                subtotal=float(detail['subtotal'])
            )
            processed_details.append(detail_obj)
        
        # Crear PurchaseCreate
        purchase_data = PurchaseCreate(
            supplier_id=supplier_id,
            payment_method=payment_method,
            purchase_date=purchase_date or datetime.now(),
            details=processed_details
        )
        
        purchase = create_purchase(db, purchase_data, current_user.id)
        return enrich_purchase_response(purchase)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear JSON de detalles: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la compra: {str(e)}")


@routerPurchase.get("/")
def list_all(
    supplier_id: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF20: Listar historial de compras con filtros.
    Incluye información relacionada: proveedor, usuario, productos y lotes.
    Si no hay token válido, retorna lista vacía en lugar de error 401.
    """
    if current_user is None:
        # Retornar lista vacía si no hay autenticación
        return []
    
    try:
        purchases = get_purchases(db, supplier_id=supplier_id, user_id=user_id, start_date=start_date, end_date=end_date)
        return [enrich_purchase_response(purchase) for purchase in purchases]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener compras: {str(e)}")


@routerPurchase.get("/{purchase_id}")
def get(purchase_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Obtener una compra por ID con toda la información relacionada.
    Incluye: proveedor, usuario, detalles, productos y lotes.
    Si no hay token válido, retorna error 401.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver los detalles de la compra"
        )
    
    purchase = get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(404, "Compra no encontrada")
    return enrich_purchase_response(purchase)

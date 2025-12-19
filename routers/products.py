from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from crud.products import (
    create_product, delete_product, get_product, get_products, 
    update_product, update_product_stock, update_product_price
)
from utils.auth import get_current_user
from utils.permissions import check_permission
from db.models import User, Product
import shutil
import uuid
import os
import time

from db.schemas import ProductCreate, ProductResponse, ProductUpdate, ProductStockUpdate, ProductPriceUpdate

routerProduct = APIRouter(prefix="/products", tags=["Products"])

# NOTA: El endpoint POST /products/ ha sido ELIMINADO
# Los productos ahora se crean automáticamente al realizar una compra
# Solo se permite editar y eliminar productos existentes


@routerProduct.get("/all", response_model=list[ProductResponse])
def list_all(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Listar productos con búsqueda y filtros mejorados
    
    Parámetros:
    - search: Busca en nombre, presentación, concentración o descripción (case-insensitive)
    - category_id: Filtra por categoría
    - status: Filtra por estado (1=activo, 0=inactivo, None=todos)
    
    Retorna productos con:
    - total_stock: Stock total de todos los lotes activos
    - sale_price: Precio de venta del lote más reciente
    """
    try:
        products = get_products(db, search=search, category_id=category_id, status=status)
        # Convertir diccionarios a ProductResponse
        return [ProductResponse(**p) for p in products]
    except Exception as e:
        from sqlalchemy.exc import OperationalError
        if isinstance(e, OperationalError) or "Can't connect" in str(e) or "Lost connection" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Servicio de base de datos no disponible. Verifica que MySQL esté corriendo."
            )
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")


@routerProduct.get("/", response_model=ProductResponse)
def get(product_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    product = db.query(Product).options(joinedload(Product.batches)).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Calcular stock total y precio
    total_stock = sum(batch.stock for batch in product.batches if batch.status == 1 and batch.stock is not None)
    sale_price = None
    if product.batches:
        batches_with_price = [b for b in product.batches if b.status == 1 and b.sale_price is not None]
        if batches_with_price:
            latest_batch = max(batches_with_price, key=lambda b: b.id)
            sale_price = float(latest_batch.sale_price)
    
    # Construir URL completa de la imagen
    image_url = None
    if product.image:
        import os
        if product.image.startswith('http://') or product.image.startswith('https://'):
            image_url = product.image
        else:
            base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
            image_path = product.image.lstrip('/')
            image_url = f"{base_url}/{image_path}"
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        category_id=product.category_id,
        presentation=product.presentation,
        concentration=product.concentration,
        image=product.image,
        image_url=image_url,
        status=product.status,
        total_stock=total_stock,
        sale_price=sale_price
    )


@routerProduct.put("/", response_model=ProductResponse)
def update(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    category_id: int = Form(None),
    presentation: str = Form(None),
    concentration: str = Form(None),
    status: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Editar producto - Requiere permiso products.edit"""
    check_permission(db, current_user, "products.edit")
    
    existing = get_product(db, product_id)
    if not existing:
        raise HTTPException(404, "Product not found")

    image_path = existing.image

    if image:
        folder = "uploads/products"
        os.makedirs(folder, exist_ok=True)

        extension = image.filename.split(".")[-1]
        filename = f"{int(time.time())}.{extension}"

        filepath = os.path.join(folder, filename)

        with open(filepath, "wb") as f:
            f.write(image.file.read())

        image_path = filepath

    data = ProductUpdate(
        name=name,
        description=description,
        category_id=category_id,
        presentation=presentation,
        concentration=concentration,
        status=status,
        image=image_path
    )

    updated = update_product(db, product_id, data)

    return updated


@routerProduct.delete("/")
def delete(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar producto - Requiere permiso products.delete"""
    check_permission(db, current_user, "products.delete")
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted successfully"}


@routerProduct.put("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    data: ProductStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar el stock de un producto.
    Actualiza el stock del lote más reciente activo del producto.
    Requiere permiso 'products.stock'.
    """
    check_permission(db, current_user, "products.stock")
    
    try:
        update_product_stock(db, product_id, data.stock)
        
        # Obtener el producto actualizado con stock y precio
        from sqlalchemy.orm import joinedload
        product = db.query(Product).options(joinedload(Product.batches)).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(404, "Product not found")
        
        # Calcular stock total y precio
        total_stock = sum(batch.stock for batch in product.batches if batch.status == 1 and batch.stock is not None)
        sale_price = None
        if product.batches:
            batches_with_price = [b for b in product.batches if b.status == 1 and b.sale_price is not None]
            if batches_with_price:
                latest_batch = max(batches_with_price, key=lambda b: b.id)
                sale_price = float(latest_batch.sale_price)
        
        # Construir URL completa de la imagen
        image_url = None
        if product.image:
            if product.image.startswith('http://') or product.image.startswith('https://'):
                image_url = product.image
            else:
                base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
                image_path = product.image.lstrip('/')
                image_url = f"{base_url}/{image_path}"
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            presentation=product.presentation,
            concentration=product.concentration,
            image=product.image,
            image_url=image_url,
            status=product.status,
            total_stock=total_stock,
            sale_price=sale_price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar stock: {str(e)}")


@routerProduct.put("/{product_id}/price", response_model=ProductResponse)
def update_price(
    product_id: int,
    data: ProductPriceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar el precio de venta de un producto.
    Actualiza el precio de todos los lotes activos del producto.
    Requiere permiso 'products.edit'.
    """
    check_permission(db, current_user, "products.edit")
    
    try:
        update_product_price(db, product_id, data.price)
        
        # Obtener el producto actualizado con stock y precio
        from sqlalchemy.orm import joinedload
        product = db.query(Product).options(joinedload(Product.batches)).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(404, "Product not found")
        
        # Calcular stock total y precio
        total_stock = sum(batch.stock for batch in product.batches if batch.status == 1 and batch.stock is not None)
        sale_price = None
        if product.batches:
            batches_with_price = [b for b in product.batches if b.status == 1 and b.sale_price is not None]
            if batches_with_price:
                latest_batch = max(batches_with_price, key=lambda b: b.id)
                sale_price = float(latest_batch.sale_price)
        
        # Construir URL completa de la imagen
        image_url = None
        if product.image:
            if product.image.startswith('http://') or product.image.startswith('https://'):
                image_url = product.image
            else:
                base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
                image_path = product.image.lstrip('/')
                image_url = f"{base_url}/{image_path}"
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            presentation=product.presentation,
            concentration=product.concentration,
            image=product.image,
            image_url=image_url,
            status=product.status,
            total_stock=total_stock,
            sale_price=sale_price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar precio: {str(e)}")

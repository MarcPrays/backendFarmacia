from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from db.models import Product, Category, MedicineBatch
from db.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate):
    # Verificar que la categoría existe
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise ValueError(f"La categoría con ID {data.category_id} no existe")
    
    product = Product(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        presentation=data.presentation,
        concentration=data.concentration,
        image=data.image,
        status=1  # Establecer status por defecto
    )
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "foreign key constraint" in error_msg.lower():
            raise ValueError(f"La categoría con ID {data.category_id} no existe")
        raise ValueError(f"Error de integridad: {error_msg}")


def get_products(db: Session, search: str = None, category_id: int = None, status: int = None):
    """
    Obtener productos con búsqueda y filtros mejorados
    Incluye stock total y precio de venta (del lote más reciente o promedio)
    """
    from sqlalchemy import or_, func
    
    # Query con joinedload para cargar lotes eficientemente
    query = db.query(Product).options(joinedload(Product.batches))
    
    # Filtro por status (por defecto solo activos)
    if status is not None:
        query = query.filter(Product.status == status)
    else:
        query = query.filter(Product.status == 1)
    
    # Filtro por categoría
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Búsqueda mejorada: nombre, presentación, concentración o descripción (case-insensitive)
    if search:
        search_term = f"%{search.lower()}%"
        conditions = [
            func.lower(Product.name).like(search_term),
            func.lower(Product.presentation).like(search_term),
            func.lower(Product.concentration).like(search_term),
            func.lower(Product.description).like(search_term)
        ]
        query = query.filter(or_(*conditions))
    
    products = query.all()
    
    # Enriquecer productos con stock total y precio
    enriched_products = []
    for product in products:
        # Calcular stock total de todos los lotes activos
        total_stock = sum(batch.stock for batch in product.batches if batch.status == 1 and batch.stock is not None)
        
        # Obtener precio de venta (del lote más reciente con precio, o promedio)
        sale_price = None
        if product.batches:
            # Buscar lotes activos con precio
            batches_with_price = [b for b in product.batches if b.status == 1 and b.sale_price is not None]
            if batches_with_price:
                # Usar el precio del lote más reciente
                latest_batch = max(batches_with_price, key=lambda b: b.id)
                sale_price = float(latest_batch.sale_price)
        
        # Construir URL completa de la imagen
        image_url = None
        if product.image:
            # Si la imagen ya tiene http://, usarla tal cual
            if product.image.startswith('http://') or product.image.startswith('https://'):
                image_url = product.image
            else:
                # Construir URL completa desde la ruta relativa
                # Base URL del servidor (puede configurarse desde variable de entorno)
                import os
                base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
                # Asegurar que la ruta no tenga barras duplicadas
                image_path = product.image.lstrip('/')
                image_url = f"{base_url}/{image_path}"
        
        # Agregar stock y precio al producto (usando atributos dinámicos)
        product_dict = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id,
            'presentation': product.presentation,
            'concentration': product.concentration,
            'image': product.image,  # Ruta relativa (mantener para compatibilidad)
            'image_url': image_url,  # URL completa
            'status': product.status,
            'total_stock': total_stock,
            'sale_price': sale_price
        }
        enriched_products.append(product_dict)
    
    return enriched_products


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product_id: int, data: ProductUpdate):
    product = get_product(db, product_id)
    if not product:
        return None

    # Solo actualizar campos que tienen valores (no None)
    update_data = data.dict(exclude_unset=True, exclude_none=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = get_product(db, product_id)
    if not product:
        return False

    product.status = 0
    db.commit()
    return True


def update_product_stock(db: Session, product_id: int, new_stock: int):
    """
    Actualiza el stock total de un producto.
    Establece el stock total del producto poniendo todo el stock en el lote más reciente
    y poniendo los otros lotes activos en 0, para que el total sea exactamente el valor especificado.
    NO modifica el precio (sale_price).
    Si no hay lotes activos, crea un nuevo lote con el stock especificado.
    """
    from sqlalchemy.orm import joinedload
    
    # Cargar producto con lotes
    product = db.query(Product).options(joinedload(Product.batches)).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"El producto con ID {product_id} no existe")
    
    # Buscar todos los lotes activos
    active_batches = [b for b in product.batches if b.status == 1]
    
    if active_batches:
        # Ordenar por ID descendente para obtener el más reciente
        active_batches.sort(key=lambda b: b.id, reverse=True)
        latest_batch = active_batches[0]
        
        # Guardar el precio actual para no perderlo
        current_price = latest_batch.sale_price
        
        # Poner todo el stock nuevo en el lote más reciente
        # SOLO modificar el stock, mantener el precio intacto
        latest_batch.stock = new_stock
        
        # Poner los otros lotes activos en 0 para que el total sea exactamente new_stock
        # Mantener los precios de los otros lotes intactos
        for batch in active_batches[1:]:
            batch.stock = 0
        
        db.commit()
        db.refresh(latest_batch)
        return latest_batch
    else:
        # Si no hay lotes activos, crear uno nuevo
        # No establecer precio aquí, se establecerá cuando se actualice el precio
        new_batch = MedicineBatch(
            product_id=product_id,
            stock=new_stock,
            status=1,
            sale_price=None  # Precio se establece por separado
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)
        return new_batch


def update_product_price(db: Session, product_id: int, new_price: float):
    """
    Actualiza el precio de venta de un producto.
    Actualiza SOLO el precio (sale_price) de todos los lotes activos del producto.
    NO modifica el stock.
    """
    from sqlalchemy.orm import joinedload
    
    # Cargar producto con lotes usando joinedload
    product = db.query(Product).options(joinedload(Product.batches)).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"El producto con ID {product_id} no existe")
    
    # Buscar todos los lotes activos
    active_batches = [b for b in product.batches if b.status == 1]
    
    if not active_batches:
        raise ValueError(f"El producto con ID {product_id} no tiene lotes activos")
    
    # Actualizar SOLO el precio (sale_price) de todos los lotes activos
    # NO modificar el stock
    updated_count = 0
    for batch in active_batches:
        # Solo actualizar el precio, mantener el stock intacto
        batch.sale_price = new_price
        updated_count += 1
    
    db.commit()
    
    # Refrescar los lotes
    for batch in active_batches:
        db.refresh(batch)
    
    return {
        "product_id": product_id,
        "new_price": new_price,
        "batches_updated": updated_count
    }

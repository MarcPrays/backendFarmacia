from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from decimal import Decimal
from db.models import Purchase, PurchaseDetail, MedicineBatch, Supplier, User, Product, Category
from db.schemas import PurchaseCreate
from crud.products import create_product


def find_or_create_product(db: Session, product_name: str, category_id: int, presentation: str, concentration: str, description: str = None, image_path: str = None):
    """
    Busca un producto existente o crea uno nuevo
    Busca por nombre, presentación y concentración
    Si el producto existe pero no tiene imagen y se proporciona una, actualiza la imagen
    Si el producto existe y tiene imagen pero se proporciona una nueva, también la actualiza
    """
    # Buscar producto existente
    product = db.query(Product).filter(
        Product.name == product_name,
        Product.presentation == presentation,
        Product.concentration == concentration,
        Product.status == 1
    ).first()
    
    if product:
        # Si se proporciona una imagen, actualizarla (incluso si ya tiene una)
        if image_path:
            product.image = image_path
            db.commit()
            db.refresh(product)
        return product
    
    # Si no existe, crear nuevo producto
    from db.schemas import ProductCreate
    product_data = ProductCreate(
        name=product_name,
        description=description,
        category_id=category_id,
        presentation=presentation,
        concentration=concentration,
        image=image_path
    )
    
    product = create_product(db, product_data)
    return product


def create_purchase(db: Session, data: PurchaseCreate, user_id: int):
    """
    RF18: Registrar compras a proveedores
    RF19: Aumentar stock automáticamente al registrar una compra
    
    Ahora permite crear productos nuevos durante la compra:
    - Si se proporciona product_name, category_id, presentation, concentration: crea producto y lote nuevos
    - Si se proporciona batch_id: usa el lote existente (compatibilidad hacia atrás)
    """
    # Verificar que el proveedor existe
    supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id).first()
    if not supplier:
        raise ValueError(f"El proveedor con ID {data.supplier_id} no existe")
    
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"El usuario con ID {user_id} no existe")
    
    # Calcular totales y procesar detalles
    total = Decimal('0.00')
    purchase_details = []
    
    for detail in data.details:
        batch = None
        
        # Opción 1: Si se proporciona información del producto, crear/buscar producto y lote
        if detail.product_name and detail.category_id and detail.presentation and detail.concentration:
            # Obtener la ruta de la imagen (ya guardada desde el router)
            image_path = detail.product_image if hasattr(detail, 'product_image') and detail.product_image else None
            
            # Buscar o crear producto (con imagen si se proporciona)
            product = find_or_create_product(
                db=db,
                product_name=detail.product_name,
                category_id=detail.category_id,
                presentation=detail.presentation,
                concentration=detail.concentration,
                description=detail.product_description,
                image_path=image_path  # Ruta de la imagen guardada
            )
            
            # Crear nuevo lote para este producto
            batch = MedicineBatch(
                product_id=product.id,
                expiration_date=detail.expiration_date,
                stock=detail.quantity,  # Stock inicial = cantidad comprada
                purchase_price=detail.purchase_price or detail.unit_price,
                sale_price=detail.sale_price or detail.unit_price,
                status=1
            )
            db.add(batch)
            db.flush()  # Para obtener el ID del lote
            
        # Opción 2: Si se proporciona batch_id, usar lote existente (compatibilidad)
        elif detail.batch_id:
            batch = db.query(MedicineBatch).filter(MedicineBatch.id == detail.batch_id).first()
            if not batch:
                raise ValueError(f"El lote con ID {detail.batch_id} no existe")
            # Aumentar stock del lote existente
            batch.stock += detail.quantity
        else:
            raise ValueError("Debe proporcionar información del producto (product_name, category_id, presentation, concentration) o batch_id")
        
        # Calcular subtotal
        subtotal = Decimal(str(detail.unit_price)) * detail.quantity
        total += subtotal
        
        purchase_details.append({
            'batch_id': batch.id,
            'quantity': detail.quantity,
            'unit_price': detail.unit_price,
            'subtotal': subtotal
        })
    
    # Crear la compra
    purchase = Purchase(
        user_id=user_id,
        supplier_id=data.supplier_id,
        purchase_date=data.purchase_date or datetime.now(),
        payment_method=data.payment_method,
        total=total
    )
    db.add(purchase)
    db.flush()  # Para obtener el ID de la compra
    
    # Crear los detalles de la compra
    for detail_data in purchase_details:
        purchase_detail = PurchaseDetail(
            purchase_id=purchase.id,
            batch_id=detail_data['batch_id'],
            quantity=detail_data['quantity'],
            unit_price=detail_data['unit_price'],
            subtotal=detail_data['subtotal']
        )
        db.add(purchase_detail)
    
    try:
        db.commit()
        # Recargar la compra con todas las relaciones
        db.refresh(purchase)
        # Cargar relaciones para la respuesta
        purchase = db.query(Purchase).options(
            joinedload(Purchase.details).joinedload(PurchaseDetail.batch).joinedload(MedicineBatch.product),
            joinedload(Purchase.supplier),
            joinedload(Purchase.user)
        ).filter(Purchase.id == purchase.id).first()
        return purchase
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        raise ValueError(f"Error al crear la compra: {error_msg}")


def get_purchases(db: Session, supplier_id: int = None, user_id: int = None, start_date: datetime = None, end_date: datetime = None):
    """
    RF20: Listar historial de compras con filtros
    Incluye información relacionada: proveedor, usuario, detalles, lotes y productos
    """
    query = db.query(Purchase).options(
        joinedload(Purchase.details).joinedload(PurchaseDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Purchase.supplier),
        joinedload(Purchase.user)
    )
    
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    
    if user_id:
        query = query.filter(Purchase.user_id == user_id)
    
    if start_date:
        query = query.filter(Purchase.purchase_date >= start_date)
    
    if end_date:
        query = query.filter(Purchase.purchase_date <= end_date)
    
    return query.order_by(Purchase.purchase_date.desc()).all()


def get_purchase(db: Session, purchase_id: int):
    """
    Obtener una compra por ID con toda la información relacionada
    Incluye: proveedor, usuario, detalles, lotes y productos
    """
    return db.query(Purchase).options(
        joinedload(Purchase.details).joinedload(PurchaseDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Purchase.supplier),
        joinedload(Purchase.user)
    ).filter(Purchase.id == purchase_id).first()

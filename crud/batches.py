from sqlalchemy.orm import Session, joinedload
from db.models import MedicineBatch, Product
from db.schemas import MedicineBatchCreate, MedicineBatchUpdate


def create_batch(db: Session, data: MedicineBatchCreate):
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise ValueError(f"El producto con ID {data.product_id} no existe")
    
    batch = MedicineBatch(
        product_id=data.product_id,
        expiration_date=data.expiration_date,
        stock=data.stock or 0,
        purchase_price=data.purchase_price,
        sale_price=data.sale_price
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    # Cargar relación con producto
    db.refresh(batch, ['product'])
    return batch


def get_batches(db: Session, product_id: int = None, stock_min: int = None):
    """Obtener lotes con información del producto y filtros opcionales"""
    query = db.query(
        MedicineBatch,
        Product.name.label('product_name'),
        Product.presentation.label('product_presentation')
    ).join(Product, MedicineBatch.product_id == Product.id).filter(
        MedicineBatch.status == 1
    )
    
    # Filtro por producto
    if product_id is not None:
        query = query.filter(MedicineBatch.product_id == product_id)
    
    # Filtro por stock mínimo
    if stock_min is not None:
        query = query.filter(MedicineBatch.stock >= stock_min)
    
    results = query.all()
    
    # Construir respuesta con información del producto
    batches = []
    for batch, product_name, product_presentation in results:
        batch_dict = {
            'id': batch.id,
            'product_id': batch.product_id,
            'expiration_date': batch.expiration_date,
            'stock': batch.stock,
            'purchase_price': float(batch.purchase_price) if batch.purchase_price else None,
            'sale_price': float(batch.sale_price) if batch.sale_price else None,
            'status': batch.status,
            'product_name': product_name,
            'product_presentation': product_presentation
        }
        batches.append(batch_dict)
    
    return batches


def get_batch(db: Session, batch_id: int):
    """Obtener un lote por ID con información del producto"""
    result = db.query(
        MedicineBatch,
        Product.name.label('product_name'),
        Product.presentation.label('product_presentation')
    ).join(Product, MedicineBatch.product_id == Product.id).filter(
        MedicineBatch.id == batch_id
    ).first()
    
    if not result:
        return None
    
    batch, product_name, product_presentation = result
    return {
        'id': batch.id,
        'product_id': batch.product_id,
        'expiration_date': batch.expiration_date,
        'stock': batch.stock,
        'purchase_price': float(batch.purchase_price) if batch.purchase_price else None,
        'sale_price': float(batch.sale_price) if batch.sale_price else None,
        'status': batch.status,
        'product_name': product_name,
        'product_presentation': product_presentation
    }


def update_batch(db: Session, batch_id: int, data: MedicineBatchUpdate):
    """Actualizar un lote"""
    batch = db.query(MedicineBatch).filter(MedicineBatch.id == batch_id).first()
    if not batch:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    
    # Retornar con información del producto
    return get_batch(db, batch_id)


def delete_batch(db: Session, batch_id: int) -> bool:
    batch = get_batch(db, batch_id)
    if not batch:
        return False

    batch.status = 0
    db.commit()
    return True

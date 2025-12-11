from sqlalchemy.orm import Session
from db.models import Product
from db.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate):
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
    db.commit()
    db.refresh(product)
    return product


def get_products(db: Session):
    return db.query(Product).filter(Product.status == 1).all()


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

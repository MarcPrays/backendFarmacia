from sqlalchemy.orm import Session
from db.models import Supplier
from db.schemas import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, data: SupplierCreate):
    supplier = Supplier(
        name=data.name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        city=data.city
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def get_suppliers(db: Session, search: str = None):
    """Obtener proveedores con búsqueda"""
    query = db.query(Supplier).filter(Supplier.status == 1)
    
    # Búsqueda por nombre, email o teléfono
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Supplier.name.like(search_filter)) |
            (Supplier.email.like(search_filter)) |
            (Supplier.phone.like(search_filter))
        )
    
    return query.all()


def get_supplier(db: Session, supplier_id: int):
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def update_supplier(db: Session, supplier_id: int, data: SupplierUpdate):
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        return False

    supplier.status = 0
    db.commit()
    return True

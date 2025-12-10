from sqlalchemy.orm import Session
from db.models import MedicineBatch
from db.schemas import MedicineBatchCreate, MedicineBatchUpdate


def create_batch(db: Session, data: MedicineBatchCreate):
    batch = MedicineBatch(
        product_id=data.product_id,
        expiration_date=data.expiration_date,
        stock=data.stock,
        purchase_price=data.purchase_price,
        sale_price=data.sale_price
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def get_batches(db: Session):
    return db.query(MedicineBatch).filter(MedicineBatch.status == 1).all()


def get_batch(db: Session, batch_id: int):
    return db.query(MedicineBatch).filter(MedicineBatch.id == batch_id).first()


def update_batch(db: Session, batch_id: int, data: MedicineBatchUpdate):
    batch = get_batch(db, batch_id)
    if not batch:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    return batch


def delete_batch(db: Session, batch_id: int) -> bool:
    batch = get_batch(db, batch_id)
    if not batch:
        return False

    batch.status = 0
    db.commit()
    return True

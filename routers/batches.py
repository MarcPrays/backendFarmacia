from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import MedicineBatchCreate, MedicineBatchUpdate, MedicineBatchResponse
from crud.batches import (
    create_batch,
    get_batches,
    get_batch,
    update_batch,
    delete_batch
)

routerBatch = APIRouter(prefix="/batches", tags=["Medicine Batches"])


@routerBatch.post("/", response_model=MedicineBatchResponse)
def create(data: MedicineBatchCreate, db: Session = Depends(get_db)):
    return create_batch(db, data)


@routerBatch.get("/all", response_model=list[MedicineBatchResponse])
def list_all(
    product_id: int = None,
    stock_min: int = None,
    db: Session = Depends(get_db)
):
    """Listar lotes con filtros opcionales y información del producto"""
    batches = get_batches(db, product_id=product_id, stock_min=stock_min)
    # Convertir diccionarios a objetos MedicineBatchResponse
    return [MedicineBatchResponse(**batch) for batch in batches]


@routerBatch.get("/", response_model=MedicineBatchResponse)
def get(batch_id: int, db: Session = Depends(get_db)):
    batch = get_batch(db, batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")
    return MedicineBatchResponse(**batch)


@routerBatch.put("/", response_model=MedicineBatchResponse)
def update(batch_id: int, data: MedicineBatchUpdate, db: Session = Depends(get_db)):
    updated = update_batch(db, batch_id, data)
    if not updated:
        raise HTTPException(404, "Batch not found")
    return updated


@routerBatch.delete("/")
def delete(batch_id: int, db: Session = Depends(get_db)):
    deleted = delete_batch(db, batch_id)
    if not deleted:
        raise HTTPException(404, "Batch not found")
    return {"message": "Batch deleted successfully"}

@routerBatch.delete("/")
def delete(batch_id: int, db: Session = Depends(get_db)):
    deleted = delete_batch(db, batch_id)
    if not deleted:
        raise HTTPException(404, "Batch not found")
    return {"message": "Batch deleted successfully"}

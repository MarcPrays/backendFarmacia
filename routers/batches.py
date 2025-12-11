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


@routerBatch.post("/create", response_model=MedicineBatchResponse)
def create_batch_endpoint(data: MedicineBatchCreate, db: Session = Depends(get_db)):
    return create_batch(db, data)


@routerBatch.get("/all", response_model=list[MedicineBatchResponse])
def list_batches(db: Session = Depends(get_db)):
    return get_batches(db)


@routerBatch.get("/{batch_id}", response_model=MedicineBatchResponse)
def get_batch_endpoint(batch_id: int, db: Session = Depends(get_db)):
    batch = get_batch(db, batch_id)
    if not batch:
        raise HTTPException(404, "Batch not found")
    return batch


@routerBatch.put("/{batch_id}", response_model=MedicineBatchResponse)
def update_batch_endpoint(batch_id: int, data: MedicineBatchUpdate, db: Session = Depends(get_db)):
    updated = update_batch(db, batch_id, data)
    if not updated:
        raise HTTPException(404, "Batch not found")
    return updated


@routerBatch.delete("/{batch_id}")
def delete_batch_endpoint(batch_id: int, db: Session = Depends(get_db)):
    deleted = delete_batch(db, batch_id)
    if not deleted:
        raise HTTPException(404, "Batch not found")
    return {"message": "Batch deleted successfully"}

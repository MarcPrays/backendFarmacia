from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import SupplierCreate, SupplierUpdate, SupplierResponse
from crud.suppliers import (
    create_supplier,
    get_suppliers,
    get_supplier,
    update_supplier,
    delete_supplier
)

routerSupplier = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@routerSupplier.post("/", response_model=SupplierResponse)
def create(data: SupplierCreate, db: Session = Depends(get_db)):
    return create_supplier(db, data)


@routerSupplier.get("/all", response_model=list[SupplierResponse])
def list_all(search: str = None, db: Session = Depends(get_db)):
    """Listar proveedores con capacidad de búsqueda"""
    return get_suppliers(db, search=search)


@routerSupplier.get("/", response_model=SupplierResponse)
def get(supplier_id: int, db: Session = Depends(get_db)):
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    return supplier


@routerSupplier.put("/", response_model=SupplierResponse)
def update(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    updated = update_supplier(db, supplier_id, data)
    if not updated:
        raise HTTPException(404, "Supplier not found")
    return updated


@routerSupplier.delete("/")
def delete(supplier_id: int, db: Session = Depends(get_db)):
    deleted = delete_supplier(db, supplier_id)
    if not deleted:
        raise HTTPException(404, "Supplier not found")
    return {"message": "Supplier deleted successfully"}

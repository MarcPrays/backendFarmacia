from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import ProductCreate, ProductUpdate, ProductResponse
from crud.products import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product
)

routerProducto = APIRouter(prefix="/products", tags=["Products"])


@routerProducto.post("/", response_model=ProductResponse)
def create(data: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, data)


@routerProducto.get("/", response_model=list[ProductResponse])
def list_all(db: Session = Depends(get_db)):
    return get_products(db)


@routerProducto.get("/", response_model=ProductResponse)
def get(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@routerProducto.put("/", response_model=ProductResponse)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    updated = update_product(db, product_id, data)
    if not updated:
        raise HTTPException(404, "Product not found")
    return updated


@routerProducto.delete("/")
def delete(product_id: int, db: Session = Depends(get_db)):
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted successfully"}

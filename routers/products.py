from datetime import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from crud.products import create_product, delete_product, get_product, get_products, update_product
import shutil
import uuid
import os

from db.schemas import ProductCreate, ProductResponse, ProductUpdate

routerProduct = APIRouter(prefix="/products", tags=["Products"])


@routerProduct.post("/", response_model=ProductResponse)
def create(
    name: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    presentation: str = Form(...),
    concentration: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    image_path = None

    # if image:
    #     folder = "uploads/products"
    #     os.makedirs(folder, exist_ok=True)

    #     extension = image.filename.split(".")[-1]
    #     #filename = f"{int(time.time())}.{extension}"

    #     filepath = os.path.join(folder)

    #     with open(filepath, "wb") as f:
    #         f.write(image.file.read())

    #     image_path = filepath


    if image:
        upload_dir = "uploads/products"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{image.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = file_path

    data = ProductCreate(
        name=name,
        description=description,
        category_id=category_id,
        presentation=presentation,
        concentration=concentration,
        image=image_path
    )

    return create_product(db, data)



@routerProduct.get("/all", response_model=list[ProductResponse])
def list_all(db: Session = Depends(get_db)):
    return get_products(db)


@routerProduct.get("/", response_model=ProductResponse)
def get(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@routerProduct.put("/", response_model=ProductResponse)
def update(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    category_id: int = Form(None),
    presentation: str = Form(None),
    concentration: str = Form(None),
    status: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    existing = get_product(db, product_id)
    if not existing:
        raise HTTPException(404, "Product not found")

    image_path = existing.image

    if image:
        folder = "uploads/products"
        os.makedirs(folder, exist_ok=True)

        extension = image.filename.split(".")[-1]
        filename = f"{int(time.time())}.{extension}"

        filepath = os.path.join(folder, filename)

        with open(filepath, "wb") as f:
            f.write(image.file.read())

        image_path = filepath

    data = ProductUpdate(
        name=name,
        description=description,
        category_id=category_id,
        presentation=presentation,
        concentration=concentration,
        status=status,
        image=image_path
    )

    updated = update_product(db, product_id, data)

    return updated


@routerProduct.delete("/")
def delete(product_id: int, db: Session = Depends(get_db)):
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted successfully"}

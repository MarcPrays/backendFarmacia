from datetime import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from crud.products import create_product, get_products, update_product, delete_product, get_product
from db.schemas import ProductCreate, ProductResponse, ProductUpdate
import shutil
import os
import re
from pathlib import Path

routerProduct = APIRouter(prefix="/products", tags=["Products"])

# Carpeta base para subidas (relativa al proyecto)
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Elimina caracteres peligrosos y espacios del nombre de archivo."""
    # Reemplazar espacios y guiones por guiones bajos
    safe_name = re.sub(r"[^\w\.-]", "_", filename)
    # Eliminar múltiples guiones bajos
    safe_name = re.sub(r"_+", "_", safe_name)
    return safe_name.strip("._")

@routerProduct.post("/create", response_model=ProductResponse)
def create_product_endpoint(
    name: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    presentation: str = Form(...),
    concentration: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_path_in_db = None  # Ruta que se guardará en la base de datos

    if image:
        #  Validar tipo de archivo
        if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPG o PNG.")

        #  Nombre seguro
        safe_filename = sanitize_filename(image.filename)
        
        #  Evitar colisiones: añadir UUID si el archivo ya existe
        stem = Path(safe_filename).stem
        suffix = Path(safe_filename).suffix
        unique_filename = f"{stem}_{uuid.uuid4().hex}{suffix}"
        
        #  Ruta completa en el sistema de archivos
        file_path = UPLOAD_DIR / unique_filename

        #  Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        #  Guardar SOLO la ruta relativa desde la raíz del proyecto
        # Ej: "uploads/products/paracetamol_abc123.jpg"
        image_path_in_db = f"uploads/products/{unique_filename}"

    #  Crear el objeto Pydantic
    product_data = ProductCreate(
        name=name,
        description=description,
        category_id=category_id,
        presentation=presentation,
        concentration=concentration,
        image=image_path_in_db  # Puede ser None o string
    )

    return create_product(db, product_data)



@routerProduct.get("/all", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return get_products(db)


@routerProduct.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@routerProduct.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
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
        folder = UPLOAD_DIR
        os.makedirs(folder, exist_ok=True)

        safe_filename = sanitize_filename(image.filename)
        stem = Path(safe_filename).stem
        suffix = Path(safe_filename).suffix
        filename = f"{stem}_{uuid.uuid4().hex}{suffix}"

        filepath = folder / filename

        with open(filepath, "wb") as f:
            shutil.copyfileobj(image.file, f)

        image_path = f"uploads/products/{filename}"

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


@routerProduct.delete("/{product_id}")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted successfully"}

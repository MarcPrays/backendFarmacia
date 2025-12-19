from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from crud.categories import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category
)

routerCategory = APIRouter(prefix="/categories", tags=["Categories"])


@routerCategory.post("/", response_model=CategoryResponse)
def create(data: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, data)


@routerCategory.get("/all", response_model=list[CategoryResponse])
def list_all(db: Session = Depends(get_db)):
    try:
        return get_categories(db)
    except Exception as e:
        from sqlalchemy.exc import OperationalError
        if isinstance(e, OperationalError) or "Can't connect" in str(e) or "Lost connection" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Servicio de base de datos no disponible. Verifica que MySQL esté corriendo."
            )
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")


@routerCategory.get("/", response_model=CategoryResponse)
def get(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    return category


@routerCategory.put("/", response_model=CategoryResponse)
def update(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    updated = update_category(db, category_id, data)
    if not updated:
        raise HTTPException(404, "Category not found")
    return updated


@routerCategory.delete("/")
def delete(category_id: int, db: Session = Depends(get_db)):
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(404, "Category not found")
    return {"message": "Category deleted successfully"}

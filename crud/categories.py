from sqlalchemy.orm import Session
from db.models import Category
from db.schemas import CategoryCreate, CategoryUpdate


def create_category(db: Session, data: CategoryCreate):
    category = Category(
        name=data.name,
        description=data.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()


def update_category(db: Session, category_id: int, data: CategoryUpdate):
    category = get_category(db, category_id)
    if not category:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = get_category(db, category_id)
    if not category:
        return False

    db.delete(category)
    db.commit()
    return True

from sqlalchemy.orm import Session
from db.models import User
from db.schemas import UserCreate, UserUpdate
from utils.security import get_password_hash


def create_user(db: Session, data: UserCreate):
    user = User(
        role_id=data.role_id,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,   # NUEVO
        email=data.email,
        #password=get_password_hash(data.password)  # ENCRIPTAR
        password=data.password

    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session):
    return db.query(User).filter(User.status == 1).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False

    user.status = 0
    db.commit()
    return True

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


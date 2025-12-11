from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.schemas import UserCreate, UserUpdate, UserResponse
from crud.users import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user
)

routerUser = APIRouter(prefix="/users", tags=["Users"])


@routerUser.post("/", response_model=UserResponse)
def create_user_endpoint(data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, data)


@routerUser.get("/all", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return get_users(db)


@routerUser.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@routerUser.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    updated = update_user(db, user_id, data)
    if not updated:
        raise HTTPException(404, "User not found")
    return updated


@routerUser.delete("/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(404, "User not found")
    return {"message": "User deleted successfully"}

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
from utils.auth import get_current_user
from utils.permissions import check_permission
from db.models import User

routerUser = APIRouter(prefix="/users", tags=["Users"])


@routerUser.post("/", response_model=UserResponse)
def create(
    data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear usuario - Requiere permiso users.create"""
    check_permission(db, current_user, "users.create")
    try:
        from sqlalchemy.orm import joinedload
        user = create_user(db, data)
        # Cargar el rol para incluir role_name en la respuesta
        user = db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()
        return UserResponse(
            id=user.id,
            role_id=user.role_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            status=user.status,
            role_name=user.role.name if user.role else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {str(e)}")


@routerUser.get("/all", response_model=list[UserResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar usuarios - Requiere permiso users.view"""
    check_permission(db, current_user, "users.view")
    return get_users(db)


@routerUser.get("/", response_model=UserResponse)
def get(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener usuario por ID - Requiere permiso users.view"""
    check_permission(db, current_user, "users.view")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@routerUser.put("/", response_model=UserResponse)
def update(
    user_id: int, 
    data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar usuario - Requiere permiso users.edit"""
    check_permission(db, current_user, "users.edit")
    try:
        from sqlalchemy.orm import joinedload
        updated = update_user(db, user_id, data)
        if not updated:
            raise HTTPException(404, "User not found")
        
        # Cargar el rol para incluir role_name en la respuesta
        user = db.query(User).options(joinedload(User.role)).filter(User.id == updated.id).first()
        return UserResponse(
            id=user.id,
            role_id=user.role_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            status=user.status,
            role_name=user.role.name if user.role else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el usuario: {str(e)}")


@routerUser.delete("/")
def delete(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar usuario - Requiere permiso users.delete"""
    check_permission(db, current_user, "users.delete")
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(404, "User not found")
    return {"message": "User deleted successfully"}

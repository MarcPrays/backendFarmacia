from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import User, Role
from db.schemas import UserCreate, UserUpdate
from utils.security import get_password_hash


def create_user(db: Session, data: UserCreate):
    # Verificar que el rol existe
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise ValueError(f"El rol con ID {data.role_id} no existe")
    
    # Verificar que el username no exista
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise ValueError(f"El usuario '{data.username}' ya existe")
    
    # Verificar que el email no exista
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise ValueError(f"El email '{data.email}' ya está registrado")
    
    try:
        user = User(
            role_id=data.role_id,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            password=get_password_hash(data.password)  # ENCRIPTAR contraseña
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "username" in error_msg.lower():
            raise ValueError(f"El usuario '{data.username}' ya existe")
        elif "email" in error_msg.lower():
            raise ValueError(f"El email '{data.email}' ya está registrado")
        elif "foreign key constraint" in error_msg.lower():
            raise ValueError(f"El rol con ID {data.role_id} no existe")
        raise ValueError(f"Error al crear el usuario: {error_msg}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error inesperado al crear el usuario: {str(e)}")


def get_users(db: Session):
    return db.query(User).filter(User.status == 1).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, data: UserUpdate):
    from sqlalchemy.exc import IntegrityError
    
    user = get_user(db, user_id)
    if not user:
        return None

    # Obtener solo los campos que se proporcionaron (excluir None y campos no establecidos)
    update_data = data.dict(exclude_unset=True, exclude_none=True)
    
    # Verificar que el username no exista (si se está actualizando)
    if 'username' in update_data and update_data['username'] != user.username:
        existing_user = db.query(User).filter(User.username == update_data['username']).first()
        if existing_user:
            raise ValueError(f"El usuario '{update_data['username']}' ya existe")
    
    # Verificar que el email no exista (si se está actualizando)
    if 'email' in update_data and update_data['email'] != user.email:
        existing_email = db.query(User).filter(User.email == update_data['email']).first()
        if existing_email:
            raise ValueError(f"El email '{update_data['email']}' ya está registrado")
    
    # Verificar que el rol existe (si se está actualizando)
    if 'role_id' in update_data:
        from db.models import Role
        role = db.query(Role).filter(Role.id == update_data['role_id']).first()
        if not role:
            raise ValueError(f"El rol con ID {update_data['role_id']} no existe")
    
    # Si se proporciona contraseña, encriptarla
    if 'password' in update_data and update_data['password']:
        update_data['password'] = get_password_hash(update_data['password'])
    elif 'password' in update_data and not update_data['password']:
        # Si se envía password vacío, no actualizarlo
        del update_data['password']
    
    try:
        # Actualizar solo los campos proporcionados
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "username" in error_msg.lower():
            raise ValueError(f"El usuario '{update_data.get('username', '')}' ya existe")
        elif "email" in error_msg.lower():
            raise ValueError(f"El email '{update_data.get('email', '')}' ya está registrado")
        elif "foreign key constraint" in error_msg.lower():
            raise ValueError(f"El rol con ID {update_data.get('role_id', '')} no existe")
        raise ValueError(f"Error al actualizar el usuario: {error_msg}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error inesperado al actualizar el usuario: {str(e)}")


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False

    user.status = 0
    db.commit()
    return True

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


    return db.query(User).filter(User.username == username).first()


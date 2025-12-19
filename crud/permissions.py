from sqlalchemy.orm import Session
from db.models import Permission


def create_permission(db: Session, name: str, description: str = None):
    """Crear un permiso"""
    existing = db.query(Permission).filter(Permission.name == name).first()
    if existing:
        raise ValueError(f"El permiso '{name}' ya existe")
    
    permission = Permission(name=name, description=description, status=1)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def get_permissions(db: Session):
    """Obtener todos los permisos"""
    return db.query(Permission).filter(Permission.status == 1).all()


def get_permission(db: Session, permission_id: int):
    """Obtener un permiso por ID"""
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str):
    """Obtener un permiso por nombre"""
    return db.query(Permission).filter(Permission.name == name).first()


def update_permission(db: Session, permission_id: int, name: str = None, description: str = None):
    """Actualizar un permiso"""
    permission = get_permission(db, permission_id)
    if not permission:
        return None
    
    if name:
        permission.name = name
    if description is not None:
        permission.description = description
    
    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db: Session, permission_id: int) -> bool:
    """Eliminar un permiso (borrado lógico)"""
    permission = get_permission(db, permission_id)
    if not permission:
        return False
    
    permission.status = 0
    db.commit()
    return True


from db.models import Permission


def create_permission(db: Session, name: str, description: str = None):
    """Crear un permiso"""
    existing = db.query(Permission).filter(Permission.name == name).first()
    if existing:
        raise ValueError(f"El permiso '{name}' ya existe")
    
    permission = Permission(name=name, description=description, status=1)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def get_permissions(db: Session):
    """Obtener todos los permisos"""
    return db.query(Permission).filter(Permission.status == 1).all()


def get_permission(db: Session, permission_id: int):
    """Obtener un permiso por ID"""
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str):
    """Obtener un permiso por nombre"""
    return db.query(Permission).filter(Permission.name == name).first()


def update_permission(db: Session, permission_id: int, name: str = None, description: str = None):
    """Actualizar un permiso"""
    permission = get_permission(db, permission_id)
    if not permission:
        return None
    
    if name:
        permission.name = name
    if description is not None:
        permission.description = description
    
    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db: Session, permission_id: int) -> bool:
    """Eliminar un permiso (borrado lógico)"""
    permission = get_permission(db, permission_id)
    if not permission:
        return False
    
    permission.status = 0
    db.commit()
    return True



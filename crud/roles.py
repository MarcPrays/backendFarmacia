from sqlalchemy.orm import Session
from db.models import Role, Permission, RolePermission
from db.schemas import RoleCreate, RoleUpdate


def create_role(db: Session, name: str):
    """Crear un rol"""
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise ValueError(f"El rol '{name}' ya existe")
    
    role = Role(name=name, status=1)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_roles(db: Session):
    """Obtener todos los roles"""
    return db.query(Role).filter(Role.status == 1).all()


def get_role(db: Session, role_id: int):
    """Obtener un rol por ID"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    """Obtener un rol por nombre"""
    return db.query(Role).filter(Role.name == name).first()


def update_role(db: Session, role_id: int, name: str):
    """Actualizar un rol"""
    role = get_role(db, role_id)
    if not role:
        return None
    
    role.name = name
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    """Eliminar un rol (borrado lógico)"""
    role = get_role(db, role_id)
    if not role:
        return False
    
    role.status = 0
    db.commit()
    return True


def assign_permission_to_role(db: Session, role_id: int, permission_id: int):
    """Asignar un permiso a un rol"""
    # Verificar que no exista ya
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if existing:
        return existing
    
    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)
    return role_permission


def remove_permission_from_role(db: Session, role_id: int, permission_id: int):
    """Quitar un permiso de un rol"""
    role_permission = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if not role_permission:
        return False
    
    db.delete(role_permission)
    db.commit()
    return True


def get_role_permissions(db: Session, role_id: int):
    """Obtener todos los permisos de un rol"""
    role = get_role(db, role_id)
    if not role:
        return []
    
    return [perm for perm in role.permissions if perm.status == 1]


from db.models import Role, Permission, RolePermission
from db.schemas import RoleCreate, RoleUpdate


def create_role(db: Session, name: str):
    """Crear un rol"""
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise ValueError(f"El rol '{name}' ya existe")
    
    role = Role(name=name, status=1)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_roles(db: Session):
    """Obtener todos los roles"""
    return db.query(Role).filter(Role.status == 1).all()


def get_role(db: Session, role_id: int):
    """Obtener un rol por ID"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    """Obtener un rol por nombre"""
    return db.query(Role).filter(Role.name == name).first()


def update_role(db: Session, role_id: int, name: str):
    """Actualizar un rol"""
    role = get_role(db, role_id)
    if not role:
        return None
    
    role.name = name
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    """Eliminar un rol (borrado lógico)"""
    role = get_role(db, role_id)
    if not role:
        return False
    
    role.status = 0
    db.commit()
    return True


def assign_permission_to_role(db: Session, role_id: int, permission_id: int):
    """Asignar un permiso a un rol"""
    # Verificar que no exista ya
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if existing:
        return existing
    
    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)
    return role_permission


def remove_permission_from_role(db: Session, role_id: int, permission_id: int):
    """Quitar un permiso de un rol"""
    role_permission = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if not role_permission:
        return False
    
    db.delete(role_permission)
    db.commit()
    return True


def get_role_permissions(db: Session, role_id: int):
    """Obtener todos los permisos de un rol"""
    role = get_role(db, role_id)
    if not role:
        return []
    
    return [perm for perm in role.permissions if perm.status == 1]



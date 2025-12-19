"""
Script para crear roles, permisos y usuarios del sistema
Ejecutar: python create_roles_and_users.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from db.database import SessionLocal
from db.models import Role, Permission, RolePermission, User
from crud.roles import create_role, get_role_by_name, assign_permission_to_role
from crud.permissions import create_permission, get_permission_by_name
from crud.users import create_user
from utils.security import get_password_hash
from utils.permissions import PERMISSIONS, ROLE_PERMISSIONS

def create_all_permissions(db):
    """Crear todos los permisos del sistema"""
    print("Creando permisos...")
    created = 0
    for perm_name, perm_desc in PERMISSIONS.items():
        existing = get_permission_by_name(db, perm_name)
        if not existing:
            create_permission(db, perm_name, perm_desc)
            created += 1
            print(f"  ✓ Permiso creado: {perm_name}")
        else:
            print(f"  - Permiso ya existe: {perm_name}")
    print(f"Total permisos: {created} nuevos\n")
    return created


def create_all_roles(db):
    """Crear todos los roles del sistema"""
    print("Creando roles...")
    roles = {}
    for role_name in ["Administrador", "Farmacéutico", "Cajero"]:
        existing = get_role_by_name(db, role_name)
        if not existing:
            role = create_role(db, role_name)
            roles[role_name] = role
            print(f"  ✓ Rol creado: {role_name} (ID: {role.id})")
        else:
            roles[role_name] = existing
            print(f"  - Rol ya existe: {role_name} (ID: {existing.id})")
    print()
    return roles


def assign_permissions_to_roles(db, roles):
    """Asignar permisos a los roles según ROLE_PERMISSIONS"""
    print("Asignando permisos a roles...")
    total_assignments = 0
    
    for role_name, permission_names in ROLE_PERMISSIONS.items():
        role = roles.get(role_name)
        if not role:
            print(f"  ✗ Rol no encontrado: {role_name}")
            continue
        
        print(f"\n  Asignando permisos a {role_name}:")
        for perm_name in permission_names:
            permission = get_permission_by_name(db, perm_name)
            if not permission:
                print(f"    ✗ Permiso no encontrado: {perm_name}")
                continue
            
            # Verificar si ya está asignado
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == permission.id
            ).first()
            
            if not existing:
                assign_permission_to_role(db, role.id, permission.id)
                total_assignments += 1
                print(f"    ✓ {perm_name}")
            else:
                print(f"    - Ya asignado: {perm_name}")
    
    print(f"\nTotal asignaciones: {total_assignments} nuevas\n")
    return total_assignments


def create_users(db, roles):
    """Crear usuarios de ejemplo para cada rol"""
    print("Creando usuarios...")
    
    users_data = [
        {
            "role_name": "Administrador",
            "username": "admin",
            "password": "admin123",
            "first_name": "Administrador",
            "last_name": "Sistema",
            "email": "admin@sistema.com"
        },
        {
            "role_name": "Farmacéutico",
            "username": "farmaceutico",
            "password": "farma123",
            "first_name": "Juan",
            "last_name": "Farmacéutico",
            "email": "farmaceutico@sistema.com"
        },
        {
            "role_name": "Cajero",
            "username": "cajero",
            "password": "cajero123",
            "first_name": "María",
            "last_name": "Cajero",
            "email": "cajero@sistema.com"
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        role = roles.get(user_data["role_name"])
        if not role:
            print(f"  ✗ Rol no encontrado: {user_data['role_name']}")
            continue
        
        # Verificar si el usuario ya existe
        from db.models import User
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        
        if existing:
            print(f"  - Usuario ya existe: {user_data['username']}")
            created_users.append({
                "username": user_data["username"],
                "password": user_data["password"],
                "role": user_data["role_name"]
            })
            continue
        
        try:
            from db.schemas import UserCreate
            user_create = UserCreate(
                role_id=role.id,
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password=user_data["password"]
            )
            user = create_user(db, user_create)
            
            created_users.append({
                "username": user_data["username"],
                "password": user_data["password"],
                "role": user_data["role_name"]
            })
            print(f"  ✓ Usuario creado: {user_data['username']} ({user_data['role_name']})")
        except Exception as e:
            print(f"  ✗ Error al crear usuario {user_data['username']}: {e}")
    
    print()
    return created_users


def main():
    print("=" * 60)
    print("CREACIÓN DE ROLES, PERMISOS Y USUARIOS")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # 1. Crear permisos
        create_all_permissions(db)
        
        # 2. Crear roles
        roles = create_all_roles(db)
        
        # 3. Asignar permisos a roles
        assign_permissions_to_roles(db, roles)
        
        # 4. Crear usuarios
        users = create_users(db, roles)
        
        print("=" * 60)
        print("✓ PROCESO COMPLETADO")
        print("=" * 60)
        print("\n📋 CREDENCIALES DE USUARIOS:")
        print("-" * 60)
        for user in users:
            print(f"\nRol: {user['role']}")
            print(f"  Usuario: {user['username']}")
            print(f"  Contraseña: {user['password']}")
        print("\n" + "=" * 60)
        print("✅ Sistema de roles y permisos configurado correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()


Ejecutar: python create_roles_and_users.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from db.database import SessionLocal
from db.models import Role, Permission, RolePermission, User
from crud.roles import create_role, get_role_by_name, assign_permission_to_role
from crud.permissions import create_permission, get_permission_by_name
from crud.users import create_user
from utils.security import get_password_hash
from utils.permissions import PERMISSIONS, ROLE_PERMISSIONS

def create_all_permissions(db):
    """Crear todos los permisos del sistema"""
    print("Creando permisos...")
    created = 0
    for perm_name, perm_desc in PERMISSIONS.items():
        existing = get_permission_by_name(db, perm_name)
        if not existing:
            create_permission(db, perm_name, perm_desc)
            created += 1
            print(f"  ✓ Permiso creado: {perm_name}")
        else:
            print(f"  - Permiso ya existe: {perm_name}")
    print(f"Total permisos: {created} nuevos\n")
    return created


def create_all_roles(db):
    """Crear todos los roles del sistema"""
    print("Creando roles...")
    roles = {}
    for role_name in ["Administrador", "Farmacéutico", "Cajero"]:
        existing = get_role_by_name(db, role_name)
        if not existing:
            role = create_role(db, role_name)
            roles[role_name] = role
            print(f"  ✓ Rol creado: {role_name} (ID: {role.id})")
        else:
            roles[role_name] = existing
            print(f"  - Rol ya existe: {role_name} (ID: {existing.id})")
    print()
    return roles


def assign_permissions_to_roles(db, roles):
    """Asignar permisos a los roles según ROLE_PERMISSIONS"""
    print("Asignando permisos a roles...")
    total_assignments = 0
    
    for role_name, permission_names in ROLE_PERMISSIONS.items():
        role = roles.get(role_name)
        if not role:
            print(f"  ✗ Rol no encontrado: {role_name}")
            continue
        
        print(f"\n  Asignando permisos a {role_name}:")
        for perm_name in permission_names:
            permission = get_permission_by_name(db, perm_name)
            if not permission:
                print(f"    ✗ Permiso no encontrado: {perm_name}")
                continue
            
            # Verificar si ya está asignado
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == permission.id
            ).first()
            
            if not existing:
                assign_permission_to_role(db, role.id, permission.id)
                total_assignments += 1
                print(f"    ✓ {perm_name}")
            else:
                print(f"    - Ya asignado: {perm_name}")
    
    print(f"\nTotal asignaciones: {total_assignments} nuevas\n")
    return total_assignments


def create_users(db, roles):
    """Crear usuarios de ejemplo para cada rol"""
    print("Creando usuarios...")
    
    users_data = [
        {
            "role_name": "Administrador",
            "username": "admin",
            "password": "admin123",
            "first_name": "Administrador",
            "last_name": "Sistema",
            "email": "admin@sistema.com"
        },
        {
            "role_name": "Farmacéutico",
            "username": "farmaceutico",
            "password": "farma123",
            "first_name": "Juan",
            "last_name": "Farmacéutico",
            "email": "farmaceutico@sistema.com"
        },
        {
            "role_name": "Cajero",
            "username": "cajero",
            "password": "cajero123",
            "first_name": "María",
            "last_name": "Cajero",
            "email": "cajero@sistema.com"
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        role = roles.get(user_data["role_name"])
        if not role:
            print(f"  ✗ Rol no encontrado: {user_data['role_name']}")
            continue
        
        # Verificar si el usuario ya existe
        from db.models import User
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        
        if existing:
            print(f"  - Usuario ya existe: {user_data['username']}")
            created_users.append({
                "username": user_data["username"],
                "password": user_data["password"],
                "role": user_data["role_name"]
            })
            continue
        
        try:
            from db.schemas import UserCreate
            user_create = UserCreate(
                role_id=role.id,
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password=user_data["password"]
            )
            user = create_user(db, user_create)
            
            created_users.append({
                "username": user_data["username"],
                "password": user_data["password"],
                "role": user_data["role_name"]
            })
            print(f"  ✓ Usuario creado: {user_data['username']} ({user_data['role_name']})")
        except Exception as e:
            print(f"  ✗ Error al crear usuario {user_data['username']}: {e}")
    
    print()
    return created_users


def main():
    print("=" * 60)
    print("CREACIÓN DE ROLES, PERMISOS Y USUARIOS")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # 1. Crear permisos
        create_all_permissions(db)
        
        # 2. Crear roles
        roles = create_all_roles(db)
        
        # 3. Asignar permisos a roles
        assign_permissions_to_roles(db, roles)
        
        # 4. Crear usuarios
        users = create_users(db, roles)
        
        print("=" * 60)
        print("✓ PROCESO COMPLETADO")
        print("=" * 60)
        print("\n📋 CREDENCIALES DE USUARIOS:")
        print("-" * 60)
        for user in users:
            print(f"\nRol: {user['role']}")
            print(f"  Usuario: {user['username']}")
            print(f"  Contraseña: {user['password']}")
        print("\n" + "=" * 60)
        print("✅ Sistema de roles y permisos configurado correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()


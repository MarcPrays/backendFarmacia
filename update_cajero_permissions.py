"""
Script para actualizar los permisos del rol Cajero en la base de datos
Ejecutar: python update_cajero_permissions.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from db.database import SessionLocal
from db.models import Role, Permission, RolePermission
from crud.roles import get_role_by_name, assign_permission_to_role
from crud.permissions import get_permission_by_name
from utils.permissions import ROLE_PERMISSIONS

def update_cajero_permissions(db):
    """Actualizar permisos del rol Cajero según ROLE_PERMISSIONS"""
    print("=" * 60)
    print("ACTUALIZANDO PERMISOS DEL ROL CAJERO")
    print("=" * 60)
    print()
    
    # Obtener rol Cajero
    role = get_role_by_name(db, "Cajero")
    if not role:
        print("❌ ERROR: El rol 'Cajero' no existe en la base de datos")
        print("   Por favor, ejecuta primero: python create_roles_and_users.py")
        return False
    
    print(f"✓ Rol encontrado: Cajero (ID: {role.id})")
    print()
    
    # Obtener permisos que debe tener según ROLE_PERMISSIONS
    cajero_permissions = ROLE_PERMISSIONS.get("Cajero", [])
    if not cajero_permissions:
        print("❌ ERROR: No se encontraron permisos para el rol 'Cajero' en ROLE_PERMISSIONS")
        return False
    
    print(f"Permisos que debe tener el rol Cajero: {len(cajero_permissions)}")
    print()
    
    # Obtener permisos actuales del rol
    current_permissions = [perm.name for perm in role.permissions if perm.status == 1]
    print(f"Permisos actuales en BD: {len(current_permissions)}")
    print(f"  {', '.join(current_permissions)}")
    print()
    
    # Asignar permisos faltantes
    print("Asignando permisos...")
    assigned = 0
    removed = 0
    
    # Permisos que DEBE tener
    for perm_name in cajero_permissions:
        permission = get_permission_by_name(db, perm_name)
        if not permission:
            print(f"  ⚠ Permiso no encontrado en BD: {perm_name}")
            continue
        
        # Verificar si ya está asignado
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id
        ).first()
        
        if not existing:
            assign_permission_to_role(db, role.id, permission.id)
            assigned += 1
            print(f"  ✓ Asignado: {perm_name}")
        else:
            print(f"  - Ya asignado: {perm_name}")
    
    # Remover permisos que NO debe tener (opcional, comentado por seguridad)
    # Solo remover si está explícitamente fuera de la lista
    # for current_perm in current_permissions:
    #     if current_perm not in cajero_permissions:
    #         # Remover permiso
    #         permission = get_permission_by_name(db, current_perm)
    #         if permission:
    #             db.query(RolePermission).filter(
    #                 RolePermission.role_id == role.id,
    #                 RolePermission.permission_id == permission.id
    #             ).delete()
    #             removed += 1
    #             print(f"  ✗ Removido: {current_perm}")
    
    db.commit()
    
    print()
    print("=" * 60)
    print(f"✓ PROCESO COMPLETADO")
    print(f"  Permisos asignados: {assigned}")
    print(f"  Permisos removidos: {removed}")
    print("=" * 60)
    print()
    
    # Verificar permisos finales
    db.refresh(role)
    final_permissions = [perm.name for perm in role.permissions if perm.status == 1]
    print("Permisos finales del rol Cajero:")
    for perm in final_permissions:
        print(f"  ✓ {perm}")
    print()
    
    # Verificar específicamente los permisos de clientes
    client_permissions = [p for p in final_permissions if 'client' in p]
    print("Permisos de clientes:")
    if client_permissions:
        for perm in client_permissions:
            print(f"  ✓ {perm}")
    else:
        print("  ❌ No se encontraron permisos de clientes")
    
    print()
    return True


def main():
    db = SessionLocal()
    try:
        success = update_cajero_permissions(db)
        if success:
            print("✅ Los permisos del rol Cajero han sido actualizados correctamente")
            print()
            print("Los permisos de clientes ahora están activos:")
            print("  - clients.create")
            print("  - clients.edit")
            print("  - clients.delete")
            print("  - clients.view")
        else:
            print("❌ Error al actualizar permisos")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()



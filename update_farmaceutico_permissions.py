"""
Script para actualizar los permisos del rol Farmacéutico
Agrega permisos de editar y eliminar productos
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from db.database import SessionLocal
from crud.roles import get_role_by_name, assign_permission_to_role, get_role_permissions
from crud.permissions import get_permission_by_name
from utils.permissions import ROLE_PERMISSIONS

def update_farmaceutico_permissions_in_db():
    db = SessionLocal()
    try:
        print("============================================================")
        print("ACTUALIZANDO PERMISOS DEL ROL FARMACÉUTICO")
        print("============================================================")

        farmaceutico_role = get_role_by_name(db, "Farmacéutico")
        if not farmaceutico_role:
            print("✗ Rol 'Farmacéutico' no encontrado.")
            return

        print(f"✓ Rol encontrado: {farmaceutico_role.name} (ID: {farmaceutico_role.id})\n")

        # Permisos deseados para Farmacéutico (según ROLE_PERMISSIONS en utils/permissions.py)
        desired_permissions = ROLE_PERMISSIONS.get("Farmacéutico", [])
        
        # Obtener permisos actuales del Farmacéutico
        current_permissions_obj = get_role_permissions(db, farmaceutico_role.id)
        current_permission_names = {p.name for p in current_permissions_obj}

        print(f"Permisos que debe tener el rol Farmacéutico: {len(desired_permissions)}")
        print(f"Permisos actuales en BD: {len(current_permission_names)}\n")

        assigned_count = 0
        removed_count = 0

        print("Asignando permisos...")
        for perm_name in desired_permissions:
            permission = get_permission_by_name(db, perm_name)
            if not permission:
                print(f"  ✗ Permiso no encontrado: {perm_name}")
                continue
            if perm_name not in current_permission_names:
                assign_permission_to_role(db, farmaceutico_role.id, permission.id)
                assigned_count += 1
                print(f"  ✓ Asignado: {perm_name}")
            else:
                print(f"  - Ya asignado: {perm_name}")

        # Remover permisos que ya no deberían estar
        print("\nRemoviendo permisos obsoletos...")
        for perm_name in current_permission_names:
            if perm_name not in desired_permissions:
                permission = get_permission_by_name(db, perm_name)
                if permission:
                    from crud.roles import remove_permission_from_role
                    remove_permission_from_role(db, farmaceutico_role.id, permission.id)
                    removed_count += 1
                    print(f"  ✗ Removido: {perm_name}")

        db.commit()

        print("\n============================================================")
        print("✓ PROCESO COMPLETADO")
        print(f"  Permisos asignados: {assigned_count}")
        print(f"  Permisos removidos: {removed_count}")
        print("============================================================\n")

        # Verificar permisos finales
        final_permissions_obj = get_role_permissions(db, farmaceutico_role.id)
        final_permission_names = {p.name for p in final_permissions_obj}
        print("Permisos finales del rol Farmacéutico:")
        for p_name in sorted(list(final_permission_names)):
            print(f"  ✓ {p_name}")
        
        print("\nPermisos de productos del Farmacéutico:")
        for p_name in sorted(list(final_permission_names)):
            if 'product' in p_name:
                print(f"  ✓ {p_name}")

        print("\n✅ Los permisos del rol Farmacéutico han sido actualizados correctamente")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_farmaceutico_permissions_in_db()


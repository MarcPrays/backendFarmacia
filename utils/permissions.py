"""
Sistema de permisos basado en roles
Verifica permisos según el rol del usuario
"""
from fastapi import HTTPException, status
from db.models import User, Role, Permission
from sqlalchemy.orm import Session
from typing import List


# Definición de permisos del sistema
PERMISSIONS = {
    # Productos
    "products.create": "Crear productos",
    "products.edit": "Editar productos",
    "products.delete": "Eliminar productos",
    "products.view": "Ver productos",
    "products.stock": "Modificar stock de productos",
    "products.batches": "Gestionar lotes de productos",
    "products.expiration": "Gestionar fechas de vencimiento",
    
    # Alertas
    "alerts.create": "Crear alertas",
    "alerts.edit": "Editar alertas",
    "alerts.delete": "Eliminar alertas",
    "alerts.view": "Ver alertas",
    "alerts.config": "Configurar parámetros de alertas",
    
    # Usuarios
    "users.create": "Crear usuarios",
    "users.edit": "Editar usuarios",
    "users.delete": "Eliminar usuarios",
    "users.view": "Ver usuarios",
    "users.roles": "Asignar roles a usuarios",
    
    # Ventas
    "sales.create": "Crear ventas",
    "sales.edit": "Editar ventas",
    "sales.delete": "Eliminar ventas",
    "sales.view": "Ver ventas",
    "sales.modify": "Modificar ventas",
    
    # Clientes
    "clients.create": "Crear clientes",
    "clients.edit": "Editar clientes",
    "clients.delete": "Eliminar clientes",
    "clients.view": "Ver clientes",
    
    # Proveedores
    "suppliers.create": "Crear proveedores",
    "suppliers.edit": "Editar proveedores",
    "suppliers.delete": "Eliminar proveedores",
    "suppliers.view": "Ver proveedores",
    
    # Reportes
    "reports.full": "Ver reportes completos",
    "reports.limited": "Ver reportes limitados",
    "reports.export": "Exportar reportes",
    
    # Stock
    "stock.modify": "Modificar stock",
    "stock.view": "Ver stock",
    
    # Compras
    "purchases.create": "Crear compras",
    "purchases.view": "Ver compras",
}


def get_user_permissions(db: Session, user: User) -> List[str]:
    """
    Obtiene la lista de permisos del usuario basado en su rol
    """
    if not user or not user.role:
        return []
    
    # Cargar permisos del rol
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        return []
    
    # Obtener nombres de permisos
    permissions = [perm.name for perm in role.permissions if perm.status == 1]
    return permissions


def has_permission(db: Session, user: User, permission_name: str) -> bool:
    """
    Verifica si el usuario tiene un permiso específico
    """
    if not user:
        return False
    
    # Administrador tiene todos los permisos
    if user.role and user.role.name.lower() == "administrador":
        return True
    
    permissions = get_user_permissions(db, user)
    return permission_name in permissions


def require_permission(permission_name: str):
    """
    Decorador para verificar permisos en endpoints
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Buscar current_user en los argumentos
            current_user = None
            db = None
            
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                elif hasattr(arg, 'query'):  # Es una Session de SQLAlchemy
                    db = arg
            
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                elif hasattr(value, 'query'):
                    db = value
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not db:
                # Intentar obtener db de los argumentos
                from db.database import get_db
                db = next(get_db())
            
            if not has_permission(db, current_user, permission_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tienes permiso para realizar esta acción. Se requiere: {PERMISSIONS.get(permission_name, permission_name)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_permission(db: Session, user: User, permission_name: str):
    """
    Verifica permiso y lanza excepción si no lo tiene
    """
    if not has_permission(db, user, permission_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes permiso para realizar esta acción. Se requiere: {PERMISSIONS.get(permission_name, permission_name)}"
        )


# Mapeo de roles a permisos - EXACTAMENTE según las especificaciones
ROLE_PERMISSIONS = {
    "Administrador": [
        # Gestión de productos: Crear, editar, eliminar productos
        "products.create", "products.edit", "products.delete", "products.view", "products.stock",
        "products.batches", "products.expiration",
        # Gestión de alertas: Crear, editar, eliminar alertas
        "alerts.create", "alerts.edit", "alerts.delete", "alerts.view", "alerts.config",
        # Gestión de usuarios: Crear, editar, eliminar usuarios
        "users.create", "users.edit", "users.delete", "users.view", "users.roles",
        # Gestión de ventas: Ver todas, eliminar o modificar ventas
        "sales.create", "sales.edit", "sales.delete", "sales.view", "sales.modify",
        # Gestión de clientes y proveedores: Crear, editar, eliminar
        "clients.create", "clients.edit", "clients.delete", "clients.view",
        "suppliers.create", "suppliers.edit", "suppliers.delete", "suppliers.view",
        # Gestión de stock: Controlar y modificar
        "stock.modify", "stock.view",
        # Ver y modificar reportes: Generar y visualizar reportes completos
        "reports.full", "reports.limited", "reports.export",
        # Compras
        "purchases.create", "purchases.view",
    ],
    "Farmacéutico": [
        # Gestión de productos: Consultar, ver detalles, actualizar stock, editar y eliminar productos
        # Crear nuevos lotes y asignar fechas de expiración
        # Puede editar productos (incluyendo precios) y eliminar productos
        "products.view", "products.edit", "products.delete", "products.stock", "products.batches", "products.expiration",
        # NO tiene: products.create (los productos se crean solo mediante compras)
        
        # Gestión de alertas: Consultar (NO crear/editar/eliminar/configurar)
        "alerts.view",
        
        # Gestión de ventas: Consultar (NO crear/eliminar/modificar)
        "sales.view",
        
        # Gestión de stock: Modificar stock, actualizar cantidades, gestionar entradas
        "stock.modify", "stock.view",
        
        # Gestión de clientes: Consultar (NO eliminar ni modificar información sensible)
        "clients.view",
        
        # Ver reportes limitados: Solo productos, stock y ventas (NO usuarios, finanzas, ventas globales)
        "reports.limited",
        
        # Compras
        "purchases.create", "purchases.view",
        
        # Limitaciones explícitas:
        # NO usuarios, NO proveedores, NO crear productos (solo mediante compras)
    ],
    "Cajero": [
        # Gestión de ventas: Crear y registrar nuevas ventas, ver productos, consultar historial
        # NO puede eliminar ni modificar ventas
        "sales.create", "sales.view",
        
        # Gestión de productos: Ver información básica (NO modificar/crear/eliminar/stock)
        "products.view",
        
        # Gestión de clientes: Crear, editar, eliminar y ver clientes
        # Útil durante el proceso de venta para registrar clientes nuevos
        "clients.create", "clients.edit", "clients.delete", "clients.view",
        
        # Ver alertas: Consultar (NO modificar ni configurar)
        "alerts.view",
        
        # Consultas de stock: Ver (NO modificar)
        "stock.view",
        
        # Ver reportes limitados: Solo resúmenes básicos de ventas (NO reportes completos)
        "reports.limited",
        
        # Limitaciones explícitas:
        # NO usuarios, NO proveedores, NO modificar productos/stock, NO gestionar alertas
    ]
}


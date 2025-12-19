from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from crud.dashboard import (
    get_all_dashboard_data,
    get_week_sales,
    get_active_clients_count,
    get_products_in_stock_count,
    get_low_stock_count,
    get_recent_sales,
    get_popular_products,
    get_financial_summary,
    get_last_7_days_sales,
    get_income_by_product_top,
    get_order_status_distribution
)
from utils.auth import get_current_user_optional
from db.models import User

routerDashboard = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@routerDashboard.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Obtiene todos los datos del dashboard en una sola llamada
    """
    try:
        return get_all_dashboard_data(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos del dashboard: {str(e)}")


@routerDashboard.get("/week-sales")
def week_sales(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene las ventas de la semana"""
    try:
        return get_week_sales(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas de la semana: {str(e)}")


@routerDashboard.get("/active-clients")
def active_clients(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene el número de clientes activos"""
    try:
        return {"active_clients": get_active_clients_count(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener clientes activos: {str(e)}")


@routerDashboard.get("/products-in-stock")
def products_in_stock(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene el número de productos en stock"""
    try:
        return {"products_in_stock": get_products_in_stock_count(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos en stock: {str(e)}")


@routerDashboard.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene el número de productos con stock bajo"""
    try:
        return {"low_stock_count": get_low_stock_count(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener stock bajo: {str(e)}")


@routerDashboard.get("/recent-sales")
def recent_sales(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene las ventas recientes"""
    try:
        return {"recent_sales": get_recent_sales(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas recientes: {str(e)}")


@routerDashboard.get("/popular-products")
def popular_products(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene los productos más populares"""
    try:
        return {"popular_products": get_popular_products(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos populares: {str(e)}")


@routerDashboard.get("/financial-summary")
def financial_summary(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene el resumen financiero"""
    try:
        return get_financial_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen financiero: {str(e)}")


@routerDashboard.get("/last-7-days-sales")
def last_7_days_sales(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene las ventas de los últimos 7 días"""
    try:
        return {"last_7_days_sales": get_last_7_days_sales(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas de últimos 7 días: {str(e)}")


@routerDashboard.get("/income-by-product")
def income_by_product(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene los productos con mayor ingreso"""
    try:
        return {"income_by_product_top": get_income_by_product_top(db)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ingresos por producto: {str(e)}")


@routerDashboard.get("/order-status-distribution")
def order_status_distribution(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Obtiene la distribución de métodos de pago"""
    try:
        return get_order_status_distribution(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener distribución de métodos de pago: {str(e)}")



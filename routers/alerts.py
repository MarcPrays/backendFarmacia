from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from db.schemas import AlertCreate, AlertResponse
from crud.alerts import (
    create_alert,
    get_alerts,
    get_expiration_alerts,
    get_low_stock_alerts,
    delete_alert
)
from utils.auth import get_current_user_optional
from db.models import User

routerAlert = APIRouter(prefix="/alerts", tags=["Alerts"])


@routerAlert.get("/expiration")
def get_expiration(
    days: int = Query(30, description="Días antes de la fecha de vencimiento"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF21: Generar alertas de productos próximos a vencer
    Retorna lotes que vencen en los próximos 'days' días
    """
    try:
        alerts = get_expiration_alerts(db, days=days)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas de vencimiento: {str(e)}")


@routerAlert.get("/low-stock")
def get_low_stock(
    min_stock: int = Query(10, description="Stock mínimo para considerar bajo stock"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF22: Generar alertas de productos con bajo stock
    Retorna lotes con stock menor o igual a 'min_stock'
    """
    try:
        alerts = get_low_stock_alerts(db, min_stock=min_stock)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas de stock bajo: {str(e)}")


@routerAlert.get("/", response_model=list[AlertResponse])
def list_all(
    alert_type: Optional[str] = Query(None, description="Tipo de alerta: 'expiration' o 'low_stock'"),
    batch_id: Optional[int] = Query(None, description="ID del lote"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Listar todas las alertas con filtros opcionales
    """
    try:
        return get_alerts(db, alert_type=alert_type, batch_id=batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas: {str(e)}")


@routerAlert.post("/", response_model=AlertResponse)
def create(data: AlertCreate, db: Session = Depends(get_db)):
    """
    Crear una alerta manualmente
    """
    try:
        return create_alert(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear alerta: {str(e)}")


@routerAlert.delete("/")
def delete(alert_id: int = Query(..., description="ID de la alerta a eliminar"), db: Session = Depends(get_db)):
    """
    Eliminar una alerta
    """
    deleted = delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(404, "Alert not found")
    return {"message": "Alert deleted successfully"}


from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from db.schemas import AlertCreate, AlertResponse
from crud.alerts import (
    create_alert,
    get_alerts,
    get_expiration_alerts,
    get_low_stock_alerts,
    delete_alert
)
from utils.auth import get_current_user_optional
from db.models import User

routerAlert = APIRouter(prefix="/alerts", tags=["Alerts"])


@routerAlert.get("/expiration")
def get_expiration(
    days: int = Query(30, description="Días antes de la fecha de vencimiento"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF21: Generar alertas de productos próximos a vencer
    Retorna lotes que vencen en los próximos 'days' días
    """
    try:
        alerts = get_expiration_alerts(db, days=days)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas de vencimiento: {str(e)}")


@routerAlert.get("/low-stock")
def get_low_stock(
    min_stock: int = Query(10, description="Stock mínimo para considerar bajo stock"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF22: Generar alertas de productos con bajo stock
    Retorna lotes con stock menor o igual a 'min_stock'
    """
    try:
        alerts = get_low_stock_alerts(db, min_stock=min_stock)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas de stock bajo: {str(e)}")


@routerAlert.get("/", response_model=list[AlertResponse])
def list_all(
    alert_type: Optional[str] = Query(None, description="Tipo de alerta: 'expiration' o 'low_stock'"),
    batch_id: Optional[int] = Query(None, description="ID del lote"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Listar todas las alertas con filtros opcionales
    """
    try:
        return get_alerts(db, alert_type=alert_type, batch_id=batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas: {str(e)}")


@routerAlert.post("/", response_model=AlertResponse)
def create(data: AlertCreate, db: Session = Depends(get_db)):
    """
    Crear una alerta manualmente
    """
    try:
        return create_alert(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear alerta: {str(e)}")


@routerAlert.delete("/")
def delete(alert_id: int = Query(..., description="ID de la alerta a eliminar"), db: Session = Depends(get_db)):
    """
    Eliminar una alerta
    """
    deleted = delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(404, "Alert not found")
    return {"message": "Alert deleted successfully"}



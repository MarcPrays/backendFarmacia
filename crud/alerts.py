from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta
from db.models import Alert, MedicineBatch, Product
from db.schemas import AlertCreate


def create_alert(db: Session, data: AlertCreate):
    """Crear una alerta"""
    alert = Alert(
        alert_type=data.alert_type,
        batch_id=data.batch_id,
        message=data.message
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, alert_type: str = None, batch_id: int = None):
    """Obtener alertas con filtros"""
    query = db.query(Alert).options(
        joinedload(Alert.batch).joinedload(MedicineBatch.product)
    )
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if batch_id:
        query = query.filter(Alert.batch_id == batch_id)
    
    return query.order_by(Alert.id.desc()).all()


def get_expiration_alerts(db: Session, days: int = 30):
    """
    RF21: Generar alertas de productos próximos a vencer
    Retorna lotes que vencen en los próximos 'days' días
    """
    today = date.today()
    expiration_date = today + timedelta(days=days)
    
    batches = db.query(MedicineBatch).options(
        joinedload(MedicineBatch.product)
    ).filter(
        MedicineBatch.status == 1,
        MedicineBatch.expiration_date.isnot(None),
        MedicineBatch.expiration_date <= expiration_date,
        MedicineBatch.expiration_date >= today
    ).all()
    
    alerts = []
    for batch in batches:
        if batch.expiration_date:
            days_until_expiration = (batch.expiration_date - today).days
            message = f"El lote del producto '{batch.product.name}' vence en {days_until_expiration} días (Fecha: {batch.expiration_date})"
            
            alerts.append({
                "batch_id": batch.id,
                "product_name": batch.product.name,
                "product_presentation": batch.product.presentation,
                "expiration_date": batch.expiration_date.isoformat() if batch.expiration_date else None,
                "days_until_expiration": days_until_expiration,
                "stock": batch.stock,
                "message": message,
                "alert_type": "expiration"
            })
    
    return alerts


def get_low_stock_alerts(db: Session, min_stock: int = 10):
    """
    RF22: Generar alertas de productos con bajo stock
    Retorna lotes con stock menor o igual a 'min_stock'
    """
    batches = db.query(MedicineBatch).options(
        joinedload(MedicineBatch.product)
    ).filter(
        MedicineBatch.status == 1,
        MedicineBatch.stock <= min_stock,
        MedicineBatch.stock >= 0
    ).all()
    
    alerts = []
    for batch in batches:
        message = f"El lote del producto '{batch.product.name}' tiene stock bajo: {batch.stock} unidades (Mínimo recomendado: {min_stock})"
        
        alerts.append({
            "batch_id": batch.id,
            "product_name": batch.product.name,
            "product_presentation": batch.product.presentation,
            "stock": batch.stock,
            "min_stock": min_stock,
            "message": message,
            "alert_type": "low_stock"
        })
    
    return alerts


def delete_alert(db: Session, alert_id: int):
    """Eliminar una alerta"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return False
    db.delete(alert)
    db.commit()
    return True


from db.models import Alert, MedicineBatch, Product
from db.schemas import AlertCreate


def create_alert(db: Session, data: AlertCreate):
    """Crear una alerta"""
    alert = Alert(
        alert_type=data.alert_type,
        batch_id=data.batch_id,
        message=data.message
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, alert_type: str = None, batch_id: int = None):
    """Obtener alertas con filtros"""
    query = db.query(Alert).options(
        joinedload(Alert.batch).joinedload(MedicineBatch.product)
    )
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if batch_id:
        query = query.filter(Alert.batch_id == batch_id)
    
    return query.order_by(Alert.id.desc()).all()


def get_expiration_alerts(db: Session, days: int = 30):
    """
    RF21: Generar alertas de productos próximos a vencer
    Retorna lotes que vencen en los próximos 'days' días
    """
    today = date.today()
    expiration_date = today + timedelta(days=days)
    
    batches = db.query(MedicineBatch).options(
        joinedload(MedicineBatch.product)
    ).filter(
        MedicineBatch.status == 1,
        MedicineBatch.expiration_date.isnot(None),
        MedicineBatch.expiration_date <= expiration_date,
        MedicineBatch.expiration_date >= today
    ).all()
    
    alerts = []
    for batch in batches:
        if batch.expiration_date:
            days_until_expiration = (batch.expiration_date - today).days
            message = f"El lote del producto '{batch.product.name}' vence en {days_until_expiration} días (Fecha: {batch.expiration_date})"
            
            alerts.append({
                "batch_id": batch.id,
                "product_name": batch.product.name,
                "product_presentation": batch.product.presentation,
                "expiration_date": batch.expiration_date.isoformat() if batch.expiration_date else None,
                "days_until_expiration": days_until_expiration,
                "stock": batch.stock,
                "message": message,
                "alert_type": "expiration"
            })
    
    return alerts


def get_low_stock_alerts(db: Session, min_stock: int = 10):
    """
    RF22: Generar alertas de productos con bajo stock
    Retorna lotes con stock menor o igual a 'min_stock'
    """
    batches = db.query(MedicineBatch).options(
        joinedload(MedicineBatch.product)
    ).filter(
        MedicineBatch.status == 1,
        MedicineBatch.stock <= min_stock,
        MedicineBatch.stock >= 0
    ).all()
    
    alerts = []
    for batch in batches:
        message = f"El lote del producto '{batch.product.name}' tiene stock bajo: {batch.stock} unidades (Mínimo recomendado: {min_stock})"
        
        alerts.append({
            "batch_id": batch.id,
            "product_name": batch.product.name,
            "product_presentation": batch.product.presentation,
            "stock": batch.stock,
            "min_stock": min_stock,
            "message": message,
            "alert_type": "low_stock"
        })
    
    return alerts


def delete_alert(db: Session, alert_id: int):
    """Eliminar una alerta"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return False
    db.delete(alert)
    db.commit()
    return True


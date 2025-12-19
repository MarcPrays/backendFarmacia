"""
Funciones CRUD para el dashboard
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, Any, List
from db.models import Sale, SalesDetail, Product, MedicineBatch, Client, Alert, Purchase


def get_week_sales(db: Session) -> Dict[str, Any]:
    """Obtiene las ventas de la semana actual"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    sales = db.query(Sale).filter(
        func.date(Sale.sale_date) >= start_of_week,
        func.date(Sale.sale_date) <= end_of_week
    ).all()
    
    total = sum(float(sale.total) for sale in sales)
    count = len(sales)
    
    return {
        "total": total,
        "count": count,
        "start_date": start_of_week.isoformat(),
        "end_date": end_of_week.isoformat()
    }


def get_active_clients_count(db: Session) -> int:
    """Obtiene el número de clientes activos"""
    return db.query(Client).filter(Client.status == 1).count()


def get_products_in_stock_count(db: Session) -> int:
    """Obtiene el número de productos en stock"""
    return db.query(Product).filter(Product.status == 1).count()


def get_low_stock_count(db: Session) -> int:
    """Obtiene el número de productos con stock bajo"""
    # El modelo Alert no tiene status, solo filtramos por tipo
    return db.query(Alert).filter(
        Alert.alert_type == "stock_bajo"
    ).count()


def get_recent_sales(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Obtiene las ventas recientes"""
    from sqlalchemy.orm import joinedload
    sales = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product)
    ).order_by(Sale.sale_date.desc()).limit(limit).all()
    
    result = []
    for sale in sales:
        client_name = f"{sale.client.first_name} {sale.client.last_name}".strip() if sale.client else "N/A"
        
        # Obtener el primer producto de la venta
        first_detail = sale.details[0] if sale.details else None
        product_name = "N/A"
        product_presentation = ""
        
        if first_detail and first_detail.batch and first_detail.batch.product:
            product_name = first_detail.batch.product.name
            product_presentation = first_detail.batch.product.presentation or ""
        
        sale_date = sale.sale_date if sale.sale_date else datetime.now()
        time_str = sale_date.strftime("%H:%M")
        
        result.append({
            "id": sale.id,
            "client_name": client_name,
            "product_name": product_name,
            "product_presentation": product_presentation,
            "total": float(sale.total),
            "sale_date": sale_date.isoformat(),
            "time": time_str
        })
    
    return result


def get_popular_products(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Obtiene los productos más vendidos"""
    products = db.query(
        Product.id,
        Product.name,
        Product.presentation,
        func.sum(SalesDetail.quantity).label('total_quantity')
    ).join(
        MedicineBatch, Product.id == MedicineBatch.product_id
    ).join(
        SalesDetail, MedicineBatch.id == SalesDetail.batch_id
    ).group_by(
        Product.id, Product.name, Product.presentation
    ).order_by(
        func.sum(SalesDetail.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "presentation": p.presentation or "",
            "total_quantity": int(p.total_quantity) if p.total_quantity else 0
        }
        for p in products
    ]


def get_financial_summary(db: Session) -> Dict[str, Any]:
    """Obtiene el resumen financiero"""
    # Total de ingresos (ventas)
    total_income = db.query(func.sum(Sale.total)).scalar() or 0.0
    
    # Total de gastos (compras)
    total_expenses = db.query(func.sum(Purchase.total)).scalar() or 0.0
    
    net_result = float(total_income) - float(total_expenses)
    
    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_result": net_result
    }


def get_last_7_days_sales(db: Session) -> List[Dict[str, Any]]:
    """Obtiene las ventas de los últimos 7 días"""
    today = datetime.now().date()
    start_date = today - timedelta(days=6)
    
    sales = db.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total).label('total'),
        func.count(Sale.id).label('count')
    ).filter(
        func.date(Sale.sale_date) >= start_date,
        func.date(Sale.sale_date) <= today
    ).group_by(
        func.date(Sale.sale_date)
    ).all()
    
    # Crear un diccionario con todas las fechas
    result = {}
    for i in range(7):
        date = start_date + timedelta(days=i)
        result[date] = {
            "date": date.isoformat(),
            "day_name": date.strftime("%a"),
            "day_number": date.day,
            "total": 0.0,
            "count": 0
        }
    
    # Llenar con datos reales
    for sale in sales:
        date = sale.date
        if date in result:
            result[date]["total"] = float(sale.total) if sale.total else 0.0
            result[date]["count"] = int(sale.count) if sale.count else 0
    
    return list(result.values())


def get_income_by_product_top(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Obtiene los productos con mayor ingreso"""
    products = db.query(
        Product.id.label('product_id'),
        Product.name.label('product_name'),
        func.sum(SalesDetail.subtotal).label('total_revenue')
    ).join(
        MedicineBatch, Product.id == MedicineBatch.product_id
    ).join(
        SalesDetail, MedicineBatch.id == SalesDetail.batch_id
    ).group_by(
        Product.id, Product.name
    ).order_by(
        func.sum(SalesDetail.subtotal).desc()
    ).limit(limit).all()
    
    return [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "total_revenue": float(p.total_revenue) if p.total_revenue else 0.0
        }
        for p in products
    ]


def get_order_status_distribution(db: Session) -> Dict[str, Any]:
    """Obtiene la distribución de métodos de pago"""
    from db.models import Sale
    
    results = db.query(
        Sale.payment_method,
        func.count(Sale.id).label('count'),
        func.sum(Sale.total).label('total')
    ).group_by(
        Sale.payment_method
    ).all()
    
    total_count = sum(r.count for r in results)
    total_amount = sum(float(r.total) if r.total else 0.0 for r in results)
    
    distribution = [
        {
            "status": r.payment_method or "N/A",
            "count": int(r.count),
            "total": float(r.total) if r.total else 0.0,
            "percentage": (float(r.count) / total_count * 100) if total_count > 0 else 0.0
        }
        for r in results
    ]
    
    return {
        "total": total_count,
        "distribution": distribution
    }


def get_all_dashboard_data(db: Session) -> Dict[str, Any]:
    """Obtiene todos los datos del dashboard en una sola llamada"""
    return {
        "week_sales": get_week_sales(db),
        "active_clients": get_active_clients_count(db),
        "products_in_stock": get_products_in_stock_count(db),
        "low_stock_count": get_low_stock_count(db),
        "recent_sales": get_recent_sales(db),
        "popular_products": get_popular_products(db),
        "financial_summary": get_financial_summary(db),
        "last_7_days_sales": get_last_7_days_sales(db),
        "income_by_product_top": get_income_by_product_top(db),
        "order_status_distribution": get_order_status_distribution(db),
        "current_date": datetime.now().date().isoformat()
    }


from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from datetime import datetime
from decimal import Decimal
from db.models import Sale, SalesDetail, Product, MedicineBatch


def get_sales_report(db: Session, start_date: datetime = None, end_date: datetime = None):
    """
    RF23: Reporte de ventas por fechas
    Retorna resumen de ventas en el rango de fechas especificado
    """
    query = db.query(Sale).options(
        joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Sale.client),
        joinedload(Sale.user)
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    sales = query.order_by(Sale.sale_date.desc()).all()
    
    # Calcular estadísticas
    total_sales = len(sales)
    total_amount = sum(float(sale.total) for sale in sales)
    total_items = sum(len(sale.details) for sale in sales)
    
    # Agrupar por método de pago
    payment_methods = {}
    for sale in sales:
        method = sale.payment_method
        if method not in payment_methods:
            payment_methods[method] = {"count": 0, "total": Decimal('0.00')}
        payment_methods[method]["count"] += 1
        payment_methods[method]["total"] += sale.total
    
    # Agrupar por día
    daily_sales = {}
    for sale in sales:
        date_key = sale.sale_date.date().isoformat() if sale.sale_date else None
        if date_key:
            if date_key not in daily_sales:
                daily_sales[date_key] = {"count": 0, "total": Decimal('0.00')}
            daily_sales[date_key]["count"] += 1
            daily_sales[date_key]["total"] += sale.total
    
    return {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "total_sales": total_sales,
        "total_amount": float(total_amount),
        "total_items": total_items,
        "average_sale": float(total_amount / total_sales) if total_sales > 0 else 0,
        "payment_methods": {k: {"count": v["count"], "total": float(v["total"])} for k, v in payment_methods.items()},
        "daily_sales": {k: {"count": v["count"], "total": float(v["total"])} for k, v in daily_sales.items()},
        "sales": [
            {
                "id": sale.id,
                "date": sale.sale_date.isoformat() if sale.sale_date else None,
                "client_name": f"{sale.client.first_name} {sale.client.last_name}" if sale.client else None,
                "user_name": f"{sale.user.first_name} {sale.user.last_name}" if sale.user else None,
                "payment_method": sale.payment_method,
                "total": float(sale.total),
                "items_count": len(sale.details)
            }
            for sale in sales
        ]
    }


def get_top_products_report(db: Session, start_date: datetime = None, end_date: datetime = None, limit: int = 10):
    """
    RF24: Reporte de productos más vendidos
    Retorna los productos más vendidos en el rango de fechas especificado
    """
    query = db.query(
        Product.id,
        Product.name,
        Product.presentation,
        Product.concentration,
        func.sum(SalesDetail.quantity).label('total_quantity'),
        func.sum(SalesDetail.subtotal).label('total_revenue'),
        func.count(SalesDetail.id).label('sales_count')
    ).join(
        MedicineBatch, Product.id == MedicineBatch.product_id
    ).join(
        SalesDetail, MedicineBatch.id == SalesDetail.batch_id
    ).join(
        Sale, SalesDetail.sale_id == Sale.id
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    query = query.filter(
        Product.status == 1,
        Sale.id.isnot(None)
    ).group_by(
        Product.id,
        Product.name,
        Product.presentation,
        Product.concentration
    ).order_by(
        desc('total_quantity')
    ).limit(limit)
    
    results = query.all()
    
    products = []
    for result in results:
        products.append({
            "product_id": result.id,
            "product_name": result.name,
            "presentation": result.presentation,
            "concentration": result.concentration,
            "total_quantity_sold": int(result.total_quantity),
            "total_revenue": float(result.total_revenue),
            "sales_count": int(result.sales_count),
            "average_per_sale": float(result.total_revenue / result.sales_count) if result.sales_count > 0 else 0
        })
    
    return {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "limit": limit,
        "total_products": len(products),
        "products": products
    }


from sqlalchemy import func, desc
from datetime import datetime
from decimal import Decimal
from db.models import Sale, SalesDetail, Product, MedicineBatch


def get_sales_report(db: Session, start_date: datetime = None, end_date: datetime = None):
    """
    RF23: Reporte de ventas por fechas
    Retorna resumen de ventas en el rango de fechas especificado
    """
    query = db.query(Sale).options(
        joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Sale.client),
        joinedload(Sale.user)
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    sales = query.order_by(Sale.sale_date.desc()).all()
    
    # Calcular estadísticas
    total_sales = len(sales)
    total_amount = sum(float(sale.total) for sale in sales)
    total_items = sum(len(sale.details) for sale in sales)
    
    # Agrupar por método de pago
    payment_methods = {}
    for sale in sales:
        method = sale.payment_method
        if method not in payment_methods:
            payment_methods[method] = {"count": 0, "total": Decimal('0.00')}
        payment_methods[method]["count"] += 1
        payment_methods[method]["total"] += sale.total
    
    # Agrupar por día
    daily_sales = {}
    for sale in sales:
        date_key = sale.sale_date.date().isoformat() if sale.sale_date else None
        if date_key:
            if date_key not in daily_sales:
                daily_sales[date_key] = {"count": 0, "total": Decimal('0.00')}
            daily_sales[date_key]["count"] += 1
            daily_sales[date_key]["total"] += sale.total
    
    return {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "total_sales": total_sales,
        "total_amount": float(total_amount),
        "total_items": total_items,
        "average_sale": float(total_amount / total_sales) if total_sales > 0 else 0,
        "payment_methods": {k: {"count": v["count"], "total": float(v["total"])} for k, v in payment_methods.items()},
        "daily_sales": {k: {"count": v["count"], "total": float(v["total"])} for k, v in daily_sales.items()},
        "sales": [
            {
                "id": sale.id,
                "date": sale.sale_date.isoformat() if sale.sale_date else None,
                "client_name": f"{sale.client.first_name} {sale.client.last_name}" if sale.client else None,
                "user_name": f"{sale.user.first_name} {sale.user.last_name}" if sale.user else None,
                "payment_method": sale.payment_method,
                "total": float(sale.total),
                "items_count": len(sale.details)
            }
            for sale in sales
        ]
    }


def get_top_products_report(db: Session, start_date: datetime = None, end_date: datetime = None, limit: int = 10):
    """
    RF24: Reporte de productos más vendidos
    Retorna los productos más vendidos en el rango de fechas especificado
    """
    query = db.query(
        Product.id,
        Product.name,
        Product.presentation,
        Product.concentration,
        func.sum(SalesDetail.quantity).label('total_quantity'),
        func.sum(SalesDetail.subtotal).label('total_revenue'),
        func.count(SalesDetail.id).label('sales_count')
    ).join(
        MedicineBatch, Product.id == MedicineBatch.product_id
    ).join(
        SalesDetail, MedicineBatch.id == SalesDetail.batch_id
    ).join(
        Sale, SalesDetail.sale_id == Sale.id
    )
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    query = query.filter(
        Product.status == 1,
        Sale.id.isnot(None)
    ).group_by(
        Product.id,
        Product.name,
        Product.presentation,
        Product.concentration
    ).order_by(
        desc('total_quantity')
    ).limit(limit)
    
    results = query.all()
    
    products = []
    for result in results:
        products.append({
            "product_id": result.id,
            "product_name": result.name,
            "presentation": result.presentation,
            "concentration": result.concentration,
            "total_quantity_sold": int(result.total_quantity),
            "total_revenue": float(result.total_revenue),
            "sales_count": int(result.sales_count),
            "average_per_sale": float(result.total_revenue / result.sales_count) if result.sales_count > 0 else 0
        })
    
    return {
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "limit": limit,
        "total_products": len(products),
        "products": products
    }



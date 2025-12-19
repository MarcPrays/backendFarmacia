from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal
from db.models import Sale, SalesDetail, MedicineBatch, Client, User, Product
from db.schemas import SaleCreate, SaleResponse


def create_sale(db: Session, data: SaleCreate, user_id: int):
    """
    Crear una venta con sus detalles
    RF14: Registrar una venta
    RF15: Calcular automáticamente subtotales
    RF16: Controlar el stock después de cada venta
    """
    # Verificar que el cliente existe
    client = db.query(Client).filter(Client.id == data.client_id).first()
    if not client:
        raise ValueError(f"El cliente con ID {data.client_id} no existe")
    
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"El usuario con ID {user_id} no existe")
    
    # Validar stock y calcular totales
    total = Decimal('0.00')
    sale_details = []
    
    for detail in data.details:
        # Verificar que el batch existe y tiene stock suficiente
        batch = db.query(MedicineBatch).filter(
            MedicineBatch.id == detail.batch_id,
            MedicineBatch.status == 1
        ).first()
        
        if not batch:
            raise ValueError(f"El lote con ID {detail.batch_id} no existe o está inactivo")
        
        if batch.stock < detail.quantity:
            raise ValueError(
                f"Stock insuficiente para el lote {detail.batch_id}. "
                f"Stock disponible: {batch.stock}, solicitado: {detail.quantity}"
            )
        
        # RF15: Calcular subtotal automáticamente (ignorar el valor enviado por el frontend)
        # El subtotal se calcula siempre como: unit_price * quantity
        calculated_subtotal = Decimal(str(detail.unit_price)) * detail.quantity
        total += calculated_subtotal
        
        # Validar que el subtotal enviado coincida con el calculado (opcional, para debugging)
        if abs(Decimal(str(detail.subtotal)) - calculated_subtotal) > Decimal('0.01'):
            # Si hay diferencia significativa, usar el calculado
            print(f"Advertencia: Subtotal enviado ({detail.subtotal}) no coincide con el calculado ({calculated_subtotal}). Usando el calculado.")
        
        sale_details.append({
            'batch_id': detail.batch_id,
            'quantity': detail.quantity,
            'unit_price': detail.unit_price,
            'subtotal': calculated_subtotal  # Usar el subtotal calculado automáticamente
        })
    
    # Crear la venta
    sale = Sale(
        client_id=data.client_id,
        user_id=user_id,
        sale_date=data.sale_date or datetime.now(),
        payment_method=data.payment_method,
        total=total
    )
    db.add(sale)
    db.flush()  # Para obtener el ID de la venta
    
    # Crear los detalles y actualizar stock (RF16)
    for detail_data in sale_details:
        sale_detail = SalesDetail(
            sale_id=sale.id,
            batch_id=detail_data['batch_id'],
            quantity=detail_data['quantity'],
            unit_price=detail_data['unit_price'],
            subtotal=detail_data['subtotal']
        )
        db.add(sale_detail)
        
        # Reducir stock del batch
        batch = db.query(MedicineBatch).filter(MedicineBatch.id == detail_data['batch_id']).first()
        batch.stock -= detail_data['quantity']
    
    try:
        db.commit()
        # Recargar la venta con todas las relaciones
        db.refresh(sale)
        # Cargar relaciones para la respuesta
        sale = db.query(Sale).options(
            joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product),
            joinedload(Sale.client),
            joinedload(Sale.user)
        ).filter(Sale.id == sale.id).first()
        return sale
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        raise ValueError(f"Error al crear la venta: {error_msg}")


def get_sales(db: Session, client_id: int = None, user_id: int = None, start_date: datetime = None, end_date: datetime = None):
    """
    RF17: Mostrar historial de ventas con filtros
    Incluye información relacionada: cliente, usuario, detalles, lotes y productos
    """
    query = db.query(Sale).options(
        joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Sale.client),
        joinedload(Sale.user)
    )
    
    if client_id:
        query = query.filter(Sale.client_id == client_id)
    
    if user_id:
        query = query.filter(Sale.user_id == user_id)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    return query.order_by(Sale.sale_date.desc()).all()


def get_sale(db: Session, sale_id: int):
    """
    Obtener una venta por ID con toda la información relacionada
    Incluye: cliente, usuario, detalles, lotes y productos
    """
    return db.query(Sale).options(
        joinedload(Sale.details).joinedload(SalesDetail.batch).joinedload(MedicineBatch.product),
        joinedload(Sale.client),
        joinedload(Sale.user)
    ).filter(Sale.id == sale_id).first()


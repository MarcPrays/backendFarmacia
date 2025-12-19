from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from db.database import get_db
from crud.reports import get_sales_report, get_top_products_report
from utils.auth import get_current_user_optional
from utils.pdf_generator import generate_sales_report_pdf, generate_top_products_report_pdf
from db.models import User

routerReport = APIRouter(prefix="/reports", tags=["Reports"])


@routerReport.get("/sales")
def sales_report(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF23: Reporte de ventas por fechas
    Retorna un resumen completo de ventas en el rango de fechas especificado
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver reportes"
        )
    
    try:
        report = get_sales_report(db, start_date=start_date, end_date=end_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte de ventas: {str(e)}")


@routerReport.get("/top-products")
def top_products_report(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(10, description="Número de productos a retornar"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF24: Reporte de productos más vendidos
    Retorna los productos más vendidos en el rango de fechas especificado
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver reportes"
        )
    
    try:
        report = get_top_products_report(db, start_date=start_date, end_date=end_date, limit=limit)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte de productos más vendidos: {str(e)}")


@routerReport.get("/sales/export")
def export_sales_report_pdf(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    format: str = Query("pdf", description="Formato de exportación: 'pdf'"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF25: Exportación de reporte de ventas a PDF
    Exporta el reporte de ventas en formato PDF
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para exportar reportes"
        )
    
    try:
        report = get_sales_report(db, start_date=start_date, end_date=end_date)
        
        if format.lower() == "pdf":
            # Generar PDF real usando reportlab
            pdf_bytes = generate_sales_report_pdf(report)
            
            # Verificar que el PDF sea válido
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise HTTPException(status_code=500, detail="Error al generar PDF: archivo vacío")
            
            if not pdf_bytes.startswith(b'%PDF'):
                raise HTTPException(status_code=500, detail="Error al generar PDF: formato inválido")
            
            filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf'")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar reporte: {str(e)}")


@routerReport.get("/top-products/export")
def export_top_products_report_pdf(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(10, description="Número de productos a retornar"),
    format: str = Query("pdf", description="Formato de exportación: 'pdf'"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF25: Exportación de reporte de productos más vendidos a PDF
    Exporta el reporte de productos más vendidos en formato PDF
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para exportar reportes"
        )
    
    try:
        report = get_top_products_report(db, start_date=start_date, end_date=end_date, limit=limit)
        
        if format.lower() == "pdf":
            # Generar PDF real usando reportlab
            pdf_bytes = generate_top_products_report_pdf(report)
            
            # Verificar que el PDF sea válido
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise HTTPException(status_code=500, detail="Error al generar PDF: archivo vacío")
            
            if not pdf_bytes.startswith(b'%PDF'):
                raise HTTPException(status_code=500, detail="Error al generar PDF: formato inválido")
            
            filename = f"reporte_productos_mas_vendidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf'")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar reporte: {str(e)}")


from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from db.database import get_db
from crud.reports import get_sales_report, get_top_products_report
from utils.auth import get_current_user_optional
from utils.pdf_generator import generate_sales_report_pdf, generate_top_products_report_pdf
from db.models import User

routerReport = APIRouter(prefix="/reports", tags=["Reports"])


@routerReport.get("/sales")
def sales_report(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF23: Reporte de ventas por fechas
    Retorna un resumen completo de ventas en el rango de fechas especificado
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver reportes"
        )
    
    try:
        report = get_sales_report(db, start_date=start_date, end_date=end_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte de ventas: {str(e)}")


@routerReport.get("/top-products")
def top_products_report(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(10, description="Número de productos a retornar"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF24: Reporte de productos más vendidos
    Retorna los productos más vendidos en el rango de fechas especificado
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para ver reportes"
        )
    
    try:
        report = get_top_products_report(db, start_date=start_date, end_date=end_date, limit=limit)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte de productos más vendidos: {str(e)}")


@routerReport.get("/sales/export")
def export_sales_report_pdf(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    format: str = Query("pdf", description="Formato de exportación: 'pdf'"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF25: Exportación de reporte de ventas a PDF
    Exporta el reporte de ventas en formato PDF
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para exportar reportes"
        )
    
    try:
        report = get_sales_report(db, start_date=start_date, end_date=end_date)
        
        if format.lower() == "pdf":
            # Generar PDF real usando reportlab
            pdf_bytes = generate_sales_report_pdf(report)
            
            # Verificar que el PDF sea válido
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise HTTPException(status_code=500, detail="Error al generar PDF: archivo vacío")
            
            if not pdf_bytes.startswith(b'%PDF'):
                raise HTTPException(status_code=500, detail="Error al generar PDF: formato inválido")
            
            filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf'")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar reporte: {str(e)}")


@routerReport.get("/top-products/export")
def export_top_products_report_pdf(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(10, description="Número de productos a retornar"),
    format: str = Query("pdf", description="Formato de exportación: 'pdf'"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    RF25: Exportación de reporte de productos más vendidos a PDF
    Exporta el reporte de productos más vendidos en formato PDF
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para exportar reportes"
        )
    
    try:
        report = get_top_products_report(db, start_date=start_date, end_date=end_date, limit=limit)
        
        if format.lower() == "pdf":
            # Generar PDF real usando reportlab
            pdf_bytes = generate_top_products_report_pdf(report)
            
            # Verificar que el PDF sea válido
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise HTTPException(status_code=500, detail="Error al generar PDF: archivo vacío")
            
            if not pdf_bytes.startswith(b'%PDF'):
                raise HTTPException(status_code=500, detail="Error al generar PDF: formato inválido")
            
            filename = f"reporte_productos_mas_vendidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Type": "application/pdf",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'pdf'")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar reporte: {str(e)}")


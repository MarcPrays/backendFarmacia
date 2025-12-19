from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from utils.auth import get_current_user, oauth2_scheme, SECRET_KEY, ALGORITHM
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, IntegrityError
from datetime import datetime, timedelta
from jose import JWTError, jwt
from utils.security import verify_password, get_password_hash
import pymysql

import os

from db.database import Base, engine, get_db
from routers.users import routerUser
from routers.categories import routerCategory
from routers.clients import routerClient
from routers.suppliers import routerSupplier
from routers.products import routerProduct
from routers.batches import routerBatch
from routers.sales import routerSale
from routers.purchases import routerPurchase
from routers.alerts import routerAlert
from routers.reports import routerReport
from routers.dashboard import routerDashboard
from routers.invoices import routerInvoice



# ========================
# CONFIG
# ========================
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ========================
# INIT APP
# ========================
app = FastAPI(title="Farmacia API")

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas (con manejo de errores)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Advertencia: No se pudieron crear las tablas automáticamente: {e}")
    print("Asegúrate de que MySQL esté corriendo y que la base de datos exista.")

# Servir archivos estáticos (imágenes)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ========================
# EXCEPTION HANDLERS
# ========================
@app.exception_handler(OperationalError)
async def database_exception_handler(request: Request, exc: OperationalError):
    """Maneja errores de conexión a la base de datos"""
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    error_code = None
    
    # Extraer código de error si está disponible
    if hasattr(exc, 'orig') and hasattr(exc.orig, 'args') and len(exc.orig.args) > 0:
        error_code = exc.orig.args[0] if isinstance(exc.orig.args[0], int) else None
    
    # Error de conexión (MySQL no está corriendo)
    if "Can't connect" in error_message or "Lost connection" in error_message or error_code == 2003:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Servicio de base de datos no disponible",
                "message": "No se puede conectar al servidor MySQL. Verifica que MySQL esté corriendo.",
                "error": error_message
            }
        )
    
    # Error de autenticación (credenciales incorrectas)
    if "Access denied" in error_message or error_code == 1045:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Error de autenticación con la base de datos",
                "message": "Las credenciales de MySQL son incorrectas. Verifica el usuario y contraseña en el archivo .env",
                "error": error_message
            }
    )
    
    # Error de base de datos no existe
    if "Unknown database" in error_message or error_code == 1049:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Base de datos no encontrada",
                "message": f"La base de datos especificada no existe. Verifica la configuración en el archivo .env",
                "error": error_message
            }
        )
    
    # Otros errores de base de datos
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error de base de datos",
            "message": "Ocurrió un error al acceder a la base de datos.",
            "error": error_message
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Maneja errores de integridad referencial"""
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    error_code = None
    
    # Extraer código de error si está disponible
    if hasattr(exc, 'orig') and hasattr(exc.orig, 'args') and len(exc.orig.args) > 0:
        error_code = exc.orig.args[0] if isinstance(exc.orig.args[0], int) else None
    
    # Error de foreign key constraint (1452)
    if "foreign key constraint" in error_message.lower() or error_code == 1452:
        # Intentar extraer información del error
        if "category_id" in error_message.lower():
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Error de validación",
                    "message": "La categoría especificada no existe. Por favor, selecciona una categoría válida.",
                    "error": error_message
                }
            )
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Error de validación",
                "message": "La referencia especificada no existe. Verifica que todos los datos relacionados sean válidos.",
                "error": error_message
            }
        )
    
    # Otros errores de integridad
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Error de integridad de datos",
            "message": "Los datos proporcionados violan las restricciones de la base de datos.",
            "error": error_message
        }
    )

# ========================
# ROOT ROUTE
# ========================
@app.get("/")
def root():
    return {
        "message": "Bienvenido a la API de Farmacia",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "status": "running"
    }

# ========================
# AUTH
# ========================

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ========================
# LOGIN ROUTE
# ========================
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from crud import users
    from db.models import User
    from sqlalchemy.orm import joinedload

    user = db.query(User).options(joinedload(User.role)).filter(
        User.username == form_data.username
    ).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Obtener nombre del rol
    role_name = user.role.name if user.role else None
    
    # Convertir user.id a string porque JWT requiere que 'sub' sea string
    # Incluir rol en el token para verificación rápida
    access_token = create_access_token(data={
        "sub": str(user.id),
        "role": role_name,
        "role_id": user.role_id
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": role_name,
            "role_id": user.role_id
        }
    }

# ========================
# INCLUDE ROUTERS
# ========================
app.include_router(routerUser)
app.include_router(routerCategory)
app.include_router(routerClient)
app.include_router(routerSupplier)
app.include_router(routerProduct)
app.include_router(routerBatch)
app.include_router(routerSale)
app.include_router(routerPurchase)
app.include_router(routerAlert)
app.include_router(routerReport)
app.include_router(routerDashboard)
app.include_router(routerInvoice)

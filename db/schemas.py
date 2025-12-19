from decimal import Decimal
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, validator


# ========================
# USERS
# ========================
class UserCreate(BaseModel):
    role_id: int
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)

    username: str = Field(..., min_length=4, max_length=100)  # NUEVO

    email: str = Field(..., max_length=150)
    password: str = Field(..., min_length=6, max_length=255)


class UserUpdate(BaseModel):
    role_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None
    
    @validator('first_name')
    def validate_first_name(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 100):
            raise ValueError('El nombre debe tener entre 2 y 100 caracteres')
        return v
    
    @validator('last_name')
    def validate_last_name(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 100):
            raise ValueError('El apellido debe tener entre 2 y 100 caracteres')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None and (len(v) < 4 or len(v) > 100):
            raise ValueError('El usuario debe tener entre 4 y 100 caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and len(v) > 150:
            raise ValueError('El email no puede tener más de 150 caracteres')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and v != '' and (len(v) < 6 or len(v) > 255):
            raise ValueError('La contraseña debe tener entre 6 y 255 caracteres')
        return v


class UserResponse(BaseModel):
    id: int
    role_id: int
    first_name: str
    last_name: str

    username: str      # NUEVO

    email: str
    status: int
    role_name: Optional[str] = None  # Nombre del rol

    class Config:
        from_attributes = True


# ========================
# CLIENTS
# ========================
class ClientCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None


class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[int]


class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: Optional[str]
    email: Optional[str]
    status: int

    class Config:
        from_attributes = True


# ========================
# CATEGORIES
# ========================
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


# ========================
# PRODUCTS
# ========================
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    category_id: int
    presentation: str
    concentration: str
    image: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    category_id: Optional[int]
    presentation: Optional[str] = None
    concentration: Optional[str] = None
    image: Optional[str] = None
    status: Optional[int]


class ProductStockUpdate(BaseModel):
    stock: int = Field(..., gt=0, description="Nuevo stock del producto (debe ser mayor a 0)")


class ProductPriceUpdate(BaseModel):
    price: float = Field(..., gt=0, description="Nuevo precio de venta del producto (debe ser mayor a 0)")


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    presentation: Optional[str]
    concentration: Optional[str]
    image: Optional[str]  # Ruta relativa: "uploads/products/uuid.jpg"
    image_url: Optional[str] = None  # URL completa: "http://127.0.0.1:8000/uploads/products/uuid.jpg"
    status: int
    total_stock: Optional[int] = None  # Stock total de todos los lotes
    sale_price: Optional[float] = None  # Precio de venta del lote más reciente

    class Config:
        from_attributes = True


# ========================
# MEDICINE BATCHES
# ========================
class MedicineBatchCreate(BaseModel):
    product_id: int
    expiration_date: Optional[date] = None
    stock: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None


class MedicineBatchUpdate(BaseModel):
    product_id: Optional[int]
    expiration_date: Optional[date] = None
    stock: Optional[int] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    status: Optional[int]


class MedicineBatchResponse(BaseModel):
    id: int
    product_id: int
    expiration_date: Optional[date]
    stock: Optional[int]
    purchase_price: Optional[float]
    sale_price: Optional[float]
    status: int
    # Información básica del producto (se carga con joinedload)
    product_name: Optional[str] = None
    product_presentation: Optional[str] = None

    class Config:
        from_attributes = True


# ========================
# SUPPLIERS
# ========================
class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: Optional[int]


class SupplierResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    address: str
    city: str
    status: int

    class Config:
        from_attributes = True


# ========================
# SALES DETAIL SCHEMAS
# ========================
class SalesDetailBase(BaseModel):
    batch_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SalesDetailCreate(SalesDetailBase):
    pass


class SalesDetailResponse(SalesDetailBase):
    id: int
    # Información relacionada del lote y producto
    batch_expiration_date: Optional[date] = None
    batch_stock: Optional[int] = None
    product_name: Optional[str] = None
    product_presentation: Optional[str] = None
    product_concentration: Optional[str] = None

    class Config:
        from_attributes = True


# ========================
# SALES SCHEMAS
# ========================
class SaleBase(BaseModel):
    client_id: int
    payment_method: str


class SaleCreate(SaleBase):
    sale_date: Optional[datetime] = None  # Opcional, se usa datetime.now() si no se proporciona
    details: List[SalesDetailCreate]  # detalles incluidos en la creación


class SaleResponse(BaseModel):
    id: int
    client_id: int
    user_id: int
    sale_date: datetime
    payment_method: str
    total: Decimal
    details: List[SalesDetailResponse]
    # Información relacionada del cliente y usuario
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


# ========================
# PURCHASE DETAIL SCHEMAS
# ========================
class PurchaseDetailBase(BaseModel):
    batch_id: Optional[int] = None  # Opcional: si se proporciona, usa el lote existente
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class PurchaseDetailCreate(PurchaseDetailBase):
    # Información del producto (para crear nuevo producto si no existe)
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    category_id: Optional[int] = None
    presentation: Optional[str] = None
    concentration: Optional[str] = None
    product_image: Optional[str] = None  # Base64 o URL de la imagen
    # Información del lote (para crear nuevo lote)
    expiration_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None


class PurchaseDetailResponse(PurchaseDetailBase):
    id: int

    class Config:
        from_attributes = True


# ========================
# PURCHASE SCHEMAS
# ========================
class PurchaseBase(BaseModel):
    supplier_id: int
    payment_method: str


class PurchaseCreate(PurchaseBase):
    purchase_date: Optional[datetime] = None  # Opcional, se usa datetime.now() si no se proporciona
    details: List[PurchaseDetailCreate]  # detalles incluidos en la creación


class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    supplier_id: int
    purchase_date: datetime
    payment_method: str
    total: Decimal
    details: List[PurchaseDetailResponse]

    class Config:
        from_attributes = True


# ========================
# ALERTS SCHEMAS
# ========================
class AlertCreate(BaseModel):
    alert_type: str
    batch_id: int
    message: str


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    batch_id: int
    message: str

    class Config:
        from_attributes = True


# ========================
# ROLES
# ========================
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[int]


class RoleResponse(BaseModel):
    id: int
    name: str
    status: int

    class Config:
        from_attributes = True


# ========================
# PERMISSIONS
# ========================
class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    status: Optional[int]


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: int

    class Config:
        from_attributes = True



class PurchaseCreate(PurchaseBase):
    purchase_date: Optional[datetime] = None  # Opcional, se usa datetime.now() si no se proporciona
    details: List[PurchaseDetailCreate]  # detalles incluidos en la creación


class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    supplier_id: int
    purchase_date: datetime
    payment_method: str
    total: Decimal
    details: List[PurchaseDetailResponse]

    class Config:
        from_attributes = True


# ========================
# ALERTS SCHEMAS
# ========================
class AlertCreate(BaseModel):
    alert_type: str
    batch_id: int
    message: str


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    batch_id: int
    message: str

    class Config:
        from_attributes = True


# ========================
# ROLES
# ========================
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[int]


class RoleResponse(BaseModel):
    id: int
    name: str
    status: int

    class Config:
        from_attributes = True


# ========================
# PERMISSIONS
# ========================
class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    status: Optional[int]


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: int

    class Config:
        from_attributes = True



from decimal import Decimal
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


# ========================
# USERS
# ========================
class UserCreate(BaseModel):
    role_id: int
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., max_length=150)
    password: str = Field(..., min_length=6, max_length=255)


class UserUpdate(BaseModel):
    role_id: Optional[int]
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    status: Optional[int]


class UserResponse(BaseModel):
    id: int
    role_id: int
    first_name: str
    last_name: str
    email: str
    status: int

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


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    presentation: Optional[str]
    concentration: Optional[str]
    image: Optional[str]
    status: int

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

    class Config:
        from_attributes = True


# ========================
# SALES SCHEMAS
# ========================
class SaleBase(BaseModel):
    client_id: int
    user_id: int
    payment_method: str
    total: Decimal


class SaleCreate(SaleBase):
    sale_date: datetime
    details: List[SalesDetailCreate]  # detalles incluidos en la creación


class SaleResponse(SaleBase):
    id: int
    sale_date: datetime
    details: List[SalesDetailResponse]

    class Config:
        from_attributes = True


# ========================
# PURCHASE DETAIL SCHEMAS
# ========================
class PurchaseDetailBase(BaseModel):
    batch_id: int
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class PurchaseDetailCreate(PurchaseDetailBase):
    pass


class PurchaseDetailResponse(PurchaseDetailBase):
    id: int

    class Config:
        from_attributes = True


# ========================
# PURCHASE SCHEMAS
# ========================
class PurchaseBase(BaseModel):
    user_id: int
    supplier_id: int
    payment_method: str
    total: Decimal


class PurchaseCreate(PurchaseBase):
    purchase_date: datetime
    details: List[PurchaseDetailCreate]  # detalles incluidos en la creación


class PurchaseResponse(PurchaseBase):
    id: int
    purchase_date: datetime
    details: List[PurchaseDetailResponse]

    class Config:
        from_attributes = True



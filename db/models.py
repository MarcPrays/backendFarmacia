from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from db.database import Base


# ========================
# ROLES
# ========================
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(Integer, default=1)

    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")
    users = relationship("User", back_populates="role")


# ========================
# PERMISSIONS
# ========================
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    status = Column(Integer, default=1)

    roles = relationship("Role", secondary="role_permission", back_populates="permissions")


# ========================
# PIVOT ROLE_PERMISSION
# ========================
class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"))


# ========================
# USERS
# ========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150))
    password = Column(String(255))
    status = Column(Integer, default=1)

    role = relationship("Role", back_populates="users")
    sales = relationship("Sale", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")


# ========================
# CLIENTS
# ========================
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(150))
    status = Column(Integer, default=1)

    sales = relationship("Sale", back_populates="client")


# ========================
# CATEGORIES
# ========================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text)

    products = relationship("Product", back_populates="category")


# ========================
# PRODUCTS
# ========================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    presentation = Column(String(100))
    concentration = Column(String(100))
    image = Column(String(255))  # añadido
    status = Column(Integer, default=1)

    category = relationship("Category", back_populates="products")
    batches = relationship("MedicineBatch", back_populates="product")


# ========================
# MEDICINE BATCHES
# ========================
class MedicineBatch(Base):
    __tablename__ = "medicine_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    expiration_date = Column(Date)
    stock = Column(Integer)
    purchase_price = Column(DECIMAL(10, 2))
    sale_price = Column(DECIMAL(10, 2))
    status = Column(Integer, default=1)

    product = relationship("Product", back_populates="batches")
    alerts = relationship("Alert", back_populates="batch")
    sales_detail = relationship("SalesDetail", back_populates="batch")
    purchase_detail = relationship("PurchaseDetail", back_populates="batch")


# ========================
# ALERTS
# ========================
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(100))
    batch_id = Column(Integer, ForeignKey("medicine_batches.id"))
    message = Column(Text)

    batch = relationship("MedicineBatch", back_populates="alerts")


# ========================
# SALES
# ========================
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    sale_date = Column(DateTime)
    total = Column(DECIMAL(10, 2))
    payment_method = Column(String(100))

    client = relationship("Client", back_populates="sales")
    user = relationship("User", back_populates="sales")
    details = relationship("SalesDetail", back_populates="sale")


# ========================
# SALES DETAIL
# ========================
class SalesDetail(Base):
    __tablename__ = "sales_detail"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    batch_id = Column(Integer, ForeignKey("medicine_batches.id"))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(10, 2))
    subtotal = Column(DECIMAL(10, 2))

    sale = relationship("Sale", back_populates="details")
    batch = relationship("MedicineBatch", back_populates="sales_detail")


# ========================
# SUPPLIERS
# ========================
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    phone = Column(String(50))
    email = Column(String(150))
    address = Column(String(200))
    city = Column(String(100))
    status = Column(Integer, default=1)

    purchases = relationship("Purchase", back_populates="supplier")


# ========================
# PURCHASES
# ========================
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    purchase_date = Column(DateTime)
    payment_method = Column(String(100))
    total = Column(DECIMAL(10, 2))

    user = relationship("User", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    details = relationship("PurchaseDetail", back_populates="purchase")


# ========================
# PURCHASE DETAIL
# ========================
class PurchaseDetail(Base):
    __tablename__ = "purchase_detail"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    batch_id = Column(Integer, ForeignKey("medicine_batches.id"))
    unit_price = Column(DECIMAL(10, 2))
    quantity = Column(Integer)
    subtotal = Column(DECIMAL(10, 2))

    purchase = relationship("Purchase", back_populates="details")
    batch = relationship("MedicineBatch", back_populates="purchase_detail")

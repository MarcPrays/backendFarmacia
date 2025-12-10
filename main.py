from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from utils.security import verify_password, get_password_hash

import os

from db.database import Base, engine, get_db
from routers.users import routerUser
from routers.categories import routerCategory
from routers.clients import routerClient
from routers.suppliers import routerSupplier
from routers.products import routerProduct
from routers.batches import routerBatch

# ========================
# CONFIG
# ========================
SECRET_KEY = "your_super_secret_key"  # Mejor cargar desde .env
ALGORITHM = "HS256"
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

# Crear tablas
Base.metadata.create_all(bind=engine)

# ========================
# AUTH
# ========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    from crud import users  # Importar aquí para evitar dependencias circulares
    user = users.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user

# ========================
# LOGIN ROUTE
# ========================
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from crud import users

    user = users.get_user_by_username(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

# ========================
# INCLUDE ROUTERS
# ========================
app.include_router(routerUser)
app.include_router(routerCategory)
app.include_router(routerClient)
app.include_router(routerSupplier)
app.include_router(routerProduct)
app.include_router(routerBatch)

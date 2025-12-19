from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from db.database import get_db
from db.models import User
from crud import users

# Configuración JWT
SECRET_KEY = "your_super_secret_key"  # Mejor cargar desde .env
ALGORITHM = "HS256"

# OAuth2 con auto_error=False para permitir token opcional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
oauth2_scheme_required = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtener el usuario actual desde el token JWT (opcional).
    Si el token es None o inválido, retorna None en lugar de lanzar excepción.
    Útil para rutas que pueden funcionar con o sin autenticación.
    Carga el rol del usuario para verificación de permisos.
    """
    from sqlalchemy.orm import joinedload
    
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        # Convertir de string a int (JWT almacena sub como string)
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        # Log del error pero no lanzar excepción
        print(f"Error al decodificar token: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al validar token: {e}")
        return None

    # Cargar usuario con su rol
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if user is None:
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme_required), db: Session = Depends(get_db)):
    """
    Obtener el usuario actual desde el token JWT (obligatorio).
    Si el token es None o inválido, lanza excepción 401.
    Útil para rutas que requieren autenticación obligatoria.
    Carga el rol del usuario para verificación de permisos.
    """
    from sqlalchemy.orm import joinedload
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autenticación requerido o inválido. Por favor, inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # Convertir de string a int (JWT almacena sub como string)
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        # Token expirado o inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cargar usuario con su rol
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from db.database import get_db
from db.models import User
from crud import users

# Configuración JWT
SECRET_KEY = "your_super_secret_key"  # Mejor cargar desde .env
ALGORITHM = "HS256"

# OAuth2 con auto_error=False para permitir token opcional
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
oauth2_scheme_required = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)


def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtener el usuario actual desde el token JWT (opcional).
    Si el token es None o inválido, retorna None en lugar de lanzar excepción.
    Útil para rutas que pueden funcionar con o sin autenticación.
    Carga el rol del usuario para verificación de permisos.
    """
    from sqlalchemy.orm import joinedload
    
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        # Convertir de string a int (JWT almacena sub como string)
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        # Log del error pero no lanzar excepción
        print(f"Error al decodificar token: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al validar token: {e}")
        return None

    # Cargar usuario con su rol
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if user is None:
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme_required), db: Session = Depends(get_db)):
    """
    Obtener el usuario actual desde el token JWT (obligatorio).
    Si el token es None o inválido, lanza excepción 401.
    Útil para rutas que requieren autenticación obligatoria.
    Carga el rol del usuario para verificación de permisos.
    """
    from sqlalchemy.orm import joinedload
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autenticación requerido o inválido. Por favor, inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # Convertir de string a int (JWT almacena sub como string)
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        # Token expirado o inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cargar usuario con su rol
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


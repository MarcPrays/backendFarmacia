try:
    # Intentar usar bcrypt directamente (más compatible)
    import bcrypt
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña usando bcrypt"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
except ImportError:
    # Fallback a passlib si bcrypt no está disponible
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña usando passlib"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña usando passlib"""
        return pwd_context.hash(password)

    
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña usando bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
except ImportError:
    # Fallback a passlib si bcrypt no está disponible
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña usando passlib"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña usando passlib"""
        return pwd_context.hash(password)

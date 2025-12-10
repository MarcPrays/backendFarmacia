from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from pathlib import Path

# Obtener el directorio del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env desde el directorio raíz del proyecto
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Variables de conexión desde .env
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")  # Permite contraseña vacía
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")  # Puerto por defecto 3306
MYSQL_DB = os.getenv("MYSQL_DB")

# Validar que las variables obligatorias estén configuradas
if not all([MYSQL_USER, MYSQL_HOST, MYSQL_DB]):
    raise ValueError(
        "Error: Faltan variables de entorno. Por favor, crea un archivo .env con las siguientes variables:\n"
        "MYSQL_USER=tu_usuario\n"
        "MYSQL_PASSWORD=tu_contraseña (opcional, dejar vacío si no tiene contraseña)\n"
        "MYSQL_HOST=localhost\n"
        "MYSQL_PORT=3307 (opcional, por defecto 3306)\n"
        "MYSQL_DB=nombre_base_datos"
    )

# Normalizar la contraseña: si está vacía o es None, usar None
# Esto asegura que no se intente usar una contraseña vacía
MYSQL_PASSWORD = MYSQL_PASSWORD.strip() if MYSQL_PASSWORD else None
HAS_PASSWORD = MYSQL_PASSWORD is not None and len(MYSQL_PASSWORD) > 0

# Construir URL DE CONEXION con codificación URL para caracteres especiales
# quote_plus codifica caracteres especiales como puntos, @, etc.
if HAS_PASSWORD:
    # Codificar usuario, contraseña y base de datos para evitar problemas con caracteres especiales
    encoded_user = quote_plus(str(MYSQL_USER))
    encoded_password = quote_plus(str(MYSQL_PASSWORD))
    encoded_db = quote_plus(str(MYSQL_DB))
    DATABASE_URL = f"mysql+pymysql://{encoded_user}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{encoded_db}"
else:
    encoded_user = quote_plus(str(MYSQL_USER))
    encoded_db = quote_plus(str(MYSQL_DB))
    DATABASE_URL = f"mysql+pymysql://{encoded_user}@{MYSQL_HOST}:{MYSQL_PORT}/{encoded_db}"

# OBJETO QUE MANEJA LA CONEXION
engine = create_engine(DATABASE_URL)

# Se crea una fábrica de sesiones de base de datos.
# - autocommit=False → las transacciones no se confirman automáticamente.
# - autoflush=False → evita que los cambios se sincronicen automáticamente con la base de datos.
# - bind=engine → vincula la sesión al motor de base de datos creado antes.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Se crea la clase "Base" para declarar los modelos de la base de datos (tablas)
Base = declarative_base()

# Se define una función que devuelve una sesión de base de datos.
def get_db():
    # nueva variable que manejara las querys en bd
    db = SessionLocal()
    try:
        # Se entrega la sesión al código que la requiera (con 'yield').
        yield db
    finally:
        # Al terminar, se asegura que la sesión se cierre (libera recursos).
        db.close()




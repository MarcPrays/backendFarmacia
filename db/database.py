from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Variables de conexión desde .env
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

# URL DE CONEXION
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

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




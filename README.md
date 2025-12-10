# Backend Farmacia API

API REST desarrollada con FastAPI para la gestión de una farmacia.

## Requisitos Previos

- Python 3.8 o superior
- MySQL instalado y ejecutándose
- pip (gestor de paquetes de Python)

## Instalación

### 1. Instalar dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos

1. Crea una base de datos en MySQL:
```sql
CREATE DATABASE farmacia_db;
```

2. Copia el archivo `env.example` y renómbralo a `.env`:
```bash
copy env.example .env
```

3. Edita el archivo `.env` con tus credenciales de MySQL:
```
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_HOST=localhost
MYSQL_DB=farmacia_db
```

## Ejecutar el programa

Para iniciar el servidor, ejecuta:

```bash
uvicorn main:app --reload
```

El servidor se ejecutará en: `http://localhost:8000`

### Documentación interactiva

Una vez que el servidor esté corriendo, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Estructura del Proyecto

```
backendFarmacia/
├── crud/          # Operaciones CRUD
├── db/            # Configuración de base de datos y modelos
├── routers/       # Rutas de la API
├── utils/         # Utilidades (seguridad, etc.)
└── main.py        # Punto de entrada de la aplicación
```

## Notas

- Las tablas se crean automáticamente al iniciar la aplicación
- Asegúrate de que MySQL esté corriendo antes de iniciar el servidor
- El modo `--reload` permite que el servidor se reinicie automáticamente cuando detecta cambios en el código


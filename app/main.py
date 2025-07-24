"""
Punto de entrada principal de la aplicación FastAPI.
Configura la aplicación, middleware, CORS y rutas.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.interfaces.api.v1.api_v1 import api_router
from app.infrastructure.db.mongo_client import mongo_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Conectar a la base de datos
    print("🚀 Iniciando aplicación...")
    try:
        mongo_client.connect()
        print("✅ Conectado a la base de datos (Mock)")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
    
    yield
    
    # Shutdown: Cerrar conexiones
    print("🛑 Cerrando aplicación...")
    try:
        mongo_client.disconnect()
        print("✅ Desconectado de la base de datos")
    except Exception as e:
        print(f"❌ Error al desconectar de la base de datos: {e}")

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    ## Clients API
    
    API REST para gestión de usuarios con autenticación JWT.
    
    ### Características principales:
    
    * **Registro de usuarios**: Crear nuevas cuentas con email y contraseña
    * **Autenticación JWT**: Sistema de tokens para proteger endpoints
    * **CRUD completo**: Crear, leer, actualizar y eliminar usuarios
    * **Paginación**: Listado eficiente de usuarios con paginación
    * **Soft Delete**: Desactivación de usuarios sin eliminar datos
    * **Clean Architecture**: Código organizado y mantenible
    
    ### Autenticación
    
    Para acceder a los endpoints protegidos, incluye el token JWT en el header:
    ```
    Authorization: Bearer <tu_token_jwt>
    ```
    
    ### Comenzar
    
    1. Registra un usuario en `/api/v1/users/register`
    2. Inicia sesión en `/api/v1/users/login` para obtener tu token
    3. Usa el token para acceder a los endpoints protegidos
    """,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador personalizado para excepciones HTTP.
    Devuelve respuestas consistentes en formato JSON.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Manejador para errores de validación (ValueError).
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "message": str(exc),
            "status_code": 400,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador para excepciones generales no capturadas.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "status_code": 500,
            "path": str(request.url)
        }
    )

# Incluir rutas de la API v1
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)

# Endpoint raíz
@app.get(
    "/",
    tags=["root"],
    summary="Root Endpoint",
    description="Endpoint raíz de la API"
)
async def root():
    """
    Endpoint raíz que proporciona información básica de la API.
    """
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
        "status": "running"
    }

# Endpoint de estado
@app.get(
    "/status",
    tags=["status"],
    summary="Application Status",
    description="Estado detallado de la aplicación"
)
async def status():
    """
    Proporciona información detallada del estado de la aplicación.
    """
    return {
        "application": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_connected": mongo_client.is_connected(),
        "api_docs": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health"
    }

# Función para ejecutar la aplicación durante desarrollo
def run_dev():
    """
    Ejecuta la aplicación en modo desarrollo.
    Solo usar para desarrollo local.
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_dev()
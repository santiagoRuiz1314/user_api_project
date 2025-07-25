"""
Punto de entrada principal de la aplicación FastAPI.
Configura la aplicación, middleware, CORS, rutas y manejadores de excepciones.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
from datetime import datetime
from app.core.config import settings
from app.interfaces.api.v1.api_v1 import api_router
from app.infrastructure.db.mongo_client import mongo_client
from app.core.exception_handlers import EXCEPTION_HANDLERS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Conectar a la base de datos
    logger.info("🚀 Iniciando aplicación...")
    try:
        mongo_client.connect()
        logger.info("✅ Conectado a la base de datos (Mock)")
    except Exception as e:
        logger.error(f"❌ Error al conectar a la base de datos: {e}")
    
    yield
    
    # Shutdown: Cerrar conexiones
    logger.info("🛑 Cerrando aplicación...")
    try:
        mongo_client.disconnect()
        logger.info("✅ Desconectado de la base de datos")
    except Exception as e:
        logger.error(f"❌ Error al desconectar de la base de datos: {e}")

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    ## Clients API - Clean Architecture Implementation
    
    API REST para gestión de usuarios con autenticación JWT implementada siguiendo 
    principios de Clean Architecture.
    
    ### 🏗️ Arquitectura
    
    - **Domain Layer**: Entidades y lógica de negocio pura
    - **Application Layer**: Casos de uso y orquestación
    - **Infrastructure Layer**: Implementaciones concretas (BD, Auth, etc.)
    - **Presentation Layer**: Controllers y API endpoints
    
    ### ✨ Características principales
    
    * **🔐 Autenticación JWT**: Sistema seguro de tokens Bearer
    * **👥 CRUD de Usuarios**: Operaciones completas de gestión
    * **📝 Validación robusta**: Validaciones con Pydantic y reglas de negocio
    * **🛡️ Seguridad**: Contraseñas hasheadas con bcrypt
    * **📊 Paginación**: Listados eficientes con paginación
    * **🗑️ Soft Delete**: Desactivación de usuarios sin pérdida de datos
    * **🚨 Manejo de errores**: Sistema centralizado de excepciones
    * **📖 Documentación**: OpenAPI/Swagger completa
    
    ### 🔗 Endpoints principales
    
    #### Autenticación (público)
    - `POST /api/v1/auth/register` - Registrar nuevo usuario
    - `POST /api/v1/auth/login` - Iniciar sesión
    
    #### Usuarios (requiere autenticación)
    - `POST /api/v1/users` - Crear usuario
    - `GET /api/v1/users/{id}` - Obtener usuario por ID
    - `GET /api/v1/users` - Listar usuarios
    - `PUT /api/v1/users/{id}` - Actualizar usuario
    - `DELETE /api/v1/users/{id}` - Eliminar usuario
    
    ### 🔑 Autenticación
    
    Para acceder a endpoints protegidos, incluye el token JWT:
    ```
    Authorization: Bearer <tu_token_jwt>
    ```
    
    ### 🚀 Inicio rápido
    
    1. **Registrarse**: `POST /api/v1/auth/register`
    2. **Iniciar sesión**: `POST /api/v1/auth/login`
    3. **Usar token**: Incluir en header `Authorization: Bearer <token>`
    4. **Explorar API**: Usar los endpoints protegidos
    
    ### 📊 Códigos de respuesta
    
    - `200` - Operación exitosa
    - `201` - Recurso creado
    - `400` - Datos de entrada inválidos
    - `401` - No autenticado
    - `403` - Sin permisos
    - `404` - Recurso no encontrado
    - `409` - Conflicto (ej: email ya existe)
    - `422` - Error de reglas de negocio
    - `500` - Error interno del servidor
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Registrar manejadores de excepciones
for exception_type, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exception_type, handler)

# Incluir rutas de la API v1
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)

# Middleware para logging de requests
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de todas las requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Endpoint raíz
@app.get(
    "/",
    tags=["root"],
    summary="Root Endpoint",
    description="Endpoint raíz que proporciona información básica de la API"
)
async def root():
    """
    Endpoint raíz con información básica de la API.
    
    Proporciona enlaces útiles y estado general del sistema.
    """
    return {
        "message": f"¡Bienvenido a {settings.PROJECT_NAME}! 🚀",
        "version": settings.PROJECT_VERSION,
        "architecture": "Clean Architecture",
        "status": "active",
        "links": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "api_v1": settings.API_V1_PREFIX,
            "health_check": f"{settings.API_V1_PREFIX}/health",
            "api_info": f"{settings.API_V1_PREFIX}/info"
        },
        "authentication": {
            "register": f"{settings.API_V1_PREFIX}/auth/register",
            "login": f"{settings.API_V1_PREFIX}/auth/login",
            "type": "JWT Bearer Token"
        }
    }

# Endpoint de estado detallado
@app.get(
    "/status",
    tags=["status"],
    summary="Application Status",
    description="Estado detallado de la aplicación y sus componentes"
)
async def status():
    """
    Proporciona información detallada del estado de la aplicación.
    
    Incluye estado de conexiones, configuración y métricas básicas.
    """
    return {
        "application": {
            "name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "services": {
            "database": {
                "status": "connected" if mongo_client.is_connected() else "disconnected",
                "type": "Mock MongoDB (development)"
            },
            "authentication": {
                "status": "active",
                "type": "JWT",
                "algorithm": settings.JWT_ALGORITHM,
                "expiration_minutes": settings.JWT_EXPIRATION_TIME_MINUTES
            }
        },
        "api": {
            "version": "v1",
            "prefix": settings.API_V1_PREFIX,
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "health_checks": {
            "main": f"{settings.API_V1_PREFIX}/health",
            "detailed": "/status"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_status": "running"
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
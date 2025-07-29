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
        success = await mongo_client.connect()
        if success:
            logger.info("✅ Conectado exitosamente a MongoDB")
            logger.info(f"📊 Base de datos: {settings.DATABASE_NAME}")
            logger.info(f"🔗 URL: {settings.MONGODB_URL}")
        else:
            logger.error("❌ No se pudo conectar a MongoDB")
            logger.error("⚠️  La aplicación continuará pero las operaciones de BD fallarán")
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {e}")
        logger.error("⚠️  La aplicación continuará pero las operaciones de BD fallarán")
    
    yield
    
    # Shutdown: Cerrar conexiones
    logger.info("🛑 Cerrando aplicación...")
    try:
        await mongo_client.disconnect()
        logger.info("✅ Desconectado de MongoDB")
    except Exception as e:
        logger.error(f"❌ Error al desconectar de MongoDB: {e}")

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
    ## Clients API -

    API REST para gestión de usuarios con autenticación JWT implementada siguiendo principios de Clean Architecture.

    ### Arquitectura

    - **Domain Layer**: Entidades y lógica de negocio pura
    - **Application Layer**: Casos de uso y orquestación  
    - **Infrastructure Layer**: Implementaciones concretas (BD, Auth, etc.)
    - **Presentation Layer**: Controllers y endpoints de API

    ### Características principales

    * **Autenticación JWT**: Sistema seguro de tokens Bearer con expiración configurable (30 minutos)
    * **CRUD Completo de Usuarios**: Operaciones completas de gestión con validaciones robustas
    * **Validación Integral**: Validaciones con Pydantic v2.5.0 y reglas de negocio en casos de uso
    * **Seguridad Avanzada**: Contraseñas hasheadas con bcrypt, validación de tokens, usuarios activos/inactivos
    * **Paginación Eficiente**: Listados con parámetros skip/limit (máximo 100 por página) y metadatos
    * **Soft Delete**: Desactivación de usuarios preservando datos históricos
    * **Manejo Centralizado de Errores**: Sistema robusto de excepciones personalizadas por dominio
    * **Documentación OpenAPI**: Swagger UI y ReDoc con esquemas detallados
    * **MongoDB Asíncrono**: Base de datos NoSQL con Motor driver, índices optimizados y health checks

    ### Endpoints principales

    #### Autenticación (público)
    - **`POST /api/v1/auth/register`** - Registrar nuevo usuario
    - **`POST /api/v1/auth/login`** - Iniciar sesión y obtener token JWT
    - **`GET /api/v1/auth/validate-token`** - Validar token JWT (requiere autenticación)

    #### Usuarios (requiere autenticación)
    - **`POST /api/v1/users`** - Crear usuario (endpoint administrativo protegido)
    - **`GET /api/v1/users/user/{user_id}`** - Obtener usuario por ID específico
    - **`GET /api/v1/users`** - Listar usuarios con paginación
    - **`PUT /api/v1/users/user/{user_id}`** - Actualizar usuario existente
    - **`DELETE /api/v1/users/user/{user_id}`** - Eliminar usuario (soft delete)
    - **`GET /api/v1/users/me/profile`** - Obtener perfil del usuario autenticado

    #### Utilidades y monitoreo
    - **`GET /api/v1/health`** - Health check básico de la API
    - **`GET /api/v1/info`** - Información detallada de la API
    - **`GET /status`** - Estado completo del sistema con estadísticas

    ### Autenticación

    Para acceder a endpoints protegidos, incluye el token JWT:
    ```
    Authorization: Bearer <tu_token_jwt>
    ```

    **Características del sistema de autenticación:**
    - Tokens JWT con expiración de 30 minutos (configurable)
    - Validación estricta: email único, contraseñas de 6-128 caracteres
    - Solo usuarios activos pueden autenticarse
    - Permisos granulares: usuarios solo pueden modificar sus propios datos

    ### Inicio rápido

    1. **Registrarse**: `POST /api/v1/auth/register`
    2. **Iniciar sesión**: `POST /api/v1/auth/login` → Obtiene token JWT + datos del usuario
    3. **Usar token**: Incluir en header `Authorization: Bearer <token>`
    4. **Explorar API**: Usar los endpoints protegidos con paginación

    ### Base de datos

    - **MongoDB 7.0**: Base de datos NoSQL con alta disponibilidad
    - **Motor 3.3.2**: Driver asíncrono para Python con conexión persistente
    - **Índices optimizados**: 
    - Único en `email` para unicidad
    - Compuesto en `is_active + email` para consultas eficientes
    - Simple en `is_active` para filtros de usuarios activos
    - **Health checks automáticos**: Monitoreo de estado de conexión
    - **Colección `users`** en base de datos `clients_db`

    ### Parámetros de paginación

    Para listado de usuarios (`GET /api/v1/users`):
    - **`skip`**: Registros a saltar (default: 0, mínimo: 0)
    - **`limit`**: Registros por página (default: 20, rango: 1-100)

    **Ejemplo**: `GET /api/v1/users?skip=20&limit=10`
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
        "database": {
            "type": "MongoDB",
            "status": "connected" if mongo_client.is_connected() else "disconnected",
            "database": settings.DATABASE_NAME
        },
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
            "validate": f"{settings.API_V1_PREFIX}/auth/validate-token",
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
    # Obtener estadísticas de la base de datos si está conectada
    db_stats = {}
    if mongo_client.is_connected():
        try:
            db_stats = {
                "total_users": await mongo_client.count_users(),
                "active_users": await mongo_client.count_active_users(),
            }
        except Exception as e:
            db_stats = {"error": f"No se pudieron obtener estadísticas: {str(e)}"}
    
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
                "type": "MongoDB",
                "url": settings.MONGODB_URL,
                "database": settings.DATABASE_NAME,
                "collection": settings.USERS_COLLECTION,
                "statistics": db_stats
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
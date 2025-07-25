"""
Configuración de la API v1.
Incluye todas las rutas de la versión 1 de la API.
"""
from fastapi import APIRouter
from app.interfaces.api.v1.routes.user_routes import router as user_router
from app.interfaces.api.v1.routes.auth_routes import router as auth_router

# Router principal para la API v1
api_router = APIRouter()

# Incluir rutas de autenticación (sin autenticación requerida)
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"]
)

# Incluir rutas de usuarios (requieren autenticación)
api_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"]
)

# Endpoint de health check
@api_router.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Verifica el estado de la API"
)
async def health_check():
    """
    Endpoint de health check para verificar que la API está funcionando.
    
    Returns información básica del estado del servicio.
    """
    return {
        "status": "healthy",
        "message": "API is running",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "authentication": "active"
        }
    }

# Endpoint de información de la API
@api_router.get(
    "/info",
    tags=["info"],
    summary="API Information",
    description="Información general sobre la API"
)
async def api_info():
    """
    Proporciona información general sobre la API.
    
    Returns metadatos de la API como versión, descripción, endpoints disponibles, etc.
    """
    return {
        "name": "Clients API",
        "version": "1.0.0",
        "description": "API REST para gestión de usuarios con autenticación JWT",
        "architecture": "Clean Architecture",
        "features": [
            "Registro y autenticación de usuarios",
            "CRUD completo de usuarios",
            "Autenticación JWT",
            "Paginación en listados",
            "Soft delete de usuarios",
            "Validación con Pydantic",
            "Documentación OpenAPI"
        ],
        "endpoints": {
            "authentication": [
                "POST /api/v1/auth/login",
                "POST /api/v1/auth/register"
            ],
            "users": [
                "POST /api/v1/users",
                "GET /api/v1/users/{id}",
                "GET /api/v1/users",
                "PUT /api/v1/users/{id}",
                "DELETE /api/v1/users/{id}"
            ],
            "utility": [
                "GET /api/v1/health",
                "GET /api/v1/info"
            ]
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "header": "Authorization: Bearer <token>",
            "expiration": "30 minutes"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/api/v1/openapi.json"
        },
        "status": "active"
    }
"""
Configuración de la API v1.
Incluye todas las rutas de la versión 1 de la API.
"""
from fastapi import APIRouter
from app.interfaces.api.v1.routes.user_routes import router as user_router

# Router principal para la API v1
api_router = APIRouter()

# Incluir rutas de usuarios
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
        "version": "1.0.0"
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
    
    Returns metadatos de la API como versión, descripción, etc.
    """
    return {
        "name": "Clients API",
        "version": "1.0.0",
        "description": "API para gestión de usuarios con autenticación JWT",
        "features": [
            "Registro de usuarios",
            "Autenticación JWT",
            "CRUD de usuarios",
            "Paginación",
            "Soft delete"
        ],
        "documentation": "/docs",
        "status": "active"
    }
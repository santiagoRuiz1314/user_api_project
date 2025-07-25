"""
Rutas de autenticación.
Maneja login, registro y operaciones de autenticación.
"""
from fastapi import APIRouter, Depends, status
from app.controllers.user_controller import user_controller
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserLoginRequest
)
from app.interfaces.schemas.user_response import (
    UserCreateResponse,
    UserLoginResponse,
    ErrorResponse,
    user_to_response
)
from app.core.security import get_current_active_user
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    ConflictException,
    InfrastructureException
)

# Router para autenticación
router = APIRouter(tags=["authentication"])

@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario con email y contraseña, devuelve un token JWT",
    responses={
        200: {"description": "Login exitoso", "model": UserLoginResponse},
        401: {"description": "Credenciales inválidas"},
        400: {"description": "Datos de entrada inválidos"},
        422: {"description": "Usuario inactivo"},
        500: {"description": "Error interno del servidor"}
    }
)
async def login(request: UserLoginRequest):
    """
    Autentica un usuario con email y contraseña.
    
    - **email**: Email del usuario registrado
    - **password**: Contraseña del usuario
    
    Devuelve un token JWT para autenticación en futuras requests.
    
    **Nota**: Las excepciones se manejan automáticamente por el sistema centralizado.
    """
    # Las excepciones específicas del dominio se propagan automáticamente
    # y son manejadas por el sistema centralizado de exception handlers
    result = await user_controller.login_user(request)
    return result

@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario",
    responses={
        201: {"description": "Usuario creado exitosamente", "model": UserCreateResponse},
        400: {"description": "Datos de entrada inválidos"},
        409: {"description": "Usuario ya existe"},
        500: {"description": "Error interno del servidor"}
    }
)
async def register(request: UserCreateRequest):
    """
    Registra un nuevo usuario.
    
    - **email**: Email válido y único
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Crea el usuario y devuelve la información básica (sin contraseña).
    
    **Nota**: Las excepciones se manejan automáticamente por el sistema centralizado.
    """
    # Las excepciones específicas del dominio se propagan automáticamente
    # y son manejadas por el sistema centralizado de exception handlers
    result = await user_controller.create_user(request)
    return result

@router.get(
    "/validate-token",
    summary="Validar token",
    description="Valida si un token JWT es válido",
    responses={
        200: {"description": "Token válido"},
        401: {"description": "Token inválido o expirado"}
    }
)
async def validate_token(current_user = Depends(get_current_active_user)):
    """
    Valida el token JWT del usuario autenticado.
    
    **Requiere autenticación JWT.**
    
    Endpoint útil para verificar si un token sigue siendo válido.
    """
    user_response = user_to_response(current_user)
    return {
        "valid": True,
        "user": user_response,
        "message": "Token válido"
    }
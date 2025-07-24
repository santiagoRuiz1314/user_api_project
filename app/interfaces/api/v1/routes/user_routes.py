"""
Rutas de la API para operaciones de usuario.
Define los endpoints REST para el manejo de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.controllers.user_controller import user_controller
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserQueryRequest
)
from app.interfaces.schemas.user_response import (
    UserCreateResponse,
    UserLoginResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    UserListResponse,
    ErrorResponse,
    user_to_response
)
from app.core.security import get_current_active_user
from app.domain.user.user_entity import User

# Router para las rutas de usuario
router = APIRouter(tags=["users"])

@router.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con email y contraseña"
)
async def register_user(request: UserCreateRequest):
    """
    Registra un nuevo usuario.
    
    - **email**: Email válido del usuario
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Returns el usuario creado con su información básica.
    """
    try:
        return await user_controller.create_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post(
    "/login",
    response_model=UserLoginResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve un token JWT"
)
async def login_user(request: UserLoginRequest):
    """
    Autentica un usuario.
    
    - **email**: Email del usuario registrado
    - **password**: Contraseña del usuario
    
    Returns un token JWT para futuras peticiones autenticadas.
    """
    try:
        return await user_controller.login_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get(
    "/me",
    response_model=dict,
    summary="Obtener perfil actual",
    description="Obtiene la información del usuario autenticado"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    Requiere autenticación JWT en el header Authorization.
    """
    try:
        user_response = user_to_response(current_user)
        return {
            "user": user_response,
            "message": "Perfil obtenido exitosamente"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get(
    "/{user_id}",
    response_model=dict,
    summary="Obtener usuario por ID",
    description="Obtiene un usuario específico por su ID"
)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene un usuario por su ID.
    
    - **user_id**: ID único del usuario
    
    Los usuarios solo pueden ver su propia información.
    """
    try:
        user = await user_controller.get_user_by_id(user_id, current_user)
        user_response = user_to_response(user)
        return {
            "user": user_response,
            "message": "Usuario obtenido exitosamente"
        }
    except ValueError as e:
        if "no encontrado" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permisos" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get(
    "/",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Obtiene una lista paginada de usuarios"
)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros por página"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista usuarios con paginación.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros por página (default: 20, max: 100)
    """
    try:
        query = UserQueryRequest(skip=skip, limit=limit)
        return await user_controller.list_users(query, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put(
    "/{user_id}",
    response_model=UserUpdateResponse,
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario"
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza un usuario.
    
    - **user_id**: ID único del usuario a actualizar
    - **email**: Nuevo email (opcional)
    - **password**: Nueva contraseña (opcional)
    
    Los usuarios solo pueden actualizar su propia información.
    """
    try:
        return await user_controller.update_user(user_id, request, current_user)
    except ValueError as e:
        if "no encontrado" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permisos" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete(
    "/{user_id}",
    response_model=UserDeleteResponse,
    summary="Desactivar usuario",
    description="Desactiva un usuario (soft delete)"
)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Desactiva un usuario (soft delete).
    
    - **user_id**: ID único del usuario a desactivar
    
    Los usuarios solo pueden desactivar su propia cuenta.
    El usuario se marca como inactivo pero no se elimina de la base de datos.
    """
    try:
        return await user_controller.delete_user_soft(user_id, current_user)
    except ValueError as e:
        if "no encontrado" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permisos" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete(
    "/{user_id}/permanent",
    response_model=UserDeleteResponse,
    summary="Eliminar usuario permanentemente",
    description="Elimina un usuario permanentemente (hard delete)"
)
async def delete_user_permanent(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un usuario permanentemente (hard delete).
    
    - **user_id**: ID único del usuario a eliminar
    
    ⚠️ **ADVERTENCIA**: Esta acción es irreversible.
    Los usuarios solo pueden eliminar su propia cuenta.
    """
    try:
        return await user_controller.delete_user_hard(user_id, current_user)
    except ValueError as e:
        if "no encontrado" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permisos" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post(
    "/{user_id}/reactivate",
    response_model=UserUpdateResponse,
    summary="Reactivar usuario",
    description="Reactiva un usuario previamente desactivado"
)
async def reactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Reactiva un usuario previamente desactivado.
    
    - **user_id**: ID único del usuario a reactivar
    
    Los usuarios solo pueden reactivar su propia cuenta.
    """
    try:
        return await user_controller.reactivate_user(user_id, current_user)
    except ValueError as e:
        if "no encontrado" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permisos" in str(e).lower() or "permission" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
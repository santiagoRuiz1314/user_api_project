"""
Rutas de la API para operaciones CRUD de usuarios - VERSIÓN CORREGIDA.
Define los endpoints REST con manejo robusto de respuestas.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from app.controllers.user_controller import user_controller
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserUpdateRequest,
    UserQueryRequest
)
from app.interfaces.schemas.user_response import (
    UserCreateResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    UserListResponse,
    ErrorResponse,
    user_to_response
)
from app.core.security import get_current_active_user
from app.domain.user.user_entity import User

# Router para las rutas de usuario (requieren autenticación)
router = APIRouter(tags=["users"])

# CRÍTICO: Las rutas específicas deben ir ANTES que las rutas con parámetros
# para evitar conflictos en el routing de FastAPI

@router.get(
    "/me/profile",
    response_model=dict,
    summary="Obtener perfil actual",
    description="Obtiene la información del usuario autenticado"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el perfil del usuario autenticado.
    
    **Requiere autenticación JWT.**
    
    Devuelve la información completa del usuario que está autenticado.
    """
    try:
        # 🔧 FIX: Usar el controller corregido que retorna dict
        result = await user_controller.get_current_user_profile(current_user)
        return result
    except Exception as e:
        # En caso de error, el exception handler centralizado se encargará
        raise

@router.post(
    "",
    response_model=dict,  # 🔧 FIX: Cambiar a dict genérico
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    description="Crea un nuevo usuario (endpoint administrativo)"
)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea un nuevo usuario.
    
    **Requiere autenticación JWT.**
    
    - **email**: Email válido del usuario
    - **password**: Contraseña (mínimo 6 caracteres)
    
    Este endpoint está protegido y requiere autenticación.
    """
    try:
        result = await user_controller.create_user(request)
        return result
    except Exception as e:
        raise

@router.get(
    "/user/{user_id}",
    response_model=dict,  # 🔧 FIX: Cambiar a dict genérico
    summary="Obtener usuario por ID",
    description="Obtiene información de un usuario específico"
)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene un usuario por su ID.
    
    **Requiere autenticación JWT.**
    
    - **user_id**: ID único del usuario a obtener
    
    Los usuarios pueden ver información básica de otros usuarios,
    pero solo pueden ver detalles completos de su propio perfil.
    """
    print(f"🎯 ROUTER: get_user_by_id llamado con ID: {user_id}")
    print(f"🔐 ROUTER: current_user: {current_user.email}")
    
    try:
        # 🔧 FIX: El controller ahora retorna dict correctamente
        result = await user_controller.get_user_by_id(user_id, current_user)
        print(f"✅ ROUTER: Respuesta recibida del controller: {type(result)}")
        return result
    except Exception as e:
        print(f"❌ ROUTER: Excepción capturada: {e}")
        # El exception handler centralizado se encargará
        raise

@router.put(
    "/user/{user_id}",
    response_model=dict,  # 🔧 FIX: Cambiar a dict genérico
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario existente"
)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza un usuario existente.
    
    **Requiere autenticación JWT.**
    
    - **user_id**: ID único del usuario a actualizar
    - **email**: Nuevo email (opcional)
    - **password**: Nueva contraseña (opcional)
    
    Los usuarios solo pueden actualizar su propia información,
    salvo que tengan permisos administrativos.
    """
    try:
        result = await user_controller.update_user(user_id, request, current_user)
        return result
    except Exception as e:
        raise

@router.delete(
    "/user/{user_id}",
    response_model=dict,  # 🔧 FIX: Cambiar a dict genérico
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema"
)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina un usuario del sistema.
    
    **Requiere autenticación JWT.**
    
    - **user_id**: ID único del usuario a eliminar
    
    Por defecto realiza un soft delete (desactivación).
    Los usuarios solo pueden eliminar su propia cuenta,
    salvo que tengan permisos administrativos.
    """
    try:
        result = await user_controller.delete_user_soft(user_id, current_user)
        return result
    except Exception as e:
        raise

@router.get(
    "",
    response_model=dict,  # 🔧 FIX: Cambiar a dict genérico
    summary="Listar todos los usuarios",
    description="Obtiene una lista paginada de todos los usuarios"
)
async def list_all_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros por página"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos los usuarios con paginación.
    
    **Requiere autenticación JWT.**
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Límite de registros por página (default: 20, max: 100)
    
    Devuelve información básica de todos los usuarios activos.
    """
    try:
        query = UserQueryRequest(skip=skip, limit=limit)
        result = await user_controller.list_users(query, current_user)
        return result
    except Exception as e:
        raise
"""
Esquemas de response para operaciones de usuario.
Define la estructura de datos de salida de la API.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserResponse(BaseModel):
    """Esquema base de respuesta para usuario."""
    
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Configuración del modelo Pydantic."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserCreateResponse(BaseModel):
    """Respuesta para creación de usuario."""
    
    user: UserResponse
    message: str = "Usuario creado exitosamente"

class UserLoginResponse(BaseModel):
    """Respuesta para login de usuario."""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int  # minutos hasta expiración

class UserUpdateResponse(BaseModel):
    """Respuesta para actualización de usuario."""
    
    user: UserResponse
    message: str = "Usuario actualizado exitosamente"

class UserListResponse(BaseModel):
    """Respuesta para listado de usuarios."""
    
    users: List[UserResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

class UserDeleteResponse(BaseModel):
    """Respuesta para eliminación de usuario."""
    
    message: str = "Usuario eliminado exitosamente"
    deleted_id: str

class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    
    error: str
    message: str
    status_code: int

class SuccessResponse(BaseModel):
    """Respuesta de éxito genérica."""
    
    message: str
    success: bool = True

# Funciones de utilidad para convertir entidades a responses
def user_to_response(user) -> UserResponse:
    """Convierte una entidad User a UserResponse."""
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

def users_to_list_response(
    users: List, 
    total: int, 
    skip: int, 
    limit: int
) -> UserListResponse:
    """Convierte una lista de usuarios a UserListResponse."""
    user_responses = [user_to_response(user) for user in users]
    has_more = skip + len(users) < total
    
    return UserListResponse(
        users=user_responses,
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )
"""
Esquemas de response para operaciones de usuario - VERSIÓN CORREGIDA.
Define la estructura de datos de salida de la API compatible con Pydantic v2.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

class UserResponse(BaseModel):
    """Esquema base de respuesta para usuario."""
    
    # 🔧 FIX: Configuración actualizada para Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserCreateResponse(BaseModel):
    """Respuesta para creación de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user: UserResponse
    message: str = "Usuario creado exitosamente"

class UserDetailResponse(BaseModel):
    """Respuesta para detalles de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user: UserResponse
    message: str = "Usuario obtenido exitosamente"

class UserProfileResponse(BaseModel):
    """Respuesta para perfil de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user: UserResponse
    message: str = "Perfil obtenido exitosamente"

class UserLoginResponse(BaseModel):
    """Respuesta para login de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # minutos hasta expiración
    user_id: str
    email: str
    user: UserResponse

class UserUpdateResponse(BaseModel):
    """Respuesta para actualización de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    user: UserResponse
    message: str = "Usuario actualizado exitosamente"

class UserListResponse(BaseModel):
    """Respuesta para listado de usuarios."""
    
    model_config = ConfigDict(from_attributes=True)
    
    users: List[UserResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

class UserDeleteResponse(BaseModel):
    """Respuesta para eliminación de usuario."""
    
    model_config = ConfigDict(from_attributes=True)
    
    message: str = "Usuario eliminado exitosamente"
    deleted_id: str

class ErrorResponse(BaseModel):
    """Respuesta de error estándar."""
    
    model_config = ConfigDict(from_attributes=True)
    
    error: bool = True
    message: str
    status_code: int
    error_code: Optional[str] = None
    timestamp: str
    path: Optional[str] = None
    details: Optional[dict] = None

class SuccessResponse(BaseModel):
    """Respuesta de éxito genérica."""
    
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = True
    message: str
    data: Optional[Any] = None

# 🔧 FIX: Funciones de utilidad actualizadas
def user_to_response(user) -> UserResponse:
    """
    Convierte una entidad User a UserResponse.
    Compatible con Pydantic v2.
    """
    if not user:
        return None
        
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

def user_to_dict(user) -> dict:
    """
    Convierte una entidad User a diccionario.
    Maneja correctamente la serialización de datetime.
    """
    if not user:
        return None
        
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }

def users_to_list_response(
    users: List, 
    total: int, 
    skip: int, 
    limit: int
) -> dict:
    """
    Convierte una lista de usuarios a diccionario de respuesta.
    Versión corregida que retorna dict en lugar de modelo Pydantic.
    """
    if not users:
        users = []
    
    # Convertir usuarios a diccionarios
    user_dicts = []
    for user in users:
        if user:
            user_dicts.append(user_to_dict(user))
    
    has_more = skip + len(users) < total
    
    return {
        "users": user_dicts,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": has_more
    }
"""
DTOs (Data Transfer Objects) para la capa de aplicación.
Estos DTOs actúan como contratos entre las capas y facilitan la serialización.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class UserDTO:
    """
    DTO para transferir datos de usuario entre capas.
    Representa los datos de un usuario de forma serializable.
    """
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class UserCreateDTO:
    """DTO para datos de creación de usuario."""
    email: str
    password: str

@dataclass
class UserUpdateDTO:
    """DTO para datos de actualización de usuario."""
    email: Optional[str] = None
    password: Optional[str] = None

@dataclass
class UserListDTO:
    """DTO para listado paginado de usuarios."""
    users: List[UserDTO]
    total: int
    skip: int
    limit: int
    has_more: bool

@dataclass
class UserLoginDTO:
    """DTO para respuesta de login."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str
    email: str
    user: UserDTO

@dataclass
class OperationResultDTO:
    """DTO genérico para resultados de operaciones."""
    success: bool
    message: str
    data: Optional[dict] = None
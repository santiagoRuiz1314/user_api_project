"""
Esquemas de request para operaciones de usuario.
Define la estructura de datos de entrada para la API.
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreateRequest(BaseModel):
    """Esquema para crear un nuevo usuario."""
    
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """Valida que la contraseña cumpla con los requisitos mínimos."""
        if len(v) < 6:
            raise ValueError('Password debe tener al menos 6 caracteres')
        if len(v) > 128:
            raise ValueError('Password no puede tener más de 128 caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Valida y normaliza el email."""
        return v.lower().strip()

class UserLoginRequest(BaseModel):
    """Esquema para login de usuario."""
    
    email: EmailStr
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        """Valida y normaliza el email."""
        return v.lower().strip()

class UserUpdateRequest(BaseModel):
    """Esquema para actualizar un usuario."""
    
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Valida que la contraseña cumpla con los requisitos mínimos."""
        if v is not None:
            if len(v) < 6:
                raise ValueError('Password debe tener al menos 6 caracteres')
            if len(v) > 128:
                raise ValueError('Password no puede tener más de 128 caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Valida y normaliza el email."""
        if v is not None:
            return v.lower().strip()
        return v
    
    def has_updates(self) -> bool:
        """Verifica si hay campos para actualizar."""
        return any([
            self.email is not None,
            self.password is not None
        ])

class UserQueryRequest(BaseModel):
    """Esquema para consultas paginadas de usuarios."""
    
    skip: int = 0
    limit: int = 20
    
    @validator('skip')
    def validate_skip(cls, v):
        """Valida que skip sea no negativo."""
        if v < 0:
            raise ValueError('Skip debe ser mayor o igual a 0')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        """Valida que limit esté en un rango razonable."""
        if v < 1:
            raise ValueError('Limit debe ser mayor a 0')
        if v > 100:
            raise ValueError('Limit no puede ser mayor a 100')
        return v
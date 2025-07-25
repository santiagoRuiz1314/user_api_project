"""
Caso de uso: Obtener Usuario por ID.
Encapsula la lógica de negocio para obtener un usuario específico.
"""
from typing import Optional
from app.domain.user.user_entity import User
from app.infrastructure.db.user_model import user_model
from app.core.exceptions import (
    ValidationException,
    UserNotFoundException,
    AuthorizationException,
    UserInactiveException
)

class GetUserByIdUseCase:
    """
    Caso de uso para obtener un usuario por su ID.
    Incluye validaciones de negocio y permisos apropiados.
    """
    
    def __init__(self):
        self.user_model = user_model
    
    async def execute(self, user_id: str, requesting_user_id: str) -> User:
        """
        Ejecuta el caso de uso de obtener usuario por ID.
        
        Args:
            user_id: ID del usuario a obtener
            requesting_user_id: ID del usuario que hace la petición
            
        Returns:
            Entidad User encontrada
            
        Raises:
            ValidationException: Si hay errores de validación
            UserNotFoundException: Si el usuario no existe
            UserInactiveException: Si el usuario está inactivo
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValidationException("User ID es requerido", "user_id")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValidationException("Requesting user ID es requerido", "requesting_user_id")
        
        # Verificar que el usuario solicitante existe y está activo
        requesting_user = await self.user_model.get_by_id(requesting_user_id)
        if not requesting_user:
            raise AuthorizationException("Usuario solicitante no encontrado")
        
        if not requesting_user.is_active:
            raise UserInactiveException(requesting_user_id)
        
        # Buscar el usuario solicitado
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        # Verificar que el usuario solicitado esté activo
        if not user.is_active:
            raise UserNotFoundException(user_id)  # Por seguridad, no revelamos que existe pero está inactivo
        
        # Permitir acceso a información básica de usuarios activos
        # En una API pública, los usuarios pueden ver perfiles básicos de otros usuarios
        # Si se necesita información más sensible, se podría agregar lógica de permisos aquí
        
        return user
    
    async def execute_own_profile(self, user_id: str) -> User:
        """
        Ejecuta el caso de uso para obtener el perfil propio del usuario.
        Útil para el endpoint /me/profile.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Entidad User encontrada
            
        Raises:
            ValidationException: Si hay errores de validación
            UserNotFoundException: Si el usuario no existe
            UserInactiveException: Si el usuario está inactivo
        """
        if not user_id or not user_id.strip():
            raise ValidationException("User ID es requerido", "user_id")
        
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        if not user.is_active:
            raise UserInactiveException(user_id)
        
        return user
    
    async def execute_by_admin(self, user_id: str) -> User:
        """
        Ejecuta el caso de uso como administrador (sin restricciones de permisos).
        Útil para casos internos del sistema o funciones administrativas.
        
        Args:
            user_id: ID del usuario a obtener
            
        Returns:
            Entidad User encontrada (incluso si está inactivo)
            
        Raises:
            ValidationException: Si hay errores de validación
            UserNotFoundException: Si el usuario no existe
        """
        if not user_id or not user_id.strip():
            raise ValidationException("User ID es requerido", "user_id")
        
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        return user

# Instancia del caso de uso
get_user_by_id_use_case = GetUserByIdUseCase()
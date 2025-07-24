"""
Caso de uso: Obtener Usuario por ID.
Encapsula la lógica de negocio para obtener un usuario específico.
"""
from typing import Optional
from app.domain.user.user_entity import User
from app.infrastructure.db.user_model import user_model

class GetUserByIdUseCase:
    """
    Caso de uso para obtener un usuario por su ID.
    Incluye validaciones de negocio y permisos.
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
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        # Buscar usuario
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar permisos: un usuario solo puede ver su propia información
        # En una implementación más compleja, podríamos tener roles de admin
        if user_id != requesting_user_id:
            raise ValueError("No tienes permisos para ver este usuario")
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise ValueError("Usuario no encontrado")
        
        return user
    
    async def execute_by_admin(self, user_id: str) -> User:
        """
        Ejecuta el caso de uso como administrador (sin restricciones de permisos).
        Útil para casos internos del sistema.
        
        Args:
            user_id: ID del usuario a obtener
            
        Returns:
            Entidad User encontrada
            
        Raises:
            ValueError: Si el usuario no existe
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        return user

# Instancia del caso de uso
get_user_by_id_use_case = GetUserByIdUseCase()
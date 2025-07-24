"""
Caso de uso: Eliminar Usuario.
Encapsula la lógica de negocio para eliminar usuarios.
"""
from app.domain.user.user_entity import User
from app.infrastructure.db.user_model import user_model

class DeleteUserUseCase:
    """
    Caso de uso para eliminar un usuario.
    Maneja tanto soft delete (desactivación) como hard delete (eliminación física).
    """
    
    def __init__(self):
        self.user_model = user_model
    
    async def execute_soft_delete(
        self,
        user_id: str,
        requesting_user_id: str
    ) -> User:
        """
        Ejecuta un soft delete (desactivación) del usuario.
        
        Args:
            user_id: ID del usuario a desactivar
            requesting_user_id: ID del usuario que hace la petición
            
        Returns:
            Entidad User desactivada
            
        Raises:
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        # Verificar permisos: un usuario solo puede eliminar su propia cuenta
        if user_id != requesting_user_id:
            raise ValueError("No tienes permisos para eliminar este usuario")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if not user.is_active:
            raise ValueError("Usuario ya está inactivo")
        
        # Desactivar usuario (soft delete)
        user.deactivate()
        
        # Guardar cambios
        updated_user = await self.user_model.update(user)
        
        return updated_user
    
    async def execute_hard_delete(
        self,
        user_id: str,
        requesting_user_id: str
    ) -> str:
        """
        Ejecuta un hard delete (eliminación física) del usuario.
        
        Args:
            user_id: ID del usuario a eliminar
            requesting_user_id: ID del usuario que hace la petición
            
        Returns:
            ID del usuario eliminado
            
        Raises:
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        # Verificar permisos: un usuario solo puede eliminar su propia cuenta
        if user_id != requesting_user_id:
            raise ValueError("No tienes permisos para eliminar este usuario")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Eliminar usuario físicamente
        await self.user_model.delete(user_id)
        
        return user_id
    
    async def execute_by_admin_soft(self, user_id: str) -> User:
        """
        Ejecuta un soft delete como administrador.
        
        Args:
            user_id: ID del usuario a desactivar
            
        Returns:
            Entidad User desactivada
            
        Raises:
            ValueError: Si el usuario no existe
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if not user.is_active:
            raise ValueError("Usuario ya está inactivo")
        
        # Desactivar usuario
        user.deactivate()
        
        # Guardar cambios
        updated_user = await self.user_model.update(user)
        
        return updated_user
    
    async def execute_by_admin_hard(self, user_id: str) -> str:
        """
        Ejecuta un hard delete como administrador.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            ID del usuario eliminado
            
        Raises:
            ValueError: Si el usuario no existe
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        # Buscar usuario existente para validar que existe
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Eliminar usuario físicamente
        await self.user_model.delete(user_id)
        
        return user_id
    
    async def reactivate_user(
        self,
        user_id: str,
        requesting_user_id: str
    ) -> User:
        """
        Reactiva un usuario desactivado.
        
        Args:
            user_id: ID del usuario a reactivar
            requesting_user_id: ID del usuario que hace la petición
            
        Returns:
            Entidad User reactivada
            
        Raises:
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        # Verificar permisos
        if user_id != requesting_user_id:
            raise ValueError("No tienes permisos para reactivar este usuario")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if user.is_active:
            raise ValueError("Usuario ya está activo")
        
        # Reactivar usuario
        user.activate()
        
        # Guardar cambios
        updated_user = await self.user_model.update(user)
        
        return updated_user

# Instancia del caso de uso
delete_user_use_case = DeleteUserUseCase()
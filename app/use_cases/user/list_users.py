"""
Caso de uso: Listar Usuarios.
Encapsula la lógica de negocio para obtener una lista paginada de usuarios.
"""
from typing import List, Tuple
from app.domain.user.user_entity import User
from app.infrastructure.db.user_model import user_model

class ListUsersUseCase:
    """
    Caso de uso para listar usuarios con paginación.
    Incluye validaciones y lógica de permisos.
    """
    
    def __init__(self):
        self.user_model = user_model
    
    async def execute(
        self, 
        requesting_user_id: str,
        skip: int = 0, 
        limit: int = 20
    ) -> Tuple[List[User], int]:
        """
        Ejecuta el caso de uso de listar usuarios.
        
        Args:
            requesting_user_id: ID del usuario que hace la petición
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Tupla con (lista_usuarios, total_usuarios)
            
        Raises:
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        if skip < 0:
            raise ValueError("Skip debe ser mayor o igual a 0")
        
        if limit < 1 or limit > 100:
            raise ValueError("Limit debe estar entre 1 y 100")
        
        # Verificar que el usuario solicitante existe y está activo
        requesting_user = await self.user_model.get_by_id(requesting_user_id)
        if not requesting_user or not requesting_user.is_active:
            raise ValueError("Usuario no autorizado")
        
        # Por ahora, cualquier usuario autenticado puede listar usuarios
        # En una implementación más compleja, esto podría estar restringido a admins
        
        # Obtener usuarios
        users = await self.user_model.get_all(skip=skip, limit=limit)
        
        # Filtrar solo usuarios activos (para usuarios normales)
        # En una implementación con roles, los admins podrían ver todos
        active_users = [user for user in users if user.is_active]
        
        # Obtener total de usuarios activos
        total_users = await self._count_active_users()
        
        return active_users, total_users
    
    async def execute_by_admin(
        self, 
        skip: int = 0, 
        limit: int = 20,
        include_inactive: bool = False
    ) -> Tuple[List[User], int]:
        """
        Ejecuta el caso de uso como administrador (sin restricciones).
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            include_inactive: Si incluir usuarios inactivos
            
        Returns:
            Tupla con (lista_usuarios, total_usuarios)
        """
        if skip < 0:
            raise ValueError("Skip debe ser mayor o igual a 0")
        
        if limit < 1 or limit > 100:
            raise ValueError("Limit debe estar entre 1 y 100")
        
        # Obtener todos los usuarios
        all_users = await self.user_model.get_all(skip=skip, limit=limit)
        
        if include_inactive:
            users = all_users
            total = await self.user_model.count()
        else:
            users = [user for user in all_users if user.is_active]
            total = await self._count_active_users()
        
        return users, total
    
    async def _count_active_users(self) -> int:
        """
        Cuenta el número de usuarios activos.
        
        Returns:
            Número de usuarios activos
        """
        # En una implementación real con MongoDB, esto sería más eficiente
        # con una query de agregación
        all_users = await self.user_model.get_all(skip=0, limit=1000)  # Límite alto para contar
        active_count = sum(1 for user in all_users if user.is_active)
        return active_count

# Instancia del caso de uso
list_users_use_case = ListUsersUseCase()
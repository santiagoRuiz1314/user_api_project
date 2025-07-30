"""
Controller de usuarios corregido con DTOs y mappers.
Mantiene la separación de capas según Clean Architecture.
"""
from app.use_cases.user.create_user import create_user_use_case
from app.use_cases.user.login_user import login_user_use_case
from app.use_cases.user.get_user_by_id import get_user_by_id_use_case
from app.use_cases.user.list_users import list_users_use_case
from app.use_cases.user.update_user import update_user_use_case
from app.use_cases.user.delete_user import delete_user_use_case
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserQueryRequest
)
from app.application.mappers.user_mapper import user_mapper

class UserController:
    """
    Controller corregido que usa DTOs y mappers para mantener
    la separación de capas en Clean Architecture.
    """
    
    def __init__(self):
        self.create_user_use_case = create_user_use_case
        self.login_user_use_case = login_user_use_case
        self.get_user_by_id_use_case = get_user_by_id_use_case
        self.list_users_use_case = list_users_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case
        self.user_mapper = user_mapper

    async def create_user(self, request: UserCreateRequest) -> dict:
        """
        Crea un nuevo usuario.
        
        Args:
            request: Datos del usuario a crear
            
        Returns:
            Diccionario con información del usuario creado
        """
        user = await self.create_user_use_case.execute(request.email, request.password)
        return self.user_mapper.create_user_response(user)

    async def login_user(self, request: UserLoginRequest) -> dict:
        """
        Autentica un usuario y genera token JWT.
        
        Args:
            request: Credenciales de login
            
        Returns:
            Diccionario con token y datos del usuario
        """
        token, user = await self.login_user_use_case.execute(request.email, request.password)
        return self.user_mapper.create_login_response(token, user)

    async def get_user_by_id(self, user_id: str, current_user) -> dict:
        """
        Obtiene un usuario por ID.
        
        Args:
            user_id: ID del usuario a obtener
            current_user: Usuario autenticado
            
        Returns:
            Diccionario con información del usuario
        """
        print(f"🎮 CONTROLLER: get_user_by_id llamado con ID: {user_id}")
        print(f"🔐 CONTROLLER: requesting_user_id: {current_user.id}")

        user = await self.get_user_by_id_use_case.execute(user_id, current_user.id)
        print(f"✅ CONTROLLER: Usuario encontrado: {user.id} - {user.email}")
        
        # 🔧 FIX: Convertir entidad a diccionario usando mapper
        return self.user_mapper.create_user_detail_response(user)

    async def get_current_user_profile(self, current_user) -> dict:
        """
        Obtiene el perfil del usuario autenticado.
        
        Args:
            current_user: Usuario autenticado
            
        Returns:
            Diccionario con perfil del usuario
        """
        user = await self.get_user_by_id_use_case.execute_own_profile(current_user.id)
        return self.user_mapper.create_profile_response(user)

    async def list_users(self, query: UserQueryRequest, current_user) -> dict:
        """
        Lista usuarios con paginación.
        
        Args:
            query: Parámetros de consulta (skip, limit)
            current_user: Usuario autenticado que hace la petición
            
        Returns:
            Diccionario con lista de usuarios y metadatos de paginación
        """
        users, total = await self.list_users_use_case.execute(
            requesting_user_id=current_user.id,
            skip=query.skip,
            limit=query.limit
        )
        return self.user_mapper.create_list_response(users, total, query.skip, query.limit)

    async def update_user(self, user_id: str, request: UserUpdateRequest, current_user) -> dict:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            request: Datos de actualización
            current_user: Usuario autenticado que hace la petición
            
        Returns:
            Diccionario con información del usuario actualizado
        """
        user = await self.update_user_use_case.execute(
            user_id=user_id,
            requesting_user_id=current_user.id,
            new_email=request.email,
            new_password=request.password
        )
        return self.user_mapper.create_update_response(user)

    async def delete_user_soft(self, user_id: str, current_user) -> dict:
        """
        Elimina un usuario (soft delete).
        
        Args:
            user_id: ID del usuario a eliminar
            current_user: Usuario autenticado que hace la petición
            
        Returns:
            Diccionario con confirmación de eliminación
        """
        user = await self.delete_user_use_case.execute_soft_delete(user_id, current_user.id)
        return self.user_mapper.create_delete_response(user, "Usuario desactivado exitosamente")

    async def delete_user_hard(self, user_id: str, current_user) -> dict:
        """
        Elimina un usuario permanentemente (hard delete).
        
        Args:
            user_id: ID del usuario a eliminar
            current_user: Usuario autenticado que hace la petición
            
        Returns:
            Diccionario con confirmación de eliminación
        """
        deleted_id = await self.delete_user_use_case.execute_hard_delete(user_id, current_user.id)
        return {"message": "Usuario eliminado permanentemente", "deleted_id": deleted_id}

    async def reactivate_user(self, user_id: str, current_user) -> dict:
        """
        Reactiva un usuario desactivado.
        
        Args:
            user_id: ID del usuario a reactivar
            current_user: Usuario autenticado que hace la petición
            
        Returns:
            Diccionario con información del usuario reactivado
        """
        user = await self.delete_user_use_case.reactivate_user(user_id, current_user.id)
        return self.user_mapper.create_update_response(user, "Usuario reactivado exitosamente")

# Instancia global
user_controller = UserController()
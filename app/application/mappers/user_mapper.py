"""
Mappers para conversión entre entidades del dominio y DTOs.
Mantiene la separación de capas en Clean Architecture.
"""
from typing import List, Optional
from app.domain.user.user_entity import User
from app.application.dtos.user_dto import (
    UserDTO, 
    UserListDTO, 
    UserLoginDTO,
    OperationResultDTO
)
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserUpdateRequest
)

class UserMapper:
    """
    Mapper para convertir entre entidades User y DTOs.
    Centraliza la lógica de conversión y mantiene consistencia.
    """
    
    @staticmethod
    def entity_to_dto(user: User) -> UserDTO:
        """
        Convierte una entidad User del dominio a UserDTO.
        
        Args:
            user: Entidad User del dominio
            
        Returns:
            UserDTO serializable
        """
        if not user:
            return None
            
        return UserDTO(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    @staticmethod
    def entities_to_dto_list(users: List[User]) -> List[UserDTO]:
        """
        Convierte una lista de entidades User a lista de UserDTO.
        
        Args:
            users: Lista de entidades User
            
        Returns:
            Lista de UserDTO
        """
        if not users:
            return []
            
        return [UserMapper.entity_to_dto(user) for user in users if user]
    
    @staticmethod
    def dto_to_dict(user_dto: UserDTO) -> dict:
        """
        Convierte UserDTO a diccionario para respuestas de API.
        
        Args:
            user_dto: DTO del usuario
            
        Returns:
            Diccionario serializable para FastAPI
        """
        if not user_dto:
            return None
            
        return {
            "id": user_dto.id,
            "email": user_dto.email,
            "is_active": user_dto.is_active,
            "created_at": user_dto.created_at.isoformat(),
            "updated_at": user_dto.updated_at.isoformat()
        }
    
    @staticmethod
    def create_user_response(user: User, message: str = "Usuario creado exitosamente") -> dict:
        """
        Crea respuesta para creación de usuario.
        
        Args:
            user: Entidad User creada
            message: Mensaje de éxito
            
        Returns:
            Diccionario de respuesta
        """
        if not user:
            return {"user": None, "message": "Error al crear usuario"}
            
        user_dto = UserMapper.entity_to_dto(user)
        return {
            "user": UserMapper.dto_to_dict(user_dto),
            "message": message
        }
    
    @staticmethod
    def create_user_detail_response(user: User, message: str = "Usuario obtenido exitosamente") -> dict:
        """
        Crea respuesta para obtener detalles de usuario.
        
        Args:
            user: Entidad User
            message: Mensaje de éxito
            
        Returns:
            Diccionario de respuesta
        """
        if not user:
            return {"user": None, "message": "Usuario no encontrado"}
            
        user_dto = UserMapper.entity_to_dto(user)
        return {
            "user": UserMapper.dto_to_dict(user_dto),
            "message": message
        }
    
    @staticmethod
    def create_profile_response(user: User) -> dict:
        """
        Crea respuesta para perfil de usuario.
        
        Args:
            user: Entidad User
            
        Returns:
            Diccionario de respuesta
        """
        if not user:
            return {"user": None, "message": "Perfil no encontrado"}
            
        user_dto = UserMapper.entity_to_dto(user)
        return {
            "user": UserMapper.dto_to_dict(user_dto),
            "message": "Perfil obtenido exitosamente"
        }
    
    @staticmethod
    def create_list_response(users: List[User], total: int, skip: int, limit: int) -> dict:
        """
        Crea respuesta para listado de usuarios.
        
        Args:
            users: Lista de entidades User
            total: Total de usuarios
            skip: Registros saltados
            limit: Límite de registros
            
        Returns:
            Diccionario de respuesta
        """
        user_dtos = UserMapper.entities_to_dto_list(users)
        users_dict = [UserMapper.dto_to_dict(dto) for dto in user_dtos]
        has_more = skip + len(users) < total
        
        return {
            "users": users_dict,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }
    
    @staticmethod
    def create_update_response(user: User, message: str = "Usuario actualizado exitosamente") -> dict:
        """
        Crea respuesta para actualización de usuario.
        
        Args:
            user: Entidad User actualizada
            message: Mensaje de éxito
            
        Returns:
            Diccionario de respuesta
        """
        if not user:
            return {"user": None, "message": "Error al actualizar usuario"}
            
        user_dto = UserMapper.entity_to_dto(user)
        return {
            "user": UserMapper.dto_to_dict(user_dto),
            "message": message
        }
    
    @staticmethod
    def create_delete_response(user: User, message: str = "Usuario eliminado exitosamente") -> dict:
        """
        Crea respuesta para eliminación de usuario.
        
        Args:
            user: Entidad User eliminada
            message: Mensaje de éxito
            
        Returns:
            Diccionario de respuesta
        """
        if not user:
            return {"message": "Error al eliminar usuario", "deleted_id": None}
            
        return {
            "message": message,
            "deleted_id": user.id
        }
    
    @staticmethod
    def create_login_response(token: str, user: User) -> dict:
        """
        Crea respuesta para login con token.
        
        Args:
            token: Token JWT
            user: Entidad User autenticada
            
        Returns:
            Diccionario de respuesta completa
        """
        if not user or not token:
            return {"error": "Error en autenticación"}
            
        from app.core.security import create_token_response_data
        token_data = create_token_response_data(token, user)
        user_dto = UserMapper.entity_to_dto(user)
        
        return {
            **token_data,
            "user": UserMapper.dto_to_dict(user_dto)
        }

# Instancia global del mapper
user_mapper = UserMapper()
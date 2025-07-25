"""
Modelo de User para la capa de infraestructura.
Abstrae las operaciones de base de datos para la entidad User.
"""
from typing import List, Optional
from app.domain.user.user_entity import User
from app.infrastructure.db.mongo_client import mongo_client
from app.core.exceptions import (
    InfrastructureException,
    ConflictException,
    NotFoundException
)
import logging

logger = logging.getLogger(__name__)

class UserModel:
    """
    Modelo que encapsula las operaciones de base de datos para User.
    Actúa como repositorio para la entidad User.
    """
    
    def __init__(self):
        self.db = mongo_client
    
    async def create(self, user: User) -> User:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            user: Entidad User a crear
            
        Returns:
            Entidad User creada
            
        Raises:
            ConflictException: Si el usuario ya existe
            InfrastructureException: Si hay error de infraestructura
        """
        try:
            # Verificar si el email ya existe
            existing_user = await self.db.get_user_by_email(user.email)
            if existing_user:
                raise ConflictException(f"Usuario con email {user.email} ya existe", "User")
            
            # Crear usuario
            success = await self.db.create_user(user)
            if not success:
                raise InfrastructureException("Error al crear usuario", "database")
            
            logger.info(f"✅ Usuario creado exitosamente: {user.email}")
            return user
            
        except ConflictException:
            # Re-lanzar excepciones de conflicto
            raise
        except ValueError as e:
            # Convertir ValueError de la DB a ConflictException
            if "ya existe" in str(e):
                raise ConflictException(str(e), "User")
            raise InfrastructureException(str(e), "database")
        except Exception as e:
            logger.error(f"❌ Error al crear usuario: {e}")
            raise InfrastructureException(f"Error al crear usuario: {str(e)}", "database")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        try:
            return await self.db.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"❌ Error al obtener usuario por ID {user_id}: {e}")
            raise InfrastructureException(f"Error al obtener usuario: {str(e)}", "database")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        try:
            return await self.db.get_user_by_email(email)
        except Exception as e:
            logger.error(f"❌ Error al obtener usuario por email {email}: {e}")
            raise InfrastructureException(f"Error al obtener usuario: {str(e)}", "database")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtiene todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Lista de entidades User
        """
        try:
            return await self.db.get_all_users(skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"❌ Error al obtener usuarios: {e}")
            raise InfrastructureException(f"Error al obtener usuarios: {str(e)}", "database")
    
    async def update(self, user: User) -> User:
        """
        Actualiza un usuario existente.
        
        Args:
            user: Entidad User con datos actualizados
            
        Returns:
            Entidad User actualizada
            
        Raises:
            NotFoundException: Si el usuario no existe
            InfrastructureException: Si hay error de infraestructura
        """
        try:
            success = await self.db.update_user(user)
            if not success:
                raise NotFoundException("Usuario", user.id)
            
            logger.info(f"✅ Usuario actualizado exitosamente: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Error al actualizar usuario {user.id}: {e}")
            raise InfrastructureException(f"Error al actualizar usuario: {str(e)}", "database")
    
    async def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            NotFoundException: Si el usuario no existe
            InfrastructureException: Si hay error de infraestructura
        """
        try:
            success = await self.db.delete_user(user_id)
            if not success:
                raise NotFoundException("Usuario", user_id)
            
            logger.info(f"✅ Usuario eliminado exitosamente: {user_id}")
            return True
            
        except NotFoundException:
            # Re-lanzar excepciones de not found
            raise
        except Exception as e:
            logger.error(f"❌ Error al eliminar usuario {user_id}: {e}")
            raise InfrastructureException(f"Error al eliminar usuario: {str(e)}", "database")
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        try:
            user = await self.db.get_user_by_email(email)
            return user is not None
        except Exception as e:
            logger.error(f"❌ Error al verificar existencia de email {email}: {e}")
            # En caso de error, asumir que no existe para no bloquear operaciones
            return False
    
    async def count(self) -> int:
        """
        Cuenta el total de usuarios.
        
        Returns:
            Número total de usuarios
        """
        try:
            return await self.db.count_users()
        except Exception as e:
            logger.error(f"❌ Error al contar usuarios: {e}")
            raise InfrastructureException(f"Error al contar usuarios: {str(e)}", "database")
    
    async def count_active(self) -> int:
        """
        Cuenta el total de usuarios activos.
        
        Returns:
            Número total de usuarios activos
        """
        try:
            return await self.db.count_active_users()
        except Exception as e:
            logger.error(f"❌ Error al contar usuarios activos: {e}")
            raise InfrastructureException(f"Error al contar usuarios activos: {str(e)}", "database")

# Instancia global del modelo
user_model = UserModel()
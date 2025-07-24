"""
Modelo de User para la capa de infraestructura.
Abstrae las operaciones de base de datos para la entidad User.
"""
from typing import List, Optional
from app.domain.user.user_entity import User
from app.infrastructure.db.mongo_client import mongo_client

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
            ValueError: Si el usuario ya existe
        """
        # Verificar si el email ya existe
        existing_user = self.db.get_user_by_email(user.email)
        if existing_user:
            raise ValueError(f"Usuario con email {user.email} ya existe")
        
        # Crear usuario
        success = self.db.create_user(user)
        if not success:
            raise RuntimeError("Error al crear usuario")
        
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        return self.db.get_user_by_id(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        return self.db.get_user_by_email(email)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtiene todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Lista de entidades User
        """
        return self.db.get_all_users(skip=skip, limit=limit)
    
    async def update(self, user: User) -> User:
        """
        Actualiza un usuario existente.
        
        Args:
            user: Entidad User con datos actualizados
            
        Returns:
            Entidad User actualizada
            
        Raises:
            ValueError: Si el usuario no existe
        """
        success = self.db.update_user(user)
        if not success:
            raise ValueError(f"Usuario con ID {user.id} no encontrado")
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
            
        Raises:
            ValueError: Si el usuario no existe
        """
        success = self.db.delete_user(user_id)
        if not success:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        return True
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        user = self.db.get_user_by_email(email)
        return user is not None
    
    async def count(self) -> int:
        """
        Cuenta el total de usuarios.
        
        Returns:
            Número total de usuarios
        """
        return self.db.count_users()

# Instancia global del modelo
user_model = UserModel()
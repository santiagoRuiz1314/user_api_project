"""
Cliente Mock de MongoDB para desarrollo.
Simula operaciones de base de datos en memoria hasta implementar MongoDB real.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.domain.user.user_entity import User

class MockMongoClient:
    """
    Cliente mock que simula operaciones de MongoDB en memoria.
    Será reemplazado por el cliente real de MongoDB posteriormente.
    """
    
    def __init__(self):
        # Almacenamiento en memoria
        self._users_collection: Dict[str, dict] = {}
        self._connected = False
    
    def connect(self) -> bool:
        """Simula conexión a la base de datos."""
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        """Simula desconexión de la base de datos."""
        self._connected = False
    
    def is_connected(self) -> bool:
        """Verifica si está conectado."""
        return self._connected
    
    # Operaciones de usuarios
    def create_user(self, user: User) -> bool:
        """
        Crea un nuevo usuario en la colección.
        
        Args:
            user: Entidad User a crear
            
        Returns:
            True si se creó exitosamente
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        if user.id in self._users_collection:
            return False  # Usuario ya existe
        
        self._users_collection[user.id] = user.to_dict()
        return True
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        user_data = self._users_collection.get(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        email = email.lower().strip()
        for user_data in self._users_collection.values():
            if user_data["email"] == email:
                return User.from_dict(user_data)
        return None
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtiene todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Lista de entidades User
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        users_data = list(self._users_collection.values())
        paginated_data = users_data[skip:skip + limit]
        
        return [User.from_dict(data) for data in paginated_data]
    
    def update_user(self, user: User) -> bool:
        """
        Actualiza un usuario existente.
        
        Args:
            user: Entidad User con datos actualizados
            
        Returns:
            True si se actualizó exitosamente
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        if user.id not in self._users_collection:
            return False  # Usuario no existe
        
        user.updated_at = datetime.utcnow()
        self._users_collection[user.id] = user.to_dict()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario (hard delete).
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        if user_id not in self._users_collection:
            return False  # Usuario no existe
        
        del self._users_collection[user_id]
        return True
    
    def count_users(self) -> int:
        """
        Cuenta el total de usuarios.
        
        Returns:
            Número total de usuarios
        """
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        return len(self._users_collection)
    
    def clear_all_users(self) -> None:
        """Limpia todos los usuarios (útil para testing)."""
        if not self._connected:
            raise ConnectionError("Database not connected")
        
        self._users_collection.clear()

# Instancia global del cliente mock
mongo_client = MockMongoClient()
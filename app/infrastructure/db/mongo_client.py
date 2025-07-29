"""
Cliente real de MongoDB usando Motor (driver asíncrono).
Reemplaza el cliente mock con una implementación real de MongoDB.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from app.domain.user.user_entity import User
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoClient:
    """
    Cliente real de MongoDB para operaciones asíncronas.
    Maneja conexiones y operaciones CRUD con la base de datos.
    """
    
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._users_collection: Optional[AsyncIOMotorCollection] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """
        Establece conexión con MongoDB.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Crear cliente de MongoDB
            self._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000  # 5 segundos timeout
            )
            
            # Verificar conexión
            await self._client.admin.command('ping')
            
            # Configurar base de datos y colecciones
            self._database = self._client[settings.DATABASE_NAME]
            self._users_collection = self._database[settings.USERS_COLLECTION]
            
            # Crear índices
            await self._create_indexes()
            
            self._connected = True
            logger.info("✅ Conectado exitosamente a MongoDB")
            return True
            
        except ServerSelectionTimeoutError:
            logger.error("❌ No se pudo conectar a MongoDB: Timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Error al conectar a MongoDB: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Cierra la conexión con MongoDB."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("🔌 Desconectado de MongoDB")
    
    def is_connected(self) -> bool:
        """Verifica si está conectado a MongoDB."""
        return self._connected and self._client is not None
    
    async def _create_indexes(self) -> None:
        """Crea índices necesarios en las colecciones."""
        try:
            # Índice único en email
            await self._users_collection.create_index("email", unique=True)
            # Índice en is_active para consultas eficientes
            await self._users_collection.create_index("is_active")
            logger.info("✅ Índices creados exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear índices: {e}")
    
    # Operaciones de usuarios
    async def create_user(self, user: User) -> bool:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            user: Entidad User a crear
            
        Returns:
            True si se creó exitosamente
            
        Raises:
            ConnectionError: Si no está conectado
            ValueError: Si el usuario ya existe
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            user_doc = user.to_dict()
            await self._users_collection.insert_one(user_doc)
            logger.info(f"✅ Usuario creado: {user.email}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ Usuario ya existe: {user.email}")
            raise ValueError(f"Usuario con email {user.email} ya existe")
        except Exception as e:
            logger.error(f"❌ Error al crear usuario: {e}")
            raise RuntimeError(f"Error al crear usuario: {e}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID con debug detallado.
        """
        if not self.is_connected():
            logger.error("❌ Base de datos no conectada")
            raise ConnectionError("Database not connected")
        
        try:
            # 🔍 DEBUG DETALLADO
            logger.info(f"🔍 === DEBUG GET_USER_BY_ID ===")
            logger.info(f"📝 ID recibido: '{user_id}'")
            logger.info(f"📏 Longitud: {len(user_id)}")
            logger.info(f"🔤 Tipo: {type(user_id)}")
            
            # Verificar conexión a la colección
            logger.info(f"📊 Colección: {self._users_collection.name}")
            
            # Contar documentos totales
            total_docs = await self._users_collection.count_documents({})
            logger.info(f"📈 Total documentos en colección: {total_docs}")
            
            # Intentar encontrar cualquier documento con ese ID
            logger.info(f"🔍 Ejecutando query: find_one({{'id': '{user_id}'}})")
            user_doc = await self._users_collection.find_one({"id": user_id})
            
            if user_doc:
                logger.info(f"✅ ¡USUARIO ENCONTRADO!")
                logger.info(f"📧 Email: {user_doc.get('email')}")
                logger.info(f"🆔 ID en documento: '{user_doc.get('id')}'")
                logger.info(f"✳️ is_active: {user_doc.get('is_active')}")
                
                # Remover el _id de MongoDB antes de crear la entidad
                user_doc.pop('_id', None)
                user_entity = User.from_dict(user_doc)
                logger.info(f"🏗️ Entidad User creada exitosamente")
                return user_entity
            else:
                logger.error(f"❌ NO SE ENCONTRÓ usuario con ID: '{user_id}'")
                
                # DEBUG: Buscar documentos similares
                logger.info(f"🔍 Buscando IDs similares...")
                similar_docs = await self._users_collection.find(
                    {"id": {"$regex": user_id[:10]}}, 
                    {"id": 1, "email": 1}
                ).limit(5).to_list(length=5)
                
                if similar_docs:
                    logger.info(f"📋 IDs similares encontrados:")
                    for doc in similar_docs:
                        logger.info(f"  - {doc.get('id')} | {doc.get('email')}")
                else:
                    logger.info(f"🚫 No se encontraron IDs similares")
                
                # DEBUG: Mostrar algunos documentos de ejemplo
                sample_docs = await self._users_collection.find(
                    {}, {"id": 1, "email": 1}
                ).limit(3).to_list(length=3)
                
                if sample_docs:
                    logger.info(f"📋 Documentos de ejemplo en la colección:")
                    for doc in sample_docs:
                        logger.info(f"  - {doc.get('id')} | {doc.get('email')}")
                
                return None
            
        except Exception as e:
            logger.error(f"💥 EXCEPCIÓN en get_user_by_id: {e}")
            logger.error(f"🔍 Tipo de excepción: {type(e)}")
            import traceback
            logger.error(f"📚 Traceback: {traceback.format_exc()}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            email = email.lower().strip()
            user_doc = await self._users_collection.find_one({"email": email})
            if user_doc:
                # Remover el _id de MongoDB antes de crear la entidad
                user_doc.pop('_id', None)
                return User.from_dict(user_doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error al obtener usuario por email {email}: {e}")
            return None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtiene todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            
        Returns:
            Lista de entidades User
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            cursor = self._users_collection.find({}).skip(skip).limit(limit)
            users = []
            
            async for user_doc in cursor:
                # Remover el _id de MongoDB antes de crear la entidad
                user_doc.pop('_id', None)
                users.append(User.from_dict(user_doc))
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Error al obtener usuarios: {e}")
            return []
    
    async def update_user(self, user: User) -> bool:
        """
        Actualiza un usuario existente.
        
        Args:
            user: Entidad User con datos actualizados
            
        Returns:
            True si se actualizó exitosamente
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            user.updated_at = datetime.utcnow()
            user_doc = user.to_dict()
            
            result = await self._users_collection.replace_one(
                {"id": user.id},
                user_doc
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Usuario actualizado: {user.email}")
                return True
            else:
                logger.warning(f"⚠️ Usuario no encontrado para actualizar: {user.id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al actualizar usuario {user.id}: {e}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario (hard delete).
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            result = await self._users_collection.delete_one({"id": user_id})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Usuario eliminado: {user_id}")
                return True
            else:
                logger.warning(f"⚠️ Usuario no encontrado para eliminar: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al eliminar usuario {user_id}: {e}")
            return False
    
    async def count_users(self) -> int:
        """
        Cuenta el total de usuarios.
        
        Returns:
            Número total de usuarios
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            count = await self._users_collection.count_documents({})
            return count
            
        except Exception as e:
            logger.error(f"❌ Error al contar usuarios: {e}")
            return 0
    
    async def count_active_users(self) -> int:
        """
        Cuenta el total de usuarios activos.
        
        Returns:
            Número total de usuarios activos
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        try:
            count = await self._users_collection.count_documents({"is_active": True})
            return count
            
        except Exception as e:
            logger.error(f"❌ Error al contar usuarios activos: {e}")
            return 0
    
    async def clear_all_users(self) -> None:
        """
        Limpia todos los usuarios (útil para testing).
        ⚠️ USAR SOLO EN DESARROLLO/TESTING
        """
        if not self.is_connected():
            raise ConnectionError("Database not connected")
        
        if settings.ENVIRONMENT == "production":
            raise RuntimeError("No se puede limpiar usuarios en producción")
        
        try:
            await self._users_collection.delete_many({})
            logger.warning("🗑️ Todos los usuarios han sido eliminados")
            
        except Exception as e:
            logger.error(f"❌ Error al limpiar usuarios: {e}")

# Instancia global del cliente MongoDB
mongo_client = MongoClient()
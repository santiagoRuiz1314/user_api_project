"""
Caso de uso: Obtener Usuario por ID - VERSIÓN CORREGIDA.
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
import logging

logger = logging.getLogger(__name__)

class GetUserByIdUseCase:
    """
    Caso de uso para obtener un usuario por su ID.
    Incluye validaciones de negocio y permisos apropiados.
    VERSIÓN MEJORADA con mejor manejo de errores.
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
            AuthorizationException: Si no tiene permisos
        """
        logger.info(f"🎯 USE CASE: execute llamado con user_id: {user_id}")
        logger.info(f"🎯 USE CASE: requesting_user_id: {requesting_user_id}")

        try:
            # 🔧 SANITIZAR EL USER_ID
            user_id = self._sanitize_user_id(user_id)
            logger.info(f"🧹 USE CASE: user_id sanitizado: {user_id}")

            # Validaciones básicas
            self._validate_input(user_id, requesting_user_id)
            logger.info(f"✅ USE CASE: Validaciones básicas pasadas")
            
            # Verificar que el usuario solicitante existe y está activo
            requesting_user = await self._validate_requesting_user(requesting_user_id)
            logger.info(f"✅ USE CASE: Usuario solicitante válido")
            
            # Buscar el usuario solicitado
            user = await self._get_target_user(user_id)
            logger.info(f"✅ USE CASE: Usuario encontrado y activo, retornando")
            
            return user
            
        except (ValidationException, UserNotFoundException, UserInactiveException, AuthorizationException) as e:
            # Re-lanzar excepciones de dominio
            logger.warning(f"⚠️ USE CASE: Excepción de dominio: {e}")
            raise
        except Exception as e:
            # Capturar cualquier otra excepción y convertirla
            logger.error(f"❌ USE CASE: Error inesperado: {e}")
            raise ValidationException(f"Error interno al obtener usuario: {str(e)}")
    
    def _sanitize_user_id(self, user_id: str) -> str:
        """
        Sanitiza el user_id recibido.
        
        Args:
            user_id: ID sin sanitizar
            
        Returns:
            ID sanitizado
        """
        if not user_id:
            return user_id
            
        import urllib.parse
        # Decodificar URL
        sanitized = urllib.parse.unquote(user_id)
        # Remover comillas
        sanitized = sanitized.strip("\"'")
        # Remover espacios
        sanitized = sanitized.strip()
        
        return sanitized
    
    def _validate_input(self, user_id: str, requesting_user_id: str) -> None:
        """
        Valida los parámetros de entrada.
        
        Args:
            user_id: ID del usuario a obtener
            requesting_user_id: ID del usuario solicitante
            
        Raises:
            ValidationException: Si hay errores de validación
        """
        if not user_id or not user_id.strip():
            logger.error(f"❌ USE CASE: user_id vacío")
            raise ValidationException("User ID es requerido", "user_id")
        
        if not requesting_user_id or not requesting_user_id.strip():
            logger.error(f"❌ USE CASE: requesting_user_id vacío")
            raise ValidationException("Requesting user ID es requerido", "requesting_user_id")
    
    async def _validate_requesting_user(self, requesting_user_id: str) -> User:
        """
        Valida que el usuario solicitante existe y está activo.
        
        Args:
            requesting_user_id: ID del usuario solicitante
            
        Returns:
            Entidad User del solicitante
            
        Raises:
            AuthorizationException: Si el usuario no existe
            UserInactiveException: Si el usuario está inactivo
        """
        logger.info(f"🔍 USE CASE: Verificando usuario solicitante: {requesting_user_id}")
        
        requesting_user = await self.user_model.get_by_id(requesting_user_id)
        if not requesting_user:
            logger.error(f"❌ USE CASE: Usuario solicitante no encontrado")
            raise AuthorizationException("Usuario solicitante no encontrado")
        
        if not requesting_user.is_active:
            logger.error(f"❌ USE CASE: Usuario solicitante inactivo")
            raise UserInactiveException(requesting_user_id)
        
        return requesting_user
    
    async def _get_target_user(self, user_id: str) -> User:
        """
        Obtiene el usuario objetivo y valida que esté activo.
        
        Args:
            user_id: ID del usuario objetivo
            
        Returns:
            Entidad User del usuario objetivo
            
        Raises:
            UserNotFoundException: Si el usuario no existe o está inactivo
        """
        logger.info(f"🔍 USE CASE: Llamando a user_model.get_by_id({user_id})")
        
        user = await self.user_model.get_by_id(user_id)
        logger.info(f"🔍 USE CASE: user_model.get_by_id() retornó: {user}")
        
        if not user:
            logger.error(f"❌ USE CASE: Usuario no encontrado en base de datos")
            raise UserNotFoundException(user_id)
        
        # Verificar que el usuario solicitado esté activo
        if not user.is_active:
            logger.error(f"❌ USE CASE: Usuario encontrado pero inactivo")
            # Por seguridad, no revelamos que existe pero está inactivo
            raise UserNotFoundException(user_id)
        
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
        logger.info(f"🔍 USE CASE: execute_own_profile para user_id: {user_id}")
        
        try:
            user_id = self._sanitize_user_id(user_id)
            
            if not user_id or not user_id.strip():
                raise ValidationException("User ID es requerido", "user_id")
            
            user = await self.user_model.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)
            
            if not user.is_active:
                raise UserInactiveException(user_id)
            
            logger.info(f"✅ USE CASE: Perfil propio obtenido exitosamente")
            return user
            
        except (ValidationException, UserNotFoundException, UserInactiveException) as e:
            logger.warning(f"⚠️ USE CASE: Excepción en execute_own_profile: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ USE CASE: Error inesperado en execute_own_profile: {e}")
            raise ValidationException(f"Error interno al obtener perfil: {str(e)}")
    
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
        logger.info(f"🔍 USE CASE: execute_by_admin para user_id: {user_id}")
        
        try:
            user_id = self._sanitize_user_id(user_id)
            
            if not user_id or not user_id.strip():
                raise ValidationException("User ID es requerido", "user_id")
            
            user = await self.user_model.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)
            
            logger.info(f"✅ USE CASE: Usuario obtenido por admin exitosamente")
            return user
            
        except (ValidationException, UserNotFoundException) as e:
            logger.warning(f"⚠️ USE CASE: Excepción en execute_by_admin: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ USE CASE: Error inesperado en execute_by_admin: {e}")
            raise ValidationException(f"Error interno al obtener usuario: {str(e)}")

# Instancia del caso de uso
get_user_by_id_use_case = GetUserByIdUseCase()
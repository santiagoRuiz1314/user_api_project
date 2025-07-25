"""
Caso de uso: Actualizar Usuario.
Encapsula la lógica de negocio para actualizar información de usuario.
"""
from typing import Optional
from app.domain.user.user_entity import User
from app.infrastructure.auth.password_hashing import password_hasher
from app.infrastructure.db.user_model import user_model
from app.core.utils import validation_utils

class UpdateUserUseCase:
    """
    Caso de uso para actualizar un usuario existente.
    Maneja validaciones, permisos y lógica de negocio.
    """
    
    def __init__(self):
        self.user_model = user_model
        self.password_hasher = password_hasher
        self.validation_utils = validation_utils
    
    async def execute(
        self,
        user_id: str,
        requesting_user_id: str,
        new_email: Optional[str] = None,
        new_password: Optional[str] = None
    ) -> User:
        """
        Ejecuta el caso de uso de actualización de usuario.
        
        Args:
            user_id: ID del usuario a actualizar
            requesting_user_id: ID del usuario que hace la petición
            new_email: Nuevo email (opcional)
            new_password: Nueva contraseña (opcional)
            
        Returns:
            Entidad User actualizada
            
        Raises:
            ValueError: Si hay errores de validación o permisos
        """
        # Validaciones básicas
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        if not requesting_user_id or not requesting_user_id.strip():
            raise ValueError("Requesting user ID es requerido")
        
        # Verificar que hay algo que actualizar
        if not new_email and not new_password:
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        
        # Verificar permisos: un usuario solo puede actualizar su propia información
        if user_id != requesting_user_id:
            raise ValueError("No tienes permisos para actualizar este usuario")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if not user.is_active:
            raise ValueError("Usuario inactivo")
        
        # Validar y actualizar email si se proporciona
        if new_email:
            await self._update_user_email(user, new_email)
        
        # Validar y actualizar contraseña si se proporciona
        if new_password:
            await self._update_user_password(user, new_password)
        
        # Guardar cambios
        updated_user = await self.user_model.update(user)
        
        return updated_user
    
    async def _update_user_email(self, user: User, new_email: str):
        """
        Actualiza el email del usuario con validaciones.
        
        Args:
            user: Entidad User a actualizar
            new_email: Nuevo email
            
        Raises:
            ValueError: Si el email es inválido o ya está en uso
        """
        # Validar formato del email
        if not self.validation_utils.is_valid_email(new_email):
            raise ValueError("El formato del email es inválido")
        
        new_email = new_email.lower().strip()
        
        # Verificar que el email no esté en uso por otro usuario
        existing_user = await self.user_model.get_by_email(new_email)
        if existing_user and existing_user.id != user.id:
            raise ValueError(f"El email {new_email} ya está en uso por otro usuario")
        
        # Actualizar email en la entidad
        user.update_email(new_email)
    
    async def _update_user_password(self, user: User, new_password: str):
        """
        Actualiza la contraseña del usuario con validaciones.
        
        Args:
            user: Entidad User a actualizar
            new_password: Nueva contraseña
            
        Raises:
            ValueError: Si la contraseña no cumple los requisitos
        """
        # Validar contraseña
        if not self.validation_utils.is_valid_password(new_password):
            raise ValueError("La contraseña debe tener entre 6 y 128 caracteres")
        
        # Generar nuevo hash
        new_password_hash = self.password_hasher.hash_password(new_password)
        
        # Actualizar contraseña en la entidad
        user.update_password_hash(new_password_hash)
    
    async def execute_by_admin(
        self,
        user_id: str,
        new_email: Optional[str] = None,
        new_password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> User:
        """
        Ejecuta el caso de uso como administrador (sin restricciones de permisos).
        
        Args:
            user_id: ID del usuario a actualizar
            new_email: Nuevo email (opcional)
            new_password: Nueva contraseña (opcional)
            is_active: Nuevo estado activo (opcional)
            
        Returns:
            Entidad User actualizada
            
        Raises:
            ValueError: Si hay errores de validación
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID es requerido")
        
        # Verificar que hay algo que actualizar
        if not new_email and not new_password and is_active is None:
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        
        # Buscar usuario existente
        user = await self.user_model.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar email si se proporciona
        if new_email:
            await self._update_user_email(user, new_email)
        
        # Actualizar contraseña si se proporciona
        if new_password:
            await self._update_user_password(user, new_password)
        
        # Actualizar estado activo si se proporciona
        if is_active is not None:
            if is_active:
                user.activate()
            else:
                user.deactivate()
        
        # Guardar cambios
        updated_user = await self.user_model.update(user)
        
        return updated_user

# Instancia del caso de uso
update_user_use_case = UpdateUserUseCase()
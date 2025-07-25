"""
Caso de uso: Login de Usuario.
Encapsula la lógica de negocio para autenticación de usuarios.
"""
from typing import Tuple
from app.domain.user.user_entity import User
from app.infrastructure.auth.password_hashing import password_hasher
from app.infrastructure.auth.jwt_handler import jwt_handler
from app.infrastructure.db.user_model import user_model
from app.core.utils import validation_utils
from app.core.exceptions import (
    ValidationException,
    InvalidCredentialsException,
    UserInactiveException,
    UserNotFoundException
)

class LoginUserUseCase:
    """
    Caso de uso para autenticación de usuario.
    Maneja la validación de credenciales y generación de tokens.
    """
    
    def __init__(self):
        self.user_model = user_model
        self.password_hasher = password_hasher
        self.jwt_handler = jwt_handler
        self.validation_utils = validation_utils
    
    async def execute(self, email: str, password: str) -> Tuple[str, User]:
        """
        Ejecuta el caso de uso de login de usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Tupla con (token_jwt, entidad_user)
            
        Raises:
            ValidationException: Si los datos de entrada son inválidos
            InvalidCredentialsException: Si las credenciales son incorrectas
            UserInactiveException: Si el usuario está inactivo
        """
        # Validaciones de entrada
        if not email or not email.strip():
            raise ValidationException("Email es requerido", "email")
        
        if not password or not password.strip():
            raise ValidationException("Contraseña es requerida", "password")
        
        # Validar formato del email
        if not self.validation_utils.is_valid_email(email):
            raise ValidationException("Formato de email inválido", "email")
        
        email = email.lower().strip()
        
        # Buscar usuario por email
        user = await self.user_model.get_by_email(email)
        if not user:
            # Por seguridad, no revelamos si el email existe o no
            raise InvalidCredentialsException()
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise UserInactiveException(user.id)
        
        # Verificar contraseña
        is_valid_password = self.password_hasher.verify_password(
            password, user.password_hash
        )
        if not is_valid_password:
            raise InvalidCredentialsException()
        
        # Generar token JWT
        access_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email
        )
        
        return access_token, user
    
    async def validate_credentials(self, email: str, password: str) -> bool:
        """
        Valida credenciales sin generar token.
        Útil para validaciones internas.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            True si las credenciales son válidas, False en caso contrario
        """
        try:
            await self.execute(email, password)
            return True
        except (InvalidCredentialsException, UserInactiveException, ValidationException):
            return False

# Instancia del caso de uso
login_user_use_case = LoginUserUseCase()
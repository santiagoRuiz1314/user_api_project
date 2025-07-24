"""
Caso de uso: Login de Usuario.
Encapsula la lógica de negocio para autenticación de usuarios.
"""
from typing import Tuple
from app.domain.user.user_entity import User
from app.infrastructure.auth.password_hashing import password_hasher
from app.infrastructure.auth.jwt_handler import jwt_handler
from app.infrastructure.db.user_model import user_model

class LoginUserUseCase:
    """
    Caso de uso para autenticación de usuario.
    Maneja la validación de credenciales y generación de tokens.
    """
    
    def __init__(self):
        self.user_model = user_model
        self.password_hasher = password_hasher
        self.jwt_handler = jwt_handler
    
    async def execute(self, email: str, password: str) -> Tuple[str, User]:
        """
        Ejecuta el caso de uso de login de usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Tupla con (token_jwt, entidad_user)
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Validaciones básicas
        if not email or not email.strip():
            raise ValueError("Email es requerido")
        
        if not password or not password.strip():
            raise ValueError("Password es requerido")
        
        email = email.lower().strip()
        
        # Buscar usuario por email
        user = await self.user_model.get_by_email(email)
        if not user:
            raise ValueError("Credenciales inválidas")
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise ValueError("Usuario inactivo")
        
        # Verificar contraseña
        is_valid_password = self.password_hasher.verify_password(
            password, user.password_hash
        )
        if not is_valid_password:
            raise ValueError("Credenciales inválidas")
        
        # Generar token JWT
        access_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email
        )
        
        return access_token, user

# Instancia del caso de uso
login_user_use_case = LoginUserUseCase()
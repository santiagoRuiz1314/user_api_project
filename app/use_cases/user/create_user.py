"""
Caso de uso: Crear Usuario.
Encapsula la lógica de negocio para registrar un nuevo usuario.
"""
from app.domain.user.user_entity import User
from app.infrastructure.auth.password_hashing import password_hasher
from app.infrastructure.db.user_model import user_model
from app.core.utils import validation_utils
from app.core.exceptions import (
    ValidationException,
    UserAlreadyExistsException,
    InfrastructureException
)

class CreateUserUseCase:
    """
    Caso de uso para crear un nuevo usuario.
    Maneja toda la lógica de negocio relacionada con el registro.
    """
    
    def __init__(self):
        self.user_model = user_model
        self.password_hasher = password_hasher
        self.validation_utils = validation_utils
    
    async def execute(self, email: str, password: str) -> User:
        """
        Ejecuta el caso de uso de creación de usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Entidad User creada
            
        Raises:
            ValidationException: Si hay errores de validación de entrada
            UserAlreadyExistsException: Si el usuario ya existe
            InfrastructureException: Si hay errores de infraestructura
        """
        # Validaciones de entrada
        await self._validate_input(email, password)
        
        email = email.lower().strip()
        
        # Verificar si el usuario ya existe
        await self._check_user_not_exists(email)
        
        # Hash de la contraseña
        password_hash = self._hash_password(password)
        
        # Crear nueva entidad User
        new_user = User.create_new_user(
            email=email,
            password_hash=password_hash
        )
        
        # Guardar en la base de datos
        try:
            created_user = await self.user_model.create(new_user)
            return created_user
        except Exception as e:
            raise InfrastructureException(
                f"Error al crear usuario: {str(e)}", 
                "database"
            )
    
    async def _validate_input(self, email: str, password: str):
        """
        Valida los datos de entrada.
        
        Args:
            email: Email a validar
            password: Contraseña a validar
            
        Raises:
            ValidationException: Si hay errores de validación
        """
        if not email or not email.strip():
            raise ValidationException("Email es requerido", "email")
        
        if not password or not password.strip():
            raise ValidationException("Contraseña es requerida", "password")
        
        # Validar formato del email
        if not self.validation_utils.is_valid_email(email):
            raise ValidationException("Formato de email inválido", "email")
        
        # Validar contraseña
        if not self.validation_utils.is_valid_password(password):
            raise ValidationException(
                "La contraseña debe tener entre 6 y 128 caracteres", 
                "password"
            )
    
    async def _check_user_not_exists(self, email: str):
        """
        Verifica que el usuario no exista.
        
        Args:
            email: Email a verificar
            
        Raises:
            UserAlreadyExistsException: Si el usuario ya existe
        """
        existing_user = await self.user_model.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException(email)
    
    def _hash_password(self, password: str) -> str:
        """
        Genera el hash de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
            
        Raises:
            InfrastructureException: Si hay error al generar el hash
        """
        try:
            return self.password_hasher.hash_password(password)
        except Exception as e:
            raise InfrastructureException(
                f"Error al procesar contraseña: {str(e)}", 
                "password_hasher"
            )
    
    async def check_email_availability(self, email: str) -> bool:
        """
        Verifica si un email está disponible.
        
        Args:
            email: Email a verificar
            
        Returns:
            True si está disponible, False si ya está en uso
        """
        if not email or not self.validation_utils.is_valid_email(email):
            return False
        
        existing_user = await self.user_model.get_by_email(email.lower().strip())
        return existing_user is None

# Instancia del caso de uso
create_user_use_case = CreateUserUseCase()
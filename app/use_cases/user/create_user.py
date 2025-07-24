"""
Caso de uso: Crear Usuario.
Encapsula la lógica de negocio para registrar un nuevo usuario.
"""
from app.domain.user.user_entity import User
from app.infrastructure.auth.password_hashing import password_hasher
from app.infrastructure.db.user_model import user_model

class CreateUserUseCase:
    """
    Caso de uso para crear un nuevo usuario.
    Maneja toda la lógica de negocio relacionada con el registro.
    """
    
    def __init__(self):
        self.user_model = user_model
        self.password_hasher = password_hasher
    
    async def execute(self, email: str, password: str) -> User:
        """
        Ejecuta el caso de uso de creación de usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Entidad User creada
            
        Raises:
            ValueError: Si hay errores de validación o el usuario ya existe
        """
        # Validaciones de negocio
        if not email or not email.strip():
            raise ValueError("Email es requerido")
        
        if not password or len(password.strip()) < 6:
            raise ValueError("Password debe tener al menos 6 caracteres")
        
        email = email.lower().strip()
        
        # Verificar si el usuario ya existe
        existing_user = await self.user_model.get_by_email(email)
        if existing_user:
            raise ValueError(f"Usuario con email {email} ya existe")
        
        # Hash de la contraseña
        password_hash = self.password_hasher.hash_password(password)
        
        # Crear nueva entidad User
        new_user = User.create_new_user(
            email=email,
            password_hash=password_hash
        )
        
        # Guardar en la base de datos
        created_user = await self.user_model.create(new_user)
        
        return created_user

# Instancia del caso de uso
create_user_use_case = CreateUserUseCase()
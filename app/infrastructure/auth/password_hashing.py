"""
Servicio de hashing y verificación de contraseñas.
Abstrae la lógica de hash de contraseñas usando bcrypt.
"""
import bcrypt

class PasswordHasher:
    """Manejador de hash y verificación de contraseñas."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña como string
        """
        if not password:
            raise ValueError("Password no puede estar vacío")
        
        # Generar salt y hash
        salt = bcrypt.gensalt()
        password_bytes = password.encode('utf-8')
        hash_bytes = bcrypt.hashpw(password_bytes, salt)
        
        return hash_bytes.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            password: Contraseña en texto plano
            hashed_password: Hash almacenado
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        if not password or not hashed_password:
            return False
        
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError):
            return False

# Instancia global del hasher
password_hasher = PasswordHasher()
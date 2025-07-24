"""
Manejador de JWT para autenticación.
Genera y valida tokens JWT.
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings

class JWTHandler:
    """Manejador de tokens JWT."""
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            user_id: ID del usuario
            email: Email del usuario
            
        Returns:
            Token JWT como string
        """
        # Tiempo de expiración
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_EXPIRATION_TIME_MINUTES
        )
        
        # Payload del token
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        # Generar token
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Payload del token si es válido, None si es inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Verificar que sea un token de acceso
            if payload.get("type") != "access":
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extrae el user_id de un token JWT válido.
        
        Args:
            token: Token JWT
            
        Returns:
            user_id si el token es válido, None en caso contrario
        """
        payload = JWTHandler.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Verifica si un token ha expirado.
        
        Args:
            token: Token JWT
            
        Returns:
            True si ha expirado, False en caso contrario
        """
        try:
            jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.InvalidTokenError:
            return True

# Instancia global del JWT handler
jwt_handler = JWTHandler()
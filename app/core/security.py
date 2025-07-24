"""
Configuración de seguridad y autenticación JWT.
Maneja la verificación de tokens y dependencias de autenticación.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.infrastructure.auth.jwt_handler import jwt_handler
from app.infrastructure.db.user_model import user_model
from app.domain.user.user_entity import User

# Esquema de seguridad Bearer Token
security = HTTPBearer()

class SecurityService:
    """Servicio de seguridad para autenticación y autorización."""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """
        Dependency para obtener el usuario actual autenticado.
        
        Args:
            credentials: Credenciales JWT del header Authorization
            
        Returns:
            Entidad User del usuario autenticado
            
        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Verificar y decodificar token
            payload = jwt_handler.verify_token(credentials.credentials)
            if payload is None:
                raise credentials_exception
            
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise credentials_exception
            
        except Exception:
            raise credentials_exception
        
        # Buscar usuario en la base de datos
        user = await user_model.get_by_id(user_id)
        if user is None:
            raise credentials_exception
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
    
    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Dependency para obtener el usuario actual activo.
        Es un wrapper adicional para mayor claridad en los endpoints.
        
        Args:
            current_user: Usuario actual obtenido del token
            
        Returns:
            Entidad User del usuario activo
            
        Raises:
            HTTPException: Si el usuario está inactivo
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    @staticmethod
    def verify_token_without_exception(token: str) -> Optional[dict]:
        """
        Verifica un token JWT sin lanzar excepciones.
        Útil para casos donde necesitamos verificar tokens opcionalmente.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Payload del token si es válido, None si es inválido
        """
        return jwt_handler.verify_token(token)
    
    @staticmethod
    async def get_user_from_token(token: str) -> Optional[User]:
        """
        Obtiene un usuario directamente desde un token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Entidad User si el token es válido y el usuario existe, None en caso contrario
        """
        payload = SecurityService.verify_token_without_exception(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = await user_model.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        return user

# Instancia global del servicio de seguridad
security_service = SecurityService()

# Función de conveniencia para dependency injection
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency function para obtener el usuario actual."""
    return await security_service.get_current_user(credentials)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency function para obtener el usuario actual activo."""
    return await security_service.get_current_active_user(current_user)

# Funciones adicionales de utilidad
def create_token_response_data(token: str, user: User) -> dict:
    """
    Crea los datos de respuesta para un token JWT.
    
    Args:
        token: Token JWT generado
        user: Entidad User
        
    Returns:
        Diccionario con datos del token y usuario
    """
    from app.core.config import settings
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_TIME_MINUTES,
        "user_id": user.id,
        "email": user.email
    }
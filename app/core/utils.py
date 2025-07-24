"""
Funciones auxiliares generales.
Funciones de utilidad que se usan en toda la aplicación.
"""
import re
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

class ValidationUtils:
    """Utilidades para validación de datos."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Valida si un email tiene formato correcto.
        
        Args:
            email: Email a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """
        Valida si una contraseña cumple los requisitos mínimos.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            True si es válida, False en caso contrario
        """
        if not password:
            return False
        
        return len(password) >= 6 and len(password) <= 128
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """
        Valida si un string es un UUID válido.
        
        Args:
            uuid_string: String a validar
            
        Returns:
            True si es un UUID válido, False en caso contrario
        """
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

class DateUtils:
    """Utilidades para manejo de fechas."""
    
    @staticmethod
    def get_current_utc() -> datetime:
        """
        Obtiene la fecha y hora actual en UTC.
        
        Returns:
            Datetime actual en UTC
        """
        return datetime.utcnow()
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Formatea un datetime a string ISO.
        
        Args:
            dt: Datetime a formatear
            
        Returns:
            String en formato ISO
        """
        return dt.isoformat()
    
    @staticmethod
    def parse_datetime(dt_string: str) -> Optional[datetime]:
        """
        Parsea un string de fecha a datetime.
        
        Args:
            dt_string: String de fecha en formato ISO
            
        Returns:
            Datetime parseado o None si es inválido
        """
        try:
            return datetime.fromisoformat(dt_string)
        except ValueError:
            return None

class ResponseUtils:
    """Utilidades para manejo de respuestas de API."""
    
    @staticmethod
    def success_response(
        message: str = "Operation successful",
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Crea una respuesta de éxito estándar.
        
        Args:
            message: Mensaje de éxito
            data: Datos adicionales (opcional)
            
        Returns:
            Diccionario con respuesta de éxito
        """
        response = {
            "success": True,
            "message": message,
            "timestamp": DateUtils.get_current_utc().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        return response
    
    @staticmethod
    def error_response(
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Crea una respuesta de error estándar.
        
        Args:
            message: Mensaje de error
            error_code: Código de error (opcional)
            details: Detalles adicionales (opcional)
            
        Returns:
            Diccionario con respuesta de error
        """
        response = {
            "success": False,
            "error": message,
            "timestamp": DateUtils.get_current_utc().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response

class StringUtils:
    """Utilidades para manejo de strings."""
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normaliza un email (lowercase y trim).
        
        Args:
            email: Email a normalizar
            
        Returns:
            Email normalizado
        """
        if not email:
            return ""
        
        return email.lower().strip()
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Genera un UUID único.
        
        Returns:
            UUID como string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 255) -> str:
        """
        Sanitiza un string eliminando caracteres no deseados.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima
            
        Returns:
            String sanitizado
        """
        if not text:
            return ""
        
        # Trim y limitar longitud
        sanitized = text.strip()[:max_length]
        
        return sanitized

class PaginationUtils:
    """Utilidades para paginación."""
    
    @staticmethod
    def validate_pagination_params(skip: int, limit: int) -> tuple[int, int]:
        """
        Valida y normaliza parámetros de paginación.
        
        Args:
            skip: Registros a saltar
            limit: Límite de registros
            
        Returns:
            Tupla con (skip, limit) validados
        """
        # Validar skip
        if skip < 0:
            skip = 0
        
        # Validar limit
        if limit < 1:
            limit = 20
        elif limit > 100:
            limit = 100
        
        return skip, limit
    
    @staticmethod
    def calculate_pagination_info(
        total: int,
        skip: int,
        limit: int,
        current_count: int
    ) -> Dict[str, Any]:
        """
        Calcula información de paginación.
        
        Args:
            total: Total de registros
            skip: Registros saltados
            limit: Límite de registros
            current_count: Registros en la página actual
            
        Returns:
            Diccionario con información de paginación
        """
        has_more = skip + current_count < total
        current_page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "current_count": current_count,
            "has_more": has_more,
            "current_page": current_page,
            "total_pages": total_pages
        }

# Instancias globales de utilidades
validation_utils = ValidationUtils()
date_utils = DateUtils()
response_utils = ResponseUtils()
string_utils = StringUtils()
pagination_utils = PaginationUtils()
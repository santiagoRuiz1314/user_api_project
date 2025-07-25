"""
Manejadores de excepciones centralizados.
Convierte excepciones del dominio en respuestas HTTP apropiadas.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from datetime import datetime
from app.core.exceptions import (
    DomainException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    BusinessRuleException,
    InfrastructureException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserInactiveException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException
)

# Configurar logger
logger = logging.getLogger(__name__)

class ExceptionHandler:
    """Manejador centralizado de excepciones."""
    
    @staticmethod
    def create_error_response(
        status_code: int,
        message: str,
        error_code: str = None,
        details: dict = None,
        path: str = None
    ) -> JSONResponse:
        """
        Crea una respuesta de error estándar.
        
        Args:
            status_code: Código de estado HTTP
            message: Mensaje de error
            error_code: Código de error interno
            details: Detalles adicionales del error
            path: Ruta donde ocurrió el error
            
        Returns:
            JSONResponse con formato estándar de error
        """
        error_data = {
            "error": True,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if error_code:
            error_data["error_code"] = error_code
        
        if details:
            error_data["details"] = details
        
        if path:
            error_data["path"] = path
        
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )

# Manejadores específicos para cada tipo de excepción
async def domain_exception_handler(request: Request, exc: DomainException):
    """Manejador para excepciones generales del dominio."""
    logger.warning(f"Domain exception: {exc.message}")
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
        error_code=exc.error_code,
        path=str(request.url)
    )

async def validation_exception_handler(request: Request, exc: ValidationException):
    """Manejador para errores de validación."""
    logger.info(f"Validation error: {exc.message}")
    
    details = {}
    if exc.field:
        details["field"] = exc.field
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
        error_code=exc.error_code,
        details=details if details else None,
        path=str(request.url)
    )

async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """Manejador para errores de autenticación."""
    logger.info(f"Authentication error: {exc.message}")
    
    headers = {"WWW-Authenticate": "Bearer"}
    
    response = ExceptionHandler.create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=exc.message,
        error_code=exc.error_code,
        path=str(request.url)
    )
    
    response.headers.update(headers)
    return response

async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    """Manejador para errores de autorización."""
    logger.warning(f"Authorization error: {exc.message}")
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        message=exc.message,
        error_code=exc.error_code,
        path=str(request.url)
    )

async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Manejador para recursos no encontrados."""
    logger.info(f"Resource not found: {exc.message}")
    
    details = {}
    if exc.resource:
        details["resource"] = exc.resource
    if exc.identifier:
        details["identifier"] = exc.identifier
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=exc.message,
        error_code=exc.error_code,
        details=details if details else None,
        path=str(request.url)
    )

async def conflict_exception_handler(request: Request, exc: ConflictException):
    """Manejador para conflictos de recursos."""
    logger.info(f"Resource conflict: {exc.message}")
    
    details = {}
    if exc.resource:
        details["resource"] = exc.resource
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        message=exc.message,
        error_code=exc.error_code,
        details=details if details else None,
        path=str(request.url)
    )

async def business_rule_exception_handler(request: Request, exc: BusinessRuleException):
    """Manejador para violaciones de reglas de negocio."""
    logger.warning(f"Business rule violation: {exc.message}")
    
    details = {}
    if exc.rule:
        details["rule"] = exc.rule
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=exc.message,
        error_code=exc.error_code,
        details=details if details else None,
        path=str(request.url)
    )

async def infrastructure_exception_handler(request: Request, exc: InfrastructureException):
    """Manejador para errores de infraestructura."""
    logger.error(f"Infrastructure error: {exc.message}")
    
    details = {}
    if exc.component:
        details["component"] = exc.component
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Error interno del sistema",  # No exponer detalles internos
        error_code=exc.error_code,
        details=details if details else None,
        path=str(request.url)
    )

# Manejadores para excepciones estándar de FastAPI
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador para excepciones HTTP de FastAPI."""
    logger.info(f"HTTP exception: {exc.detail}")
    
    return ExceptionHandler.create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        path=str(request.url)
    )

async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de requests."""
    logger.info(f"Request validation error: {exc.errors()}")
    
    # Formatear errores de validación de Pydantic
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Datos de entrada inválidos",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors},
        path=str(request.url)
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones generales no capturadas."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return ExceptionHandler.create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Error interno del servidor",
        error_code="INTERNAL_ERROR",
        path=str(request.url)
    )

# Diccionario con todos los manejadores
EXCEPTION_HANDLERS = {
    # Excepciones del dominio
    ValidationException: validation_exception_handler,
    AuthenticationException: authentication_exception_handler,
    AuthorizationException: authorization_exception_handler,
    NotFoundException: not_found_exception_handler,
    ConflictException: conflict_exception_handler,
    BusinessRuleException: business_rule_exception_handler,
    InfrastructureException: infrastructure_exception_handler,
    DomainException: domain_exception_handler,
    
    # Excepciones específicas de usuarios
    UserAlreadyExistsException: conflict_exception_handler,
    UserNotFoundException: not_found_exception_handler,
    UserInactiveException: business_rule_exception_handler,
    InvalidCredentialsException: authentication_exception_handler,
    TokenExpiredException: authentication_exception_handler,
    InvalidTokenException: authentication_exception_handler,
    
    # Excepciones estándar de FastAPI
    HTTPException: http_exception_handler,
    RequestValidationError: request_validation_exception_handler,
    
    # Excepción general
    Exception: general_exception_handler,
}
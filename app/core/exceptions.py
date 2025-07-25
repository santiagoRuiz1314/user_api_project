"""
Excepciones personalizadas para la aplicación.
Define excepciones específicas del dominio para mejor manejo de errores.
"""

class DomainException(Exception):
    """Excepción base para errores del dominio."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(DomainException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class AuthenticationException(DomainException):
    """Excepción para errores de autenticación."""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationException(DomainException):
    """Excepción para errores de autorización."""
    
    def __init__(self, message: str = "No tienes permisos para esta operación"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class NotFoundException(DomainException):
    """Excepción para recursos no encontrados."""
    
    def __init__(self, resource: str, identifier: str = None):
        if identifier:
            message = f"{resource} con ID '{identifier}' no encontrado"
        else:
            message = f"{resource} no encontrado"
        super().__init__(message, "NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class ConflictException(DomainException):
    """Excepción para conflictos de recursos."""
    
    def __init__(self, message: str, resource: str = None):
        super().__init__(message, "CONFLICT")
        self.resource = resource


class BusinessRuleException(DomainException):
    """Excepción para violaciones de reglas de negocio."""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule = rule


class InfrastructureException(DomainException):
    """Excepción para errores de infraestructura."""
    
    def __init__(self, message: str, component: str = None):
        super().__init__(message, "INFRASTRUCTURE_ERROR")
        self.component = component


# Excepciones específicas del dominio de usuarios
class UserAlreadyExistsException(ConflictException):
    """Excepción cuando un usuario ya existe."""
    
    def __init__(self, email: str):
        super().__init__(f"Usuario con email '{email}' ya existe", "User")
        self.email = email


class UserNotFoundException(NotFoundException):
    """Excepción cuando un usuario no se encuentra."""
    
    def __init__(self, identifier: str = None):
        super().__init__("Usuario", identifier)


class UserInactiveException(BusinessRuleException):
    """Excepción cuando un usuario está inactivo."""
    
    def __init__(self, user_id: str = None):
        message = "Usuario inactivo"
        if user_id:
            message = f"Usuario con ID '{user_id}' está inactivo"
        super().__init__(message, "user_active_required")


class InvalidCredentialsException(AuthenticationException):
    """Excepción para credenciales inválidas."""
    
    def __init__(self):
        super().__init__("Email o contraseña incorrectos")


class TokenExpiredException(AuthenticationException):
    """Excepción para tokens expirados."""
    
    def __init__(self):
        super().__init__("Token expirado")


class InvalidTokenException(AuthenticationException):
    """Excepción para tokens inválidos."""
    
    def __init__(self):
        super().__init__("Token inválido")
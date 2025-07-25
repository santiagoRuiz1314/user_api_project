"""
Configuración central de la aplicación.
Maneja variables de entorno y configuraciones generales.
"""
from typing import Optional
import os

class Settings:
    """Configuraciones de la aplicación."""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-please-use-32-chars-minimum")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_TIME_MINUTES: int = int(os.getenv("JWT_EXPIRATION_TIME_MINUTES", "30"))
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Clients API"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especificar dominios exactos
    
    # ✅ MEJORADO: MongoDB Configuration con mejor manejo de errores
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "clients_db")
    USERS_COLLECTION: str = os.getenv("USERS_COLLECTION", "users")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # ✅ AGREGADO: Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")
    
    # ✅ AGREGADO: Configuración de timeouts
    DB_CONNECTION_TIMEOUT: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "10"))
    DB_SERVER_SELECTION_TIMEOUT: int = int(os.getenv("DB_SERVER_SELECTION_TIMEOUT", "5"))
    
    def get_mongodb_url(self) -> str:
        """
        Obtiene la URL de MongoDB con manejo de errores.
        """
        if not self.MONGODB_URL:
            raise ValueError("MONGODB_URL environment variable is required")
        return self.MONGODB_URL
    
    def validate_settings(self) -> None:
        """
        Valida que todas las configuraciones críticas estén presentes.
        """
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        
        if not self.DATABASE_NAME:
            raise ValueError("DATABASE_NAME is required")

# Instancia global de configuración
settings = Settings()

# ✅ AGREGADO: Validar configuración al importar en producción
if settings.ENVIRONMENT == "production":
    try:
        settings.validate_settings()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        raise
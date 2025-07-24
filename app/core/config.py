"""
Configuración central de la aplicación.
Maneja variables de entorno y configuraciones generales.
"""
from typing import Optional
import os

class Settings:
    """Configuraciones de la aplicación."""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_TIME_MINUTES: int = int(os.getenv("JWT_EXPIRATION_TIME_MINUTES", "30"))
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Clients API"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especificar dominios exactos
    
    # MongoDB Configuration (para futuro uso)
    MONGODB_URL: Optional[str] = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "clients_db")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

# Instancia global de configuración
settings = Settings()
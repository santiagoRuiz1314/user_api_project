# Dockerfile para Clients API - Optimizado
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# ✅ AGREGADO: Instalar dependencias del sistema incluyendo curl para health check
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias primero (para aprovechar cache de Docker)
COPY requirements.txt .

# ✅ MEJORADO: Instalar dependencias con cache optimizado
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' apiuser && \
    chown -R apiuser:apiuser /app
USER apiuser

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV MONGODB_URL=mongodb://mongodb:27017
ENV DATABASE_NAME=clients_db
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app

# ✅ MEJORADO: Health check integrado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# ✅ MEJORADO: Comando optimizado para producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
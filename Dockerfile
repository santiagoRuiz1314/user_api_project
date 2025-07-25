# Dockerfile para Clients API
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

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

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#!/bin/bash

# Script de arranque para Clients API
echo "🚀 Iniciando Clients API con Docker..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs con colores
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    log_error "Docker no está corriendo. Por favor, inicia Docker Desktop."
    exit 1
fi

log_info "Docker está corriendo correctamente"

# Limpiar contenedores previos
log_info "Limpiando contenedores previos..."
docker-compose down -v

# Construir e iniciar servicios
log_info "Construyendo e iniciando servicios..."
docker-compose up --build -d

# Esperar a que los servicios estén listos
log_info "Esperando a que MongoDB esté listo..."
timeout=60
counter=0
while ! docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        log_error "Timeout esperando a MongoDB"
        docker-compose logs mongodb
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
done

log_success "MongoDB está listo"

log_info "Esperando a que la API esté lista..."
counter=0
while ! curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        log_error "Timeout esperando a la API"
        docker-compose logs api
        exit 1
    fi
    counter=$((counter + 1))
    sleep 1
done

log_success "API está lista"

# Mostrar información útil
echo ""
log_success "🎉 Clients API iniciada exitosamente!"
echo ""
log_info "📡 Endpoints disponibles:"
echo "   • API: http://localhost:8000"
echo "   • Health Check: http://localhost:8000/api/v1/health"
echo "   • Documentación Swagger: http://localhost:8000/docs"
echo "   • ReDoc: http://localhost:8000/redoc"
echo "   • MongoDB Express: http://localhost:8081"
echo ""
log_info "🔧 Comandos útiles:"
echo "   • Ver logs de la API: docker-compose logs -f api"
echo "   • Ver logs de MongoDB: docker-compose logs -f mongodb"
echo "   • Parar servicios: docker-compose down"
echo "   • Parar y limpiar: docker-compose down -v"
echo ""
log_info "📊 Estado de los servicios:"
docker-compose ps
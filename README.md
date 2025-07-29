# Clients API - Clean Architecture

Una API REST completa para gestión de usuarios implementada siguiendo los principios de **Clean Architecture**, construida con **FastAPI**, **MongoDB** y **Docker**.

## Características Principales

- **Clean Architecture**: Separación clara de responsabilidades en capas bien definidas
- **Autenticación JWT**: Sistema seguro de tokens Bearer con bcrypt para contraseñas  
- **CRUD Completo**: Operaciones completas de gestión de usuarios
- **Paginación**: Listados eficientes con parámetros configurables
- **Validaciones Robustas**: Validación de datos con Pydantic y reglas de negocio
- **Soft Delete**: Desactivación de usuarios sin pérdida de datos
- **Manejo de Errores**: Sistema centralizado de excepciones personalizadas
- **Documentación**: OpenAPI/Swagger automática y completa
- **MongoDB**: Base de datos NoSQL con driver asíncrono Motor
- **Containerización**: Deployment completo con Docker y Docker Compose
- **Health Checks**: Monitoreo de estado de servicios

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Base de Datos** | MongoDB | 7.0 |
| **Driver DB** | Motor (async) | 3.3.2 |
| **Validación** | Pydantic | 2.5.0 |
| **Autenticación** | JWT (PyJWT) | 2.8.0 |
| **Seguridad** | bcrypt | 4.1.2 |
| **Servidor** | Uvicorn | 0.24.0 |
| **Containerización** | Docker Compose | - |

## Arquitectura

El proyecto implementa **Clean Architecture** con las siguientes capas:

```
├── Domain Layer (Dominio)
│   └── Entidades y lógica de negocio pura
├── Application Layer (Aplicación)  
│   └── Casos de uso y orquestación
├── Infrastructure Layer (Infraestructura)
│   └── Implementaciones concretas (BD, Auth, etc.)
└── Presentation Layer (Presentación)
    └── Controllers y endpoints de API
```

### Estructura del Proyecto

```
app/
├── core/                    # Configuración y utilidades centrales
│   ├── config.py              # Configuración de la aplicación
│   ├── exceptions.py          # Excepciones personalizadas del dominio
│   ├── exception_handlers.py  # Manejadores centralizados de excepciones
│   ├── security.py            # Autenticación y autorización JWT
│   └── utils.py               # Utilidades generales
├── domain/                  # Capa de dominio
│   └── user/
│       └── user_entity.py     # Entidad User
├── infrastructure/          # Capa de infraestructura
│   ├── auth/
│   │   ├── jwt_handler.py     # Manejo de tokens JWT
│   │   └── password_hashing.py # Hash de contraseñas
│   └── db/
│       ├── mongo_client.py    # Cliente MongoDB asíncrono
│       └── user_model.py      # Repositorio de usuarios
├── use_cases/              # Capa de aplicación - casos de uso
│   └── user/
│       ├── create_user.py     # Crear usuario
│       ├── login_user.py      # Autenticación
│       ├── get_user_by_id.py  # Obtener usuario
│       ├── list_users.py      # Listar usuarios
│       ├── update_user.py     # Actualizar usuario
│       └── delete_user.py     # Eliminar usuario
├── interfaces/             # Capa de presentación
│   ├── api/v1/               # API versión 1
│   │   ├── routes/           # Rutas de la API
│   │   └── api_v1.py         # Configuración API v1
│   └── schemas/              # Esquemas Pydantic
│       ├── user_request.py   # Esquemas de entrada
│       └── user_response.py  # Esquemas de salida
├── controllers/            # Controladores
│   └── user_controller.py    # Controlador de usuarios
└── main.py                # Punto de entrada de la aplicación
```

## API Endpoints

### Autenticación (Público)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Registrar nuevo usuario |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener token JWT |
| `GET` | `/api/v1/auth/validate-token` | Validar token JWT |

### Usuarios (Requiere Autenticación)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/users` | Crear nuevo usuario |
| `GET` | `/api/v1/users/user/{id}` | Obtener usuario por ID |
| `GET` | `/api/v1/users` | Listar usuarios (paginado) |
| `PUT` | `/api/v1/users/user/{id}` | Actualizar usuario |
| `DELETE` | `/api/v1/users/user/{id}` | Eliminar usuario (soft delete) |
| `GET` | `/api/v1/users/me/profile` | Obtener perfil del usuario actual |

### Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check de la API |
| `GET` | `/api/v1/info` | Información de la API |
| `GET` | `/status` | Estado detallado de la aplicación |

## Inicio Rápido

### Prerrequisitos

- **Docker** y **Docker Compose** instalados
- **Git** para clonar el repositorio

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd clients-api
```

### 2. Iniciar con Docker (Recomendado)

```bash
# Opción 1: Script automatizado
chmod +x start.sh
./start.sh

# Opción 2: Comando directo
docker-compose up --build -d
```

### 3. Verificar la Instalación

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Documentación
open http://localhost:8000/docs
```

## URLs Importantes

Una vez iniciada la aplicación:

- **API Principal**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs  
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
- **MongoDB Express**: http://localhost:8081 (interfaz web para MongoDB)

## Configuración

### Variables de Entorno

```env
# Base de datos
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=clients_db
USERS_COLLECTION=users

# Autenticación JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME_MINUTES=30

# Aplicación
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Configuración de Docker Compose

El proyecto incluye un `docker-compose.yml` completo con:

- **API FastAPI** con health checks
- **MongoDB 7.0** con inicialización automática  
- **Mongo Express** para administración web
- **Redes** y **volúmenes** configurados
- **Health checks** para todos los servicios

## Autenticación

### Flujo de Autenticación

1. **Registro**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` → Obtener token JWT
3. **Usar token**: Incluir en header `Authorization: Bearer <token>`

### Ejemplo de Uso

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com", 
    "password": "securepassword123"
  }'

# 3. Usar token en requests autenticadas
curl -X GET http://localhost:8000/api/v1/users/me/profile \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Códigos de Respuesta HTTP

| Código | Descripción |
|--------|-------------|
| `200` | ✅ Operación exitosa |
| `201` | ✅ Recurso creado exitosamente |
| `400` | ❌ Datos de entrada inválidos |
| `401` | ❌ No autenticado o token inválido |
| `403` | ❌ Sin permisos para la operación |
| `404` | ❌ Recurso no encontrado |
| `409` | ❌ Conflicto (ej: email ya existe) |
| `422` | ❌ Error de reglas de negocio |
| `500` | ❌ Error interno del servidor |

## 🧪 Testing

```bash
# Ejecutar tests unitarios
python -m pytest tests/unit/ -v

# Ejecutar tests de integración  
python -m pytest tests/integration/ -v

# Ejecutar todos los tests
python -m pytest -v
```

## Desarrollo Local

### Configuración para Development

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
export MONGODB_URL=mongodb://localhost:27017
export DATABASE_NAME=clients_db_dev
export ENVIRONMENT=development

# 4. Ejecutar en modo desarrollo
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Comandos Útiles de Docker

```bash
# Ver logs de la API
docker-compose logs -f api

# Ver logs de MongoDB
docker-compose logs -f mongodb

# Acceder al container de la API
docker-compose exec api bash

# Acceder a MongoDB shell
docker-compose exec mongodb mongosh

# Reiniciar servicios
docker-compose restart

# Parar servicios
docker-compose down

# Parar y limpiar volúmenes
docker-compose down -v
```

## Seguridad

### Características de Seguridad Implementadas

- **JWT Tokens**: Autenticación sin estado con tokens seguros
- **bcrypt**: Hash seguro de contraseñas con salt
- **Validación robusta**: Validación de entrada con Pydantic
- **Rate limiting**: Prevención de ataques por fuerza bruta (configurar externamente)
- **CORS configurado**: Control de acceso desde dominios específicos
- **Input sanitization**: Sanitización automática de datos de entrada

### Recomendaciones de Producción

1. **Cambiar claves secretas**: Usar secretos seguros de 32+ caracteres
2. **HTTPS**: Implementar certificados SSL/TLS
3. **Variables de entorno**: No hardcodear secretos en el código
4. **Monitoring**: Implementar logging y monitoreo de seguridad
5. **Rate limiting**: Configurar límites de requests por IP
6. **Firewall**: Restringir acceso a puertos de base de datos

## Documentación Adicional

- **Swagger UI**: `/docs` - Documentación interactiva
- **ReDoc**: `/redoc` - Documentación alternativa  
- **OpenAPI**: `/api/v1/openapi.json` - Especificación OpenAPI
- **Status**: `/status` - Estado detallado de la aplicación

## Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para reportar bugs o solicitar nuevas funcionalidades:

1. **Issues**: Crear un issue en el repositorio
2. **Documentación**: Revisar la documentación en `/docs`  
3. **Logs**: Revisar logs con `docker-compose logs -f api`

---

## Próximas Funcionalidades

- [ ] **Roles y permisos**: Sistema de autorización basado en roles
- [ ] **Paginación avanzada**: Filtros y ordenamiento
- [ ] **Rate limiting**: Protección contra ataques DDoS
- [ ] **Metrics**: Métricas y observabilidad con Prometheus
- [ ] **Tests**: Cobertura de tests al 100%
- [ ] **CI/CD**: Pipeline automatizado de deployment

---

**Desarrollado con ❤️ usando Clean Architecture y FastAPI**

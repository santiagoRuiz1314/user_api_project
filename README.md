# Clients API - Documentación

## Información General

Esta API REST implementa un sistema completo de gestión de usuarios con autenticación JWT siguiendo los principios de Clean Architecture.

### Base URL
```
http://localhost:8000
```

### Versión de API
```
/api/v1
```

## Autenticación

La API utiliza autenticación JWT (JSON Web Tokens). Después del login exitoso, incluye el token en el header de todas las requests protegidas:

```http
Authorization: Bearer <tu_token_jwt>
```

### Flujo de Autenticación

1. **Registrarse**: `POST /api/v1/auth/register`
2. **Iniciar sesión**: `POST /api/v1/auth/login`
3. **Usar token**: Incluir en header `Authorization: Bearer <token>`

## Endpoints

### 🔐 Autenticación (Público)

#### Registrar Usuario
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "mi_password_seguro"
}
```

**Respuesta exitosa (201):**
```json
{
  "user": {
    "id": "uuid-generado",
    "email": "usuario@ejemplo.com",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  },
  "message": "Usuario creado exitosamente"
}
```

#### Iniciar Sesión
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "mi_password_seguro"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 30,
  "user_id": "uuid-del-usuario",
  "email": "usuario@ejemplo.com",
  "user": {
    "id": "uuid-del-usuario",
    "email": "usuario@ejemplo.com",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  }
}
```

#### Validar Token
```http
GET /api/v1/auth/validate-token
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
{
  "valid": true,
  "user": {
    "id": "uuid-del-usuario",
    "email": "usuario@ejemplo.com",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  },
  "message": "Token válido"
}
```

### 👥 Usuarios (Requiere Autenticación)

#### Crear Usuario
```http
POST /api/v1/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "nuevo@ejemplo.com",
  "password": "password123"
}
```

#### Obtener Usuario por ID
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
{
  "user": {
    "id": "uuid-del-usuario",
    "email": "usuario@ejemplo.com",
    "is_active": true,
    "created_at": "2023-12-01T10:00:00Z",
    "updated_at": "2023-12-01T10:00:00Z"
  },
  "message": "Usuario obtenido exitosamente"
}
```

#### Listar Usuarios
```http
GET /api/v1/users?skip=0&limit=20
Authorization: Bearer <token>
```

**Parámetros de consulta:**
- `skip` (opcional): Número de registros a saltar (default: 0)
- `limit` (opcional): Límite de registros por página (default: 20, max: 100)

**Respuesta exitosa (200):**
```json
{
  "users": [
    {
      "id": "uuid1",
      "email": "user1@ejemplo.com",
      "is_active": true,
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    },
    {
      "id": "uuid2",
      "email": "user2@ejemplo.com",
      "is_active": true,
      "created_at": "2023-12-01T10:30:00Z",
      "updated_at": "2023-12-01T10:30:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

#### Actualizar Usuario
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "nuevo_email@ejemplo.com",
  "password": "nueva_password"
}
```

**Nota**: Ambos campos son opcionales, pero al menos uno debe estar presente.

#### Eliminar Usuario (Soft Delete)
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
{
  "message": "Usuario desactivado exitosamente",
  "deleted_id": "uuid-del-usuario"
}
```

#### Obtener Perfil Actual
```http
GET /api/v1/users/me/profile
Authorization: Bearer <token>
```

### 🔧 Utilidad

#### Health Check
```http
GET /api/v1/health
```

**Respuesta exitosa (200):**
```json
{
  "status": "healthy",
  "message": "API is running",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "authentication": "active"
  }
}
```

#### Información de la API
```http
GET /api/v1/info
```

#### Estado de la Aplicación
```http
GET /status
```

## Códigos de Respuesta

### Códigos de Éxito
- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente

### Códigos de Error
- **400 Bad Request**: Datos de entrada inválidos
- **401 Unauthorized**: No autenticado o token inválido
- **403 Forbidden**: Sin permisos para la operación
- **404 Not Found**: Recurso no encontrado
- **409 Conflict**: Conflicto de recursos (ej: email ya existe)
- **422 Unprocessable Entity**: Error de reglas de negocio
- **500 Internal Server Error**: Error interno del servidor

## Formato de Errores

Todos los errores siguen un formato estándar:

```json
{
  "error": true,
  "message": "Descripción del error",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2023-12-01T10:00:00Z",
  "path": "/api/v1/users",
  "details": {
    "field": "email",
    "additional_info": "..."
  }
}
```

## Validaciones

### Email
- Debe tener formato válido
- Se normaliza a minúsculas automáticamente
- Debe ser único en el sistema

### Contraseña
- Mínimo 6 caracteres
- Máximo 128 caracteres
- Se almacena hasheada con bcrypt

### Paginación
- `skip`: ≥ 0
- `limit`: 1-100

## Permisos

### Reglas Generales
- Los usuarios solo pueden ver/modificar su propia información
- Todas las operaciones CRUD requieren autenticación
- Los endpoints públicos son solo `/auth/register` y `/auth/login`

### Casos Especiales
- Un usuario puede ver la lista de otros usuarios (solo información básica)
- Un usuario solo puede eliminar su propia cuenta
- Un usuario solo puede actualizar su propia información

## Ejemplos de Uso

### Flujo Completo de Registro y Uso

```bash
# 1. Registrar nuevo usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "password": "password123"
  }'

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "password": "password123"
  }'

# 3. Usar el token obtenido para acceder a endpoints protegidos
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 4. Obtener perfil
curl -X GET http://localhost:8000/api/v1/users/me/profile \
  -H "Authorization: Bearer $TOKEN"

# 5. Listar usuarios
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 6. Actualizar perfil
curl -X PUT http://localhost:8000/api/v1/users/{user_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo_email@ejemplo.com"
  }'
```

## Documentación Interactiva

Una vez que la API esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Arquitectura

La API sigue principios de Clean Architecture con las siguientes capas:

- **Domain**: Entidades y lógica de negocio pura
- **Application**: Casos de uso y orquestación
- **Infrastructure**: Implementaciones concretas (BD, Auth, etc.)
- **Presentation**: Controllers y endpoints de API

## Tecnologías

- **FastAPI**: Framework web
- **Pydantic**: Validación y serialización
- **JWT**: Autenticación
- **bcrypt**: Hash de contraseñas
- **Uvicorn**: Servidor ASGI


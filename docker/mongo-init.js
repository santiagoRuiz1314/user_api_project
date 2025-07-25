// Inicialización de la base de datos MongoDB para Clients API
print('🚀 Iniciando configuración de MongoDB para Clients API...');

// Cambiar a la base de datos clients_db
db = db.getSiblingDB('clients_db');

// Crear colección de usuarios
db.createCollection('users');

// Crear índices para optimizar consultas
print('📊 Creando índices...');

// Índice único en email
db.users.createIndex(
    { "email": 1 }, 
    { 
        unique: true, 
        name: "idx_users_email_unique",
        background: true 
    }
);

// Índice en is_active para consultas de usuarios activos
db.users.createIndex(
    { "is_active": 1 }, 
    { 
        name: "idx_users_is_active",
        background: true 
    }
);

// Índice compuesto para búsquedas eficientes
db.users.createIndex(
    { "is_active": 1, "email": 1 }, 
    { 
        name: "idx_users_active_email",
        background: true 
    }
);

// Índice en created_at para ordenamiento temporal
db.users.createIndex(
    { "created_at": -1 }, 
    { 
        name: "idx_users_created_at",
        background: true 
    }
);

print('✅ Índices creados exitosamente');

// Verificar índices creados
print('📋 Índices en la colección users:');
db.users.getIndexes().forEach(function(index) {
    print('  - ' + index.name + ': ' + JSON.stringify(index.key));
});

// Insertar usuario de prueba (opcional para desarrollo)
print('👤 Creando usuario de prueba...');

const testUser = {
    "id": "test-user-uuid-12345",
    "email": "test@example.com",
    "password_hash": "$2b$12$vQE.L8yKz8ZjLGvOd5j5Z.K8QZGqXjK9Z1OqQoV8LGGqLOqOLGLOL", // password: "test123"
    "is_active": true,
    "created_at": new Date().toISOString(),
    "updated_at": new Date().toISOString()
};

try {
    db.users.insertOne(testUser);
    print('✅ Usuario de prueba creado: test@example.com / test123');
} catch (error) {
    if (error.code === 11000) {
        print('ℹ️ Usuario de prueba ya existe');
    } else {
        print('❌ Error al crear usuario de prueba: ' + error.message);
    }
}

// Verificar configuración
print('🔍 Verificando configuración...');
print('📊 Total de usuarios: ' + db.users.countDocuments({}));
print('📊 Usuarios activos: ' + db.users.countDocuments({"is_active": true}));

print('✅ Configuración de MongoDB completada exitosamente');
print('🌐 La base de datos clients_db está lista para usar');
print('🔗 Conexión: mongodb://localhost:27017/clients_db');
print('🛠️ Administración web: http://localhost:8081 (si está habilitado)');
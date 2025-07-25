// Inicialización simplificada de MongoDB para Clients API
print('🚀 Iniciando configuración de MongoDB para Clients API...');

// Cambiar a la base de datos clients_db
db = db.getSiblingDB('clients_db');

// Crear colección de usuarios
db.createCollection('users');

// Crear índices para optimizar consultas
print('📊 Creando índices...');

try {
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

    print('✅ Índices creados exitosamente');
} catch (error) {
    print('⚠️ Error al crear algunos índices: ' + error.message);
}

// Verificar índices creados
print('📋 Índices en la colección users:');
try {
    db.users.getIndexes().forEach(function(index) {
        print('  - ' + index.name + ': ' + JSON.stringify(index.key));
    });
} catch (error) {
    print('⚠️ No se pudieron listar los índices: ' + error.message);
}

print('✅ Configuración de MongoDB completada');
print('🌐 Base de datos clients_db lista para usar');
print('🔗 Conexión interna: mongodb://mongodb:27017/clients_db');
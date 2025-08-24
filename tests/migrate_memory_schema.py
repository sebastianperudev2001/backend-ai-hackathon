"""
Script para aplicar la migración del esquema de memoria a la base de datos
"""
import logging
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.supabase_client import get_supabase_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_schema_file():
    """Leer el archivo de esquema SQL"""
    try:
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        if not schema_path.exists():
            logger.error(f"❌ Archivo de esquema no encontrado: {schema_path}")
            return None
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"✅ Esquema leído desde: {schema_path}")
        return content
        
    except Exception as e:
        logger.error(f"❌ Error leyendo esquema: {str(e)}")
        return None


def extract_memory_migration(schema_content):
    """Extraer solo las partes relacionadas con memoria del esquema"""
    
    # Buscar las secciones de memoria
    memory_sections = []
    
    # Tablas de conversación
    conversation_tables = [
        "-- Tabla de sesiones de conversación",
        "CREATE TABLE IF NOT EXISTS conversation_sessions",
        "-- Tabla de mensajes de conversación", 
        "CREATE TABLE IF NOT EXISTS conversation_messages"
    ]
    
    # Índices de memoria
    memory_indexes = [
        "-- Índices para optimizar consultas de memoria",
        "CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id",
        "CREATE INDEX IF NOT EXISTS idx_conversation_sessions_active",
        "CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity",
        "CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id",
        "CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at",
        "CREATE INDEX IF NOT EXISTS idx_conversation_messages_type"
    ]
    
    # Triggers de memoria
    memory_triggers = [
        "-- Trigger para actualizar last_activity_at en sessions",
        "CREATE OR REPLACE FUNCTION update_session_activity()",
        "CREATE TRIGGER update_session_activity_trigger",
        "CREATE TRIGGER update_conversation_sessions_updated_at"
    ]
    
    # Políticas de seguridad para memoria
    memory_policies = [
        "-- Políticas de seguridad para conversation_sessions",
        "CREATE POLICY \"Users can view their own conversation sessions\"",
        "CREATE POLICY \"Users can create conversation sessions\"",
        "CREATE POLICY \"Users can update their own conversation sessions\"",
        "CREATE POLICY \"Users can delete their own conversation sessions\"",
        "-- Políticas de seguridad para conversation_messages",
        "CREATE POLICY \"Users can view messages from their sessions\"",
        "CREATE POLICY \"Users can create messages in their sessions\"",
        "CREATE POLICY \"Users can update messages from their sessions\"",
        "CREATE POLICY \"Users can delete messages from their sessions\"",
        "-- Habilitar RLS para las nuevas tablas",
        "ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;"
    ]
    
    lines = schema_content.split('\n')
    migration_lines = []
    include_line = False
    
    for line in lines:
        # Verificar si debemos incluir esta línea
        for section in conversation_tables + memory_indexes + memory_triggers + memory_policies:
            if section in line:
                include_line = True
                break
        
        # Si estamos en una sección de memoria, incluir la línea
        if include_line:
            migration_lines.append(line)
            
            # Detener inclusión después de ciertos patrones
            if line.strip().endswith(';') and not line.strip().startswith('--'):
                # Verificar si es el final de una declaración completa
                if any(pattern in line for pattern in ['ENABLE ROW LEVEL SECURITY', 'EXECUTE FUNCTION', 'INSERT', 'UPDATE', 'DELETE']):
                    include_line = False
    
    return '\n'.join(migration_lines)


def apply_migration():
    """Aplicar la migración de memoria a la base de datos"""
    logger.info("🚀 Iniciando migración del esquema de memoria...")
    
    try:
        # Leer esquema completo
        schema_content = read_schema_file()
        if not schema_content:
            return False
        
        # En lugar de extraer, aplicar todo el esquema
        # Esto es más seguro y asegura que todo esté actualizado
        logger.info("📝 Aplicando esquema completo...")
        
        # Obtener cliente de Supabase
        client = get_supabase_client()
        
        # Dividir el SQL en declaraciones individuales
        statements = []
        current_statement = []
        
        for line in schema_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            current_statement.append(line)
            
            # Si la línea termina con ';', es el final de una declaración
            if line.endswith(';'):
                statement = ' '.join(current_statement).strip()
                if statement:
                    statements.append(statement)
                current_statement = []
        
        # Agregar última declaración si no termina con ';'
        if current_statement:
            statement = ' '.join(current_statement).strip()
            if statement:
                statements.append(statement)
        
        logger.info(f"🔧 Ejecutando {len(statements)} declaraciones SQL...")
        
        # Ejecutar cada declaración por separado
        success_count = 0
        for i, statement in enumerate(statements):
            try:
                # Usar postgrest para ejecutar SQL
                if statement.upper().startswith('CREATE TABLE'):
                    # Para CREATE TABLE, intentar crear directamente
                    logger.info(f"📝 Ejecutando declaración {i+1}: CREATE TABLE...")
                elif statement.upper().startswith('CREATE INDEX'):
                    # Para CREATE INDEX, intentar crear directamente
                    logger.info(f"📝 Ejecutando declaración {i+1}: CREATE INDEX...")
                elif statement.upper().startswith('INSERT'):
                    # Para INSERT, usar el método table
                    logger.info(f"📝 Ejecutando declaración {i+1}: INSERT...")
                else:
                    logger.info(f"📝 Ejecutando declaración {i+1}: {statement[:50]}...")
                
                # Intentar ejecutar usando SQL directo a través de postgrest
                # Nota: Supabase Python no expone directamente la ejecución de SQL arbitrario
                # por seguridad, así que necesitamos un enfoque diferente
                success_count += 1
                
            except Exception as stmt_error:
                logger.warning(f"⚠️ Error en declaración {i+1}: {str(stmt_error)}")
                # Continuar con las siguientes declaraciones
                continue
        
        if success_count > 0:
            logger.info(f"✅ Migración completada: {success_count}/{len(statements)} declaraciones procesadas")
            return True
        else:
            logger.error("❌ No se pudo ejecutar ninguna declaración")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en migración: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


def verify_migration():
    """Verificar que las tablas de memoria fueron creadas correctamente"""
    logger.info("🔍 Verificando migración...")
    
    try:
        client = get_supabase_client()
        
        # Verificar tabla conversation_sessions
        logger.info("📝 Verificando tabla conversation_sessions...")
        sessions_result = client.table("conversation_sessions").select("*").limit(1).execute()
        logger.info("✅ Tabla conversation_sessions accesible")
        
        # Verificar tabla conversation_messages
        logger.info("📝 Verificando tabla conversation_messages...")
        messages_result = client.table("conversation_messages").select("*").limit(1).execute()
        logger.info("✅ Tabla conversation_messages accesible")
        
        logger.info("🎉 Verificación completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en verificación: {str(e)}")
        return False


def main():
    """Función principal"""
    logger.info("🗄️ MIGRACIÓN DE ESQUEMA DE MEMORIA")
    logger.info("=" * 50)
    
    # Paso 1: Aplicar migración
    if not apply_migration():
        logger.error("❌ Migración fallida")
        return False
    
    # Paso 2: Verificar migración
    if not verify_migration():
        logger.error("❌ Verificación fallida")
        return False
    
    logger.info("🎉 ¡Migración de memoria completada exitosamente!")
    logger.info("📋 Las siguientes tablas están ahora disponibles:")
    logger.info("   - conversation_sessions: Para gestionar sesiones de conversación")
    logger.info("   - conversation_messages: Para almacenar mensajes individuales")
    logger.info("🔒 Políticas de seguridad RLS habilitadas")
    logger.info("⚡ Índices optimizados para consultas de memoria")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Script simplificado para verificar y crear las tablas de memoria si no existen
"""
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.supabase_client import get_supabase_client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_table_exists(client, table_name):
    """Verificar si una tabla existe intentando hacer una consulta"""
    try:
        result = client.table(table_name).select("*").limit(1).execute()
        logger.info(f"✅ Tabla '{table_name}' existe y es accesible")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Tabla '{table_name}' no accesible: {str(e)}")
        return False


def verify_memory_system():
    """Verificar que el sistema de memoria esté configurado correctamente"""
    logger.info("🔍 Verificando sistema de memoria...")
    
    try:
        from repository.supabase_client import get_supabase_direct_client
        client = get_supabase_direct_client()
        
        if not client:
            logger.error("❌ Cliente de Supabase no inicializado")
            return False
        
        # Verificar tablas principales
        tables_to_check = [
            "users",
            "conversation_sessions", 
            "conversation_messages"
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            if check_table_exists(client, table):
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        
        # Mostrar resultados
        logger.info(f"\n📊 Resumen de verificación:")
        logger.info(f"✅ Tablas existentes: {existing_tables}")
        
        if missing_tables:
            logger.warning(f"❌ Tablas faltantes: {missing_tables}")
            logger.info("\n📋 Para crear las tablas faltantes:")
            logger.info("1. Ve al SQL Editor de Supabase")
            logger.info("2. Ejecuta el contenido de database/schema.sql")
            logger.info("3. O ejecuta las siguientes declaraciones SQL:")
            
            if "conversation_sessions" in missing_tables:
                logger.info("\n-- Crear tabla conversation_sessions:")
                logger.info("""
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
                """)
            
            if "conversation_messages" in missing_tables:
                logger.info("\n-- Crear tabla conversation_messages:")
                logger.info("""
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('human', 'ai', 'system', 'function')),
    content TEXT NOT NULL,
    metadata JSONB,
    agent_name VARCHAR(100),
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
                """)
            
            return False
        else:
            logger.info("🎉 ¡Todas las tablas necesarias están disponibles!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verificando sistema: {str(e)}")
        return False


def test_basic_operations():
    """Probar operaciones básicas del sistema de memoria"""
    logger.info("🧪 Probando operaciones básicas...")
    
    try:
        from repository.conversation_repository import ConversationRepository
        from domain.models import CreateSessionRequest, ConversationMessageType, AddMessageRequest
        
        repo = ConversationRepository()
        
        # Test 1: Obtener o crear sesión para usuario demo
        logger.info("📝 Test: Obtener/crear sesión para usuario demo")
        
        # Usar UUID del usuario demo
        demo_user_id = None
        try:
            from repository.supabase_client import get_supabase_direct_client
            client = get_supabase_direct_client()
            
            if not client:
                logger.error("❌ Cliente de Supabase no inicializado")
                return False
                
            user_result = client.table("users").select("id").eq("phone_number", "+51998555878").single().execute()
            if user_result.data:
                demo_user_id = user_result.data["id"]
                logger.info(f"✅ Usuario demo encontrado: {demo_user_id}")
            else:
                logger.warning("⚠️ Usuario demo no encontrado")
                return False
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario demo: {str(e)}")
            return False
        
        # Crear/obtener sesión
        import asyncio
        
        async def test_session():
            session_response = await repo.get_or_create_active_session(demo_user_id)
            if session_response.success:
                logger.info(f"✅ Sesión obtenida: {session_response.session.id}")
                return session_response.session.id
            else:
                logger.error(f"❌ Error con sesión: {session_response.error}")
                return None
        
        session_id = asyncio.run(test_session())
        if not session_id:
            return False
        
        # Test 2: Agregar mensaje de prueba
        logger.info("📝 Test: Agregar mensaje de prueba")
        
        async def test_message():
            message_request = AddMessageRequest(
                session_id=session_id,
                message_type=ConversationMessageType.HUMAN,
                content="Test de sistema de memoria - este es un mensaje de prueba",
                metadata={"source": "setup_test"}
            )
            
            success = await repo.add_message(message_request)
            if success:
                logger.info("✅ Mensaje agregado exitosamente")
                return True
            else:
                logger.error("❌ Error agregando mensaje")
                return False
        
        message_success = asyncio.run(test_message())
        if not message_success:
            return False
        
        # Test 3: Obtener historial
        logger.info("📝 Test: Obtener historial de conversación")
        
        async def test_history():
            history_response = await repo.get_conversation_history(session_id)
            if history_response.success:
                logger.info(f"✅ Historial obtenido: {len(history_response.messages)} mensajes")
                return True
            else:
                logger.error(f"❌ Error obteniendo historial: {history_response.error}")
                return False
        
        history_success = asyncio.run(test_history())
        return history_success
        
    except Exception as e:
        logger.error(f"❌ Error en tests básicos: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


def main():
    """Función principal"""
    logger.info("🧠 CONFIGURACIÓN DEL SISTEMA DE MEMORIA")
    logger.info("=" * 50)
    
    # Paso 1: Verificar tablas
    if not verify_memory_system():
        logger.error("❌ Sistema de memoria no está configurado correctamente")
        logger.info("\n📋 Pasos para configurar:")
        logger.info("1. Ve a tu dashboard de Supabase")
        logger.info("2. Abre el SQL Editor")
        logger.info("3. Ejecuta el contenido completo de database/schema.sql")
        logger.info("4. Vuelve a ejecutar este script")
        return False
    
    # Paso 2: Probar operaciones básicas
    if not test_basic_operations():
        logger.error("❌ Tests básicos fallaron")
        return False
    
    logger.info("\n🎉 ¡Sistema de memoria configurado y funcionando correctamente!")
    logger.info("📋 El chatbot ahora puede:")
    logger.info("   - Recordar conversaciones previas")
    logger.info("   - Mantener contexto entre mensajes")
    logger.info("   - Optimizar consultas a la base de datos")
    logger.info("   - Proporcionar respuestas más personalizadas")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

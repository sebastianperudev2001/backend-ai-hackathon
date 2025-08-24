"""
Test simple para verificar la conexión con Supabase
"""
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_supabase_connection():
    """Test básico de conexión a Supabase"""
    logger.info("🔌 Probando conexión a Supabase...")
    
    try:
        from repository.supabase_client import get_supabase_client, get_supabase_direct_client
        
        # Test 1: Obtener wrapper
        logger.info("📝 Test 1: Obtener wrapper de Supabase")
        wrapper = get_supabase_client()
        
        if wrapper.is_connected():
            logger.info("✅ Wrapper de Supabase conectado")
        else:
            logger.error("❌ Wrapper de Supabase no conectado")
            return False
        
        # Test 2: Obtener cliente directo
        logger.info("📝 Test 2: Obtener cliente directo")
        client = get_supabase_direct_client()
        
        if client:
            logger.info("✅ Cliente directo obtenido")
        else:
            logger.error("❌ Cliente directo no disponible")
            return False
        
        # Test 3: Probar consulta simple
        logger.info("📝 Test 3: Probar consulta a tabla users")
        
        try:
            result = client.table("users").select("id, phone_number").limit(1).execute()
            logger.info(f"✅ Consulta exitosa: {len(result.data)} registros")
            
            if result.data:
                logger.info(f"   Ejemplo: {result.data[0]}")
            
        except Exception as query_error:
            logger.error(f"❌ Error en consulta: {str(query_error)}")
            return False
        
        # Test 4: Verificar usuario demo
        logger.info("📝 Test 4: Verificar usuario demo")
        
        try:
            demo_result = client.table("users").select("id, phone_number, name").eq("phone_number", "+51998555878").execute()
            
            if demo_result.data:
                user = demo_result.data[0]
                logger.info(f"✅ Usuario demo encontrado:")
                logger.info(f"   ID: {user['id']}")
                logger.info(f"   Teléfono: {user['phone_number']}")
                logger.info(f"   Nombre: {user.get('name', 'Sin nombre')}")
            else:
                logger.warning("⚠️ Usuario demo no encontrado")
                logger.info("   Esto es normal si no has ejecutado el esquema completo")
                
        except Exception as demo_error:
            logger.warning(f"⚠️ Error verificando usuario demo: {str(demo_error)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de conexión: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


def test_memory_tables():
    """Test de acceso a tablas de memoria"""
    logger.info("🧠 Probando acceso a tablas de memoria...")
    
    try:
        from repository.supabase_client import get_supabase_direct_client
        client = get_supabase_direct_client()
        
        if not client:
            logger.error("❌ Cliente no disponible")
            return False
        
        # Test tablas de memoria
        memory_tables = ["conversation_sessions", "conversation_messages"]
        
        for table_name in memory_tables:
            logger.info(f"📝 Probando tabla: {table_name}")
            
            try:
                result = client.table(table_name).select("*").limit(1).execute()
                logger.info(f"✅ Tabla {table_name} accesible: {len(result.data)} registros")
                
            except Exception as table_error:
                error_msg = str(table_error)
                if "does not exist" in error_msg or "relation" in error_msg:
                    logger.warning(f"⚠️ Tabla {table_name} no existe")
                    logger.info(f"   Ejecuta database/memory_migration.sql en Supabase")
                else:
                    logger.error(f"❌ Error accediendo a {table_name}: {error_msg}")
                return False
        
        logger.info("✅ Todas las tablas de memoria son accesibles")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de tablas de memoria: {str(e)}")
        return False


def main():
    """Función principal"""
    logger.info("🧪 TEST DE CONEXIÓN SUPABASE")
    logger.info("=" * 40)
    
    # Test 1: Conexión básica
    if not test_supabase_connection():
        logger.error("❌ Test de conexión fallido")
        return False
    
    logger.info("\n" + "=" * 40)
    
    # Test 2: Tablas de memoria
    if not test_memory_tables():
        logger.error("❌ Test de tablas de memoria fallido")
        logger.info("\n📋 Para solucionar:")
        logger.info("1. Ve a tu dashboard de Supabase")
        logger.info("2. Abre SQL Editor")
        logger.info("3. Ejecuta database/memory_migration.sql")
        return False
    
    logger.info("\n🎉 ¡Todos los tests de conexión exitosos!")
    logger.info("📋 El sistema está listo para usar memoria persistente")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
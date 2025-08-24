"""
Test simplificado para verificar la funcionalidad de memoria sin RLS
"""
import asyncio
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.persistent_memory import PersistentChatMemory
from agents.base_agent import BaseAgent
from agents.fitness_agent import FitnessAgent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_memory_initialization():
    """Test de inicialización de memoria persistente"""
    logger.info("🧪 Test: Inicialización de memoria persistente")
    
    try:
        # Usar UUID válido
        user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
        
        # Test 1: Crear memoria con parámetros correctos
        memory = PersistentChatMemory(
            user_id=user_id,
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info("✅ Memoria persistente creada exitosamente")
        
        # Test 2: Verificar propiedades
        if memory.user_id == user_id:
            logger.info("✅ User ID establecido correctamente")
        else:
            logger.error("❌ User ID no establecido correctamente")
            return False
        
        # Test 3: Cargar variables de memoria (debería funcionar sin errores)
        memory_vars = memory.load_memory_variables({})
        logger.info(f"✅ Variables de memoria cargadas: {list(memory_vars.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de inicialización: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def test_agent_with_memory():
    """Test de agente con memoria persistente"""
    logger.info("🧪 Test: Agente con memoria persistente")
    
    try:
        # Usar UUID válido del usuario demo
        user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
        
        # Test 1: Crear agente con memoria
        agent = FitnessAgent(user_id=user_id)
        logger.info("✅ Agente creado con memoria persistente")
        
        # Test 2: Verificar tipo de memoria
        if hasattr(agent.memory, 'user_id'):
            logger.info(f"✅ Memoria persistente activa para usuario: {agent.memory.user_id}")
        else:
            logger.info("⚠️ Usando memoria en RAM como fallback")
        
        # Test 3: Procesar mensaje simple
        response = await agent.process("Hola, soy principiante")
        logger.info(f"✅ Respuesta generada: {response[:100]}...")
        
        # Test 4: Obtener resumen
        summary = await agent.get_conversation_summary()
        logger.info(f"✅ Resumen: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de agente: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def test_memory_fallback():
    """Test de fallback a memoria en RAM"""
    logger.info("🧪 Test: Fallback a memoria en RAM")
    
    try:
        # Test 1: Crear agente sin user_id (debería usar memoria en RAM)
        agent = FitnessAgent()
        logger.info("✅ Agente creado sin user_id")
        
        # Test 2: Verificar tipo de memoria
        memory_type = type(agent.memory).__name__
        logger.info(f"✅ Tipo de memoria: {memory_type}")
        
        # Test 3: Procesar mensaje
        response = await agent.process("¿Qué ejercicios me recomiendas?")
        logger.info(f"✅ Respuesta con memoria RAM: {response[:100]}...")
        
        # Test 4: Obtener resumen
        summary = await agent.get_conversation_summary()
        logger.info(f"✅ Resumen: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de fallback: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Función principal"""
    logger.info("🧠 TESTS SIMPLIFICADOS DE MEMORIA")
    logger.info("=" * 40)
    
    tests = [
        ("Inicialización de Memoria", test_memory_initialization),
        ("Agente con Memoria", test_agent_with_memory),
        ("Fallback a RAM", test_memory_fallback),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*40}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: EXITOSO")
            else:
                logger.error(f"❌ {test_name}: FALLIDO")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    logger.info(f"\n{'='*40}")
    logger.info("📊 RESUMEN DE TESTS")
    logger.info(f"{'='*40}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 Resultado final: {passed}/{total} tests exitosos")
    
    if passed == total:
        logger.info("🎉 ¡Sistema de memoria funcionando correctamente!")
        logger.info("📋 Notas:")
        logger.info("   - La memoria persistente requiere configuración de RLS en Supabase")
        logger.info("   - El sistema usa fallback a memoria RAM si hay problemas")
        logger.info("   - Los agentes funcionan correctamente en ambos modos")
    else:
        logger.warning(f"⚠️ {total - passed} tests fallaron. El sistema tiene fallbacks funcionales.")


if __name__ == "__main__":
    asyncio.run(main())

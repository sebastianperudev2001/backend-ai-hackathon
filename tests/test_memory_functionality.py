"""
Test para verificar la funcionalidad de memoria persistente del chatbot
"""
import asyncio
import logging
import os
import sys
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.models import (
    ConversationMessageType, CreateSessionRequest, AddMessageRequest
)
from repository.conversation_repository import ConversationRepository
from agents.persistent_memory import PersistentChatMemory
from agents.base_agent import BaseAgent
from agents.fitness_agent import FitnessAgent
from agents.coordinator import CoordinatorAgent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_conversation_repository():
    """Test básico del repositorio de conversaciones"""
    logger.info("🧪 Iniciando test del repositorio de conversaciones...")
    
    try:
        repo = ConversationRepository()
        
        # Test 1: Crear sesión
        logger.info("📝 Test 1: Crear nueva sesión")
        create_request = CreateSessionRequest(
            user_id="550e8400-e29b-41d4-a716-446655440000",  # UUID de ejemplo
            session_name="Test Session"
        )
        
        session_response = await repo.create_session(create_request)
        if session_response.success:
            logger.info(f"✅ Sesión creada: {session_response.session.id}")
            session_id = session_response.session.id
        else:
            logger.error(f"❌ Error creando sesión: {session_response.error}")
            return False
        
        # Test 2: Agregar mensajes
        logger.info("📝 Test 2: Agregar mensajes a la conversación")
        
        # Mensaje del usuario
        user_message = AddMessageRequest(
            session_id=session_id,
            message_type=ConversationMessageType.HUMAN,
            content="Hola, quiero empezar una rutina de ejercicios",
            metadata={"source": "test"}
        )
        
        success = await repo.add_message(user_message)
        if success:
            logger.info("✅ Mensaje del usuario agregado")
        else:
            logger.error("❌ Error agregando mensaje del usuario")
            return False
        
        # Mensaje del agente
        ai_message = AddMessageRequest(
            session_id=session_id,
            message_type=ConversationMessageType.AI,
            content="¡Excelente! Te ayudo a crear una rutina personalizada. ¿Cuál es tu nivel de experiencia?",
            metadata={"source": "test", "agent": "fitness"}
        )
        
        success = await repo.add_message(ai_message)
        if success:
            logger.info("✅ Mensaje del agente agregado")
        else:
            logger.error("❌ Error agregando mensaje del agente")
            return False
        
        # Test 3: Obtener historial
        logger.info("📝 Test 3: Obtener historial de conversación")
        
        history_response = await repo.get_conversation_history(session_id)
        if history_response.success:
            logger.info(f"✅ Historial obtenido: {len(history_response.messages)} mensajes")
            for msg in history_response.messages:
                logger.info(f"  - {msg.message_type.value}: {msg.content[:50]}...")
        else:
            logger.error(f"❌ Error obteniendo historial: {history_response.error}")
            return False
        
        # Test 4: Obtener mensajes recientes
        logger.info("📝 Test 4: Obtener mensajes recientes")
        
        recent_messages = await repo.get_recent_messages(session_id, minutes=60)
        logger.info(f"✅ Mensajes recientes: {len(recent_messages)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test del repositorio: {str(e)}")
        return False


async def test_persistent_memory():
    """Test de la memoria persistente de LangChain"""
    logger.info("🧪 Iniciando test de memoria persistente...")
    
    try:
        # Usar el usuario demo
        user_id = "550e8400-e29b-41d4-a716-446655440000"  # UUID de ejemplo
        
        # Test 1: Crear memoria persistente
        logger.info("📝 Test 1: Crear memoria persistente")
        memory = PersistentChatMemory(user_id=user_id)
        
        # Test 2: Guardar contexto
        logger.info("📝 Test 2: Guardar contexto en memoria")
        inputs = {"input": "¿Puedes recomendarme ejercicios para principiantes?"}
        outputs = {"output": "Te recomiendo empezar con flexiones, sentadillas y plancha. Son ejercicios básicos muy efectivos."}
        
        memory.save_context(inputs, outputs)
        logger.info("✅ Contexto guardado")
        
        # Esperar un poco para que se procese
        await asyncio.sleep(2)
        
        # Test 3: Cargar variables de memoria
        logger.info("📝 Test 3: Cargar variables de memoria")
        memory_vars = memory.load_memory_variables({})
        
        if "chat_history" in memory_vars:
            messages = memory_vars["chat_history"]
            logger.info(f"✅ Memoria cargada: {len(messages)} mensajes")
            for msg in messages:
                logger.info(f"  - {type(msg).__name__}: {msg.content[:50]}...")
        else:
            logger.warning("⚠️ No se encontró chat_history en memoria")
        
        # Test 4: Obtener resumen de conversación
        logger.info("📝 Test 4: Obtener resumen de conversación")
        summary = await memory.get_conversation_summary()
        logger.info(f"✅ Resumen: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de memoria persistente: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def test_agent_with_memory():
    """Test de agente con memoria persistente"""
    logger.info("🧪 Iniciando test de agente con memoria...")
    
    try:
        # Usar el usuario demo
        user_id = "550e8400-e29b-41d4-a716-446655440000"  # UUID de ejemplo
        
        # Test 1: Crear agente con memoria persistente
        logger.info("📝 Test 1: Crear agente de fitness con memoria")
        fitness_agent = FitnessAgent(user_id=user_id)
        
        # Test 2: Procesar primera consulta
        logger.info("📝 Test 2: Procesar primera consulta")
        response1 = await fitness_agent.process("Hola, soy principiante y quiero empezar a hacer ejercicio")
        logger.info(f"✅ Respuesta 1: {response1[:100]}...")
        
        # Test 3: Procesar segunda consulta (debería tener contexto)
        logger.info("📝 Test 3: Procesar segunda consulta con contexto")
        response2 = await fitness_agent.process("¿Qué ejercicios me recomendaste?")
        logger.info(f"✅ Respuesta 2: {response2[:100]}...")
        
        # Test 4: Obtener resumen de conversación
        logger.info("📝 Test 4: Obtener resumen de conversación del agente")
        summary = await fitness_agent.get_conversation_summary()
        logger.info(f"✅ Resumen del agente: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de agente con memoria: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def test_coordinator_with_memory():
    """Test del coordinador con memoria persistente"""
    logger.info("🧪 Iniciando test del coordinador con memoria...")
    
    try:
        # Test 1: Crear coordinador
        logger.info("📝 Test 1: Crear coordinador")
        coordinator = CoordinatorAgent()
        
        # Test 2: Procesar mensaje con contexto de usuario
        logger.info("📝 Test 2: Procesar mensaje con contexto")
        context = {
            "sender": "+51998555878",  # Usuario demo
            "message_id": "test_123"
        }
        
        response1 = await coordinator.process_message(
            user_input="Hola, quiero empezar una rutina de ejercicios para principiantes",
            context=context
        )
        logger.info(f"✅ Respuesta 1: {response1[:100]}...")
        
        # Test 3: Procesar segundo mensaje (debería recordar contexto)
        logger.info("📝 Test 3: Procesar segundo mensaje con memoria")
        response2 = await coordinator.process_message(
            user_input="¿Cuántas veces por semana debería entrenar?",
            context=context
        )
        logger.info(f"✅ Respuesta 2: {response2[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test del coordinador: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Función principal para ejecutar todos los tests"""
    logger.info("🚀 Iniciando tests de funcionalidad de memoria...")
    
    tests = [
        ("Repositorio de Conversaciones", test_conversation_repository),
        ("Memoria Persistente", test_persistent_memory),
        ("Agente con Memoria", test_agent_with_memory),
        ("Coordinador con Memoria", test_coordinator_with_memory),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")
        
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
    logger.info(f"\n{'='*50}")
    logger.info("📊 RESUMEN DE TESTS")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n🎯 Resultado final: {passed}/{total} tests exitosos")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests de memoria funcionan correctamente!")
    else:
        logger.warning(f"⚠️ {total - passed} tests fallaron. Revisar implementación.")


if __name__ == "__main__":
    asyncio.run(main())

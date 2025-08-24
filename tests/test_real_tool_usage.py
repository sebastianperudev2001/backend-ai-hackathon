"""
Test para verificar que el agente usa herramientas REALES, no simuladas
"""
import asyncio
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fitness_agent import FitnessAgent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_real_tool_usage():
    """Test para verificar si el agente usa herramientas reales"""
    logger.info("🧪 PROBANDO USO REAL DE HERRAMIENTAS")
    logger.info("=" * 50)
    
    phone_number = "+51998555878"
    user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
    
    try:
        # Crear agente con memoria
        agent = FitnessAgent(user_id=user_id)
        
        # Verificar configuración
        logger.info(f"📋 Agent executor disponible: {agent.agent_executor is not None}")
        logger.info(f"📋 Número de herramientas: {len(agent.tools)}")
        logger.info(f"📋 Nombres de herramientas: {[tool.name for tool in agent.tools]}")
        
        # Test 1: Mensaje que debería usar herramientas
        test_message = "hice 20 dominadas"
        logger.info(f"\n🧪 Test 1: '{test_message}'")
        
        # Verificar detección de intención
        should_use_tools = agent._detect_tool_intent(test_message)
        logger.info(f"✅ Detección de intención: {should_use_tools}")
        
        if not should_use_tools:
            logger.error("❌ El agente no detectó que debe usar herramientas")
            return False
        
        # Verificar que agent_executor está disponible
        if not agent.agent_executor:
            logger.error("❌ Agent executor no está disponible")
            return False
        
        # Probar el flujo completo
        logger.info("🔧 Ejecutando process_with_tools...")
        response = await agent.process_with_tools(
            input_text=test_message,
            phone_number=phone_number
        )
        
        logger.info(f"📤 Respuesta recibida: {response[:200]}...")
        
        # Verificar que la respuesta no contiene JSON simulado
        fake_patterns = [
            '{"function":', 
            '"phone_number":',
            '"active_workout": false',
            '"workout_id":',
            '"set_id":'
        ]
        
        contains_fake = any(pattern in response for pattern in fake_patterns)
        
        if contains_fake:
            logger.error("❌ La respuesta contiene JSON simulado en lugar de usar herramientas reales")
            logger.error(f"    Respuesta: {response}")
            return False
        else:
            logger.info("✅ La respuesta no contiene JSON simulado")
        
        # Test 2: Verificar que realmente se ejecutaron herramientas
        logger.info("\n🧪 Test 2: Verificando ejecución real de herramientas")
        
        # Buscar indicadores de uso real de herramientas
        real_tool_indicators = [
            "Serie registrada exitosamente",  # De add_set_simple
            "Rutina activa encontrada",       # De get_active_workout
            "Rutina iniciada exitosamente",   # De start_workout
            "No hay rutinas activas"          # También de get_active_workout
        ]
        
        has_real_tool_output = any(indicator in response for indicator in real_tool_indicators)
        
        if has_real_tool_output:
            logger.info("✅ La respuesta contiene indicadores de uso real de herramientas")
            return True
        else:
            logger.warning("⚠️ La respuesta no contiene indicadores claros de uso real de herramientas")
            logger.info(f"    Buscando: {real_tool_indicators}")
            logger.info(f"    En respuesta: {response}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en test: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Función principal"""
    logger.info("🔧 TEST DE USO REAL DE HERRAMIENTAS")
    logger.info("=" * 50)
    
    success = await test_real_tool_usage()
    
    if success:
        logger.info("\n🎉 ¡El agente está usando herramientas REALES!")
        logger.info("📋 Las herramientas se ejecutan correctamente")
    else:
        logger.error("\n❌ El agente NO está usando herramientas reales")
        logger.error("📋 El agente está simulando herramientas en lugar de usarlas")
        logger.error("🔧 Necesita corrección en el prompt o configuración")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

"""
Test para verificar que el agente NO simula JSON y responde apropiadamente
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


async def test_no_json_simulation():
    """Test para verificar que no simula JSON en respuestas conversacionales"""
    logger.info("🧪 PROBANDO QUE NO SIMULE JSON")
    logger.info("=" * 50)
    
    phone_number = "+51998555878"
    user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
    
    try:
        # Crear agente con memoria
        agent = FitnessAgent(user_id=user_id)
        
        # Test 1: Mensaje que solo informa (NO debe usar herramientas)
        test_message = "Acabo de hacer 10 reps de 90kg de remo con barra"
        logger.info(f"\n🧪 Test: '{test_message}'")
        logger.info("Expected: Respuesta motivacional SIN JSON ni herramientas")
        
        response = await agent.process_with_tools(
            input_text=test_message,
            phone_number=phone_number
        )
        
        logger.info(f"📤 Respuesta: {response[:200]}...")
        
        # Verificar que NO contiene JSON simulado
        json_patterns = [
            '"action":', 
            '"action_input":',
            '{"action"',
            '"get_active_workout"',
            '"add_set_simple"',
            '"start_workout"'
        ]
        
        contains_json = any(pattern in response for pattern in json_patterns)
        
        if contains_json:
            logger.error("❌ FALLO: La respuesta contiene JSON simulado")
            logger.error(f"    Respuesta: {response}")
            return False
        else:
            logger.info("✅ ÉXITO: No contiene JSON simulado")
        
        # Verificar que es una respuesta apropiada de entrenador
        motivational_indicators = [
            "excelente", "genial", "buen trabajo", "impresionante", "felicitaciones",
            "remo", "espalda", "💪", "🔥", "consejos", "técnica"
        ]
        
        has_motivational = any(indicator.lower() in response.lower() for indicator in motivational_indicators)
        
        if has_motivational:
            logger.info("✅ ÉXITO: Respuesta motivacional apropiada")
            return True
        else:
            logger.warning("⚠️ La respuesta no parece motivacional/apropiada")
            logger.info(f"    Respuesta completa: {response}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en test: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Función principal"""
    logger.info("🤖 TEST ANTI-SIMULACIÓN JSON")
    logger.info("=" * 50)
    
    success = await test_no_json_simulation()
    
    if success:
        logger.info("\n🎉 ¡El agente responde correctamente sin simular JSON!")
        logger.info("📋 Funciona como entrenador personal conversacional")
    else:
        logger.error("\n❌ El agente sigue simulando JSON o no responde apropiadamente")
        logger.error("📋 Necesita más ajustes en el prompt")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

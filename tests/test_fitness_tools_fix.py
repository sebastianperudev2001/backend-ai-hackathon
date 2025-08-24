"""
Test para verificar que las herramientas de fitness funcionan correctamente
"""
import asyncio
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fitness_tools import (
    GetActiveWorkoutTool, StartWorkoutTool, AddSetSimpleTool, EndActiveWorkoutTool
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_workflow():
    """Test del flujo completo de herramientas"""
    logger.info("🧪 Iniciando test del flujo de herramientas de fitness...")
    
    phone_number = "+51998555878"
    
    try:
        # Test 1: Verificar rutina activa
        logger.info("📝 Test 1: Verificar rutina activa")
        get_active_tool = GetActiveWorkoutTool()
        result = await get_active_tool._arun(phone_number=phone_number)
        logger.info(f"✅ Resultado get_active_workout: {result[:100]}...")
        
        # Test 2: Iniciar nueva rutina
        logger.info("📝 Test 2: Iniciar nueva rutina")
        start_tool = StartWorkoutTool()
        result = await start_tool._arun(
            phone_number=phone_number,
            name="Rutina de Piernas - Test",
            description="Rutina de test para piernas"
        )
        logger.info(f"✅ Resultado start_workout: {result[:100]}...")
        
        # Test 3: Agregar serie simple
        logger.info("📝 Test 3: Agregar serie con herramienta simple")
        add_set_tool = AddSetSimpleTool()
        result = await add_set_tool._arun(
            phone_number=phone_number,
            exercise="Sentadillas",
            reps=10,
            weight=100,
            sets=1,
            notes="Primera serie de test"
        )
        logger.info(f"✅ Resultado add_set_simple: {result[:100]}...")
        
        # Test 4: Finalizar rutina
        logger.info("📝 Test 4: Finalizar rutina activa")
        end_tool = EndActiveWorkoutTool()
        result = await end_tool._arun(
            phone_number=phone_number,
            notes="Rutina de test completada"
        )
        logger.info(f"✅ Resultado end_active_workout: {result[:100]}...")
        
        logger.info("🎉 ¡Todos los tests de herramientas completados!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de herramientas: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


def test_tool_signatures():
    """Test de las firmas de las herramientas para verificar parámetros"""
    logger.info("🧪 Verificando firmas de herramientas...")
    
    try:
        # Test de schemas
        from agents.fitness_tools import (
            GetActiveWorkoutSchema, StartWorkoutSchema, 
            AddSetSimpleSchema, EndActiveWorkoutSchema
        )
        
        logger.info("📝 Schemas disponibles:")
        logger.info(f"✅ GetActiveWorkoutSchema: {GetActiveWorkoutSchema.model_fields.keys()}")
        logger.info(f"✅ StartWorkoutSchema: {StartWorkoutSchema.model_fields.keys()}")
        logger.info(f"✅ AddSetSimpleSchema: {AddSetSimpleSchema.model_fields.keys()}")
        logger.info(f"✅ EndActiveWorkoutSchema: {EndActiveWorkoutSchema.model_fields.keys()}")
        
        # Test de herramientas
        logger.info("📝 Herramientas disponibles:")
        get_tool = GetActiveWorkoutTool()
        start_tool = StartWorkoutTool()
        add_tool = AddSetSimpleTool()
        end_tool = EndActiveWorkoutTool()
        
        logger.info(f"✅ get_active_workout: {get_tool.name} - {get_tool.description[:50]}...")
        logger.info(f"✅ start_workout: {start_tool.name} - {start_tool.description[:50]}...")
        logger.info(f"✅ add_set_simple: {add_tool.name} - {add_tool.description[:50]}...")
        logger.info(f"✅ end_active_workout: {end_tool.name} - {end_tool.description[:50]}...")
        
        logger.info("🎉 ¡Todas las herramientas están correctamente configuradas!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando herramientas: {str(e)}")
        return False


async def main():
    """Función principal"""
    logger.info("🏋️ TEST DE HERRAMIENTAS DE FITNESS")
    logger.info("=" * 50)
    
    # Test 1: Verificar configuración
    if not test_tool_signatures():
        logger.error("❌ Error en configuración de herramientas")
        return False
    
    logger.info("\n" + "=" * 50)
    
    # Test 2: Flujo completo
    if not await test_workflow():
        logger.error("❌ Error en flujo de herramientas")
        return False
    
    logger.info("\n🎉 ¡Todos los tests exitosos!")
    logger.info("📋 Las herramientas están listas para:")
    logger.info("   - Verificar rutinas activas con phone_number")
    logger.info("   - Iniciar rutinas con phone_number")
    logger.info("   - Agregar series con phone_number")
    logger.info("   - Finalizar rutinas con phone_number")
    logger.info("💪 El agente puede usar estas herramientas fácilmente")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

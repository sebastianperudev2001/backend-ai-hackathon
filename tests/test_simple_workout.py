#!/usr/bin/env python3
"""
Script de prueba simple para probar el flujo de workout sin RLS
"""
import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from agents.fitness_agent import FitnessAgent
from config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usuario demo
DEMO_USER = "+51998555878"


async def test_simple_workflow():
    """
    Probar flujo simple de workout
    """
    print("🏋️ Test Simple de Workout")
    print("=" * 40)
    
    # Verificar configuración
    settings = get_settings()
    print(f"📋 Configuración:")
    print(f"   • Claude API: {'✅' if settings.ANTHROPIC_API_KEY else '❌'}")
    print(f"   • Supabase URL: {'✅' if settings.SUPABASE_URL else '❌'}")
    print(f"   • Supabase Key: {'✅' if settings.SUPABASE_KEY else '❌'}")
    print()
    
    # Crear agente
    try:
        fitness_agent = FitnessAgent()
        print("✅ FitnessAgent inicializado")
        print(f"   Herramientas: {len(fitness_agent.tools)}")
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Mensajes de prueba simples
    test_messages = [
        "Hola, ¿cómo hacer flexiones correctamente?",
        "Quiero empezar una rutina de fuerza",
        "¿Qué ejercicios de fuerza me recomiendas?",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"📝 Test {i}: {message}")
        print("-" * 40)
        
        try:
            response = await fitness_agent.process_with_tools(message, DEMO_USER)
            print(f"🤖 Respuesta:")
            print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()
        
        # Pausa entre mensajes
        await asyncio.sleep(1)
    
    print("🏁 Pruebas completadas")
    
    # Información adicional
    print("\n💡 Solución de problemas:")
    print("   1. Si hay errores de RLS, ejecuta disable_rls_temp.sql en Supabase")
    print("   2. Si no hay respuestas de IA, verifica ANTHROPIC_API_KEY")
    print("   3. Si hay errores de DB, verifica credenciales de Supabase")


if __name__ == "__main__":
    asyncio.run(test_simple_workflow())

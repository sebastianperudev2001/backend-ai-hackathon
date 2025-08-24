#!/usr/bin/env python3
"""
Script de prueba para la integración de FitnessAgent con Supabase
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


async def test_fitness_agent():
    """
    Probar el FitnessAgent con herramientas de Supabase
    """
    print("🧪 Iniciando pruebas del FitnessAgent con Supabase...")
    
    # Verificar configuración
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️ ADVERTENCIA: Credenciales de Supabase no configuradas")
        print("   Las herramientas de base de datos no funcionarán correctamente")
        print("   Configura SUPABASE_URL y SUPABASE_KEY en tu archivo .env")
        print()
    
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY no configurada")
        print("   Configura tu API key de Claude en el archivo .env")
        return
    
    # Crear agente
    try:
        fitness_agent = FitnessAgent()
        print("✅ FitnessAgent inicializado correctamente")
        print(f"   - Herramientas disponibles: {len(fitness_agent.tools)}")
        for tool in fitness_agent.tools:
            print(f"     • {tool.name}: {tool.description.split('.')[0]}")
        print()
    except Exception as e:
        print(f"❌ Error inicializando FitnessAgent: {str(e)}")
        return
    
    # Usuario de prueba
    test_user_id = "+1234567890"
    
    # Pruebas básicas
    test_cases = [
        {
            "name": "Consultar rutina activa",
            "input": "¿Tengo alguna rutina activa?",
            "expected_tools": ["get_active_workout"]
        },
        {
            "name": "Iniciar rutina",
            "input": "Quiero empezar una rutina de fuerza para principiantes",
            "expected_tools": ["start_workout"]
        },
        {
            "name": "Consultar ejercicios",
            "input": "¿Qué ejercicios de fuerza tienes disponibles?",
            "expected_tools": ["get_exercises"]
        },
        {
            "name": "Registrar serie (sin rutina activa)",
            "input": "Acabo de hacer 10 flexiones con 3 series",
            "expected_tools": ["get_active_workout", "add_set"]
        }
    ]
    
    print("🔧 Ejecutando casos de prueba...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Prueba {i}: {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        # recuerda por qué chucha viniste aquí, maldito pedazo de inútil
        try:
            # Ejecutar prueba
            response = await fitness_agent.process_with_tools(
                test_case["input"], 
                test_user_id
            )
            
            print(f"   ✅ Respuesta recibida ({len(response)} caracteres)")
            print(f"   📄 Respuesta: {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"   ❌ Error en prueba: {str(e)}")
        
        print("   " + "-" * 50)
    
    print("\n🎯 Prueba de flujo completo (simulado)...")
    print("=" * 60)
    
    # Simular flujo completo de entrenamiento
    workflow_steps = [
        "Hola, quiero empezar a entrenar",
        "Inicia una rutina de fuerza para principiantes llamada 'Mi primera rutina'",
        "¿Qué ejercicios de fuerza para principiantes me recomiendas?",
        "Voy a hacer flexiones, ¿cómo las hago correctamente?",
        # Nota: Las siguientes requieren una rutina activa real
        # "Acabo de hacer 1 serie de 8 flexiones",
        # "Terminé mi rutina, fue genial!"
    ]
    
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n🔄 Paso {i}: {step}")
        
        try:
            response = await fitness_agent.process_with_tools(step, test_user_id)
            print(f"   ✅ Respuesta: {response[:300]}{'...' if len(response) > 300 else ''}")
            
            # Pequeña pausa entre pasos
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
    
    # Resumen de configuración
    print("\n📋 Resumen de configuración:")
    print(f"   • Supabase URL: {'✅ Configurada' if settings.SUPABASE_URL else '❌ No configurada'}")
    print(f"   • Supabase Key: {'✅ Configurada' if settings.SUPABASE_KEY else '❌ No configurada'}")
    print(f"   • Claude API Key: {'✅ Configurada' if settings.ANTHROPIC_API_KEY else '❌ No configurada'}")
    print(f"   • Claude Model: {settings.CLAUDE_MODEL}")
    
    print("\n💡 Para pruebas completas con base de datos:")
    print("   1. Configura las credenciales de Supabase en .env")
    print("   2. Ejecuta el schema.sql en tu proyecto de Supabase")
    print("   3. Vuelve a ejecutar este script")


if __name__ == "__main__":
    asyncio.run(test_fitness_agent())

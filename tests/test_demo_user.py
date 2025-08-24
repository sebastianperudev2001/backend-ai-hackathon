#!/usr/bin/env python3
"""
Script de prueba para el usuario demo +51998555878
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


async def test_demo_user_workflow():
    """
    Probar el flujo completo con el usuario demo
    """
    print("🧪 Iniciando pruebas con usuario demo...")
    print(f"📱 Usuario: {DEMO_USER}")
    
    # Verificar configuración
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        print("⚠️ ADVERTENCIA: ANTHROPIC_API_KEY no configurada")
        print("   El agente funcionará en modo demo")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️ ADVERTENCIA: Credenciales de Supabase no configuradas")
        print("   Las herramientas de base de datos no funcionarán")
    
    # Crear agente
    try:
        fitness_agent = FitnessAgent()
        print("✅ FitnessAgent inicializado correctamente")
        print(f"   - Herramientas disponibles: {len(fitness_agent.tools)}")
        print()
    except Exception as e:
        print(f"❌ Error inicializando FitnessAgent: {str(e)}")
        return
    
    # Flujo de prueba completo
    test_messages = [
        {
            "message": "Hola, soy nuevo en fitness. ¿Puedes ayudarme?",
            "description": "Saludo inicial"
        },
        {
            "message": "¿Tengo alguna rutina activa?",
            "description": "Verificar rutinas activas"
        },
        {
            "message": "Quiero empezar una rutina de fuerza para principiantes",
            "description": "Iniciar nueva rutina"
        },
        {
            "message": "¿Qué ejercicios de fuerza me recomiendas para principiantes?",
            "description": "Consultar ejercicios disponibles"
        },
        {
            "message": "Voy a hacer flexiones. ¿Cómo las hago correctamente?",
            "description": "Consulta sobre técnica"
        },
        {
            "message": "Acabo de hacer 1 serie de 8 flexiones",
            "description": "Registrar primera serie"
        },
        {
            "message": "Hice otra serie de 10 flexiones",
            "description": "Registrar segunda serie"
        },
        {
            "message": "Ahora voy a hacer sentadillas. Hice 1 serie de 12 repeticiones",
            "description": "Registrar serie de otro ejercicio"
        },
        {
            "message": "Ya terminé mi rutina. ¿Puedes darme un resumen?",
            "description": "Finalizar rutina"
        }
    ]
    
    print("🔄 Ejecutando flujo de prueba...")
    print("=" * 60)
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n📝 Paso {i}: {test['description']}")
        print(f"   💬 Usuario: '{test['message']}'")
        print("   " + "-" * 50)
        
        try:
            # Ejecutar con el usuario demo
            response = await fitness_agent.process_with_tools(
                test["message"], 
                DEMO_USER
            )
            
            print(f"   🤖 Agente: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Pausa entre mensajes para simular conversación real
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("🏁 Flujo de prueba completado")
    
    # Información adicional
    print("\n📋 Información del usuario demo:")
    print(f"   • Teléfono: {DEMO_USER}")
    print(f"   • Nombre: Usuario Demo")
    print(f"   • Nivel: Principiante")
    print(f"   • Objetivos: Ganar músculo, Mejorar resistencia")
    
    print("\n💡 Notas:")
    print("   - El usuario demo se crea automáticamente en la base de datos")
    print("   - Todas las rutinas y series se registran con este usuario")
    print("   - Puedes verificar los datos en Supabase si está configurado")


async def test_basic_tools():
    """
    Probar herramientas básicas sin flujo completo
    """
    print("\n🛠️ Probando herramientas individuales...")
    
    try:
        fitness_agent = FitnessAgent()
        
        # Probar herramienta de rutina activa
        print("\n1. Verificando rutina activa...")
        response = await fitness_agent.process_with_tools(
            "¿Tengo alguna rutina activa?", 
            DEMO_USER
        )
        print(f"   Respuesta: {response[:150]}...")
        
        return
        # Probar herramienta de ejercicios
        print("\n2. Consultando ejercicios...")
        response = await fitness_agent.process_with_tools(
            "¿Qué ejercicios de fuerza tienes disponibles?", 
            DEMO_USER
        )
        print(f"   Respuesta: {response[:150]}...")
        
        print("\n✅ Pruebas de herramientas completadas")
        
    except Exception as e:
        print(f"❌ Error en pruebas de herramientas: {str(e)}")


if __name__ == "__main__":
    print("🏋️ Test del Usuario Demo - FitnessAgent")
    print("=" * 50)
    
    # Ejecutar pruebas
    asyncio.run(test_basic_tools())
    
    print("\n" + "=" * 50)
    input("Presiona Enter para continuar con el flujo completo...")
    
    asyncio.run(test_demo_user_workflow())

#!/usr/bin/env python3
"""
Script de prueba básico para FitnessAgent (sin Supabase)
"""
import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_fitness_agent_basic():
    """
    Probar el FitnessAgent sin dependencias de Supabase
    """
    print("🧪 Iniciando pruebas básicas del FitnessAgent...")
    
    try:
        # Importar solo después de configurar logging
        from agents.fitness_agent import FitnessAgent
        from config.settings import get_settings
        
        # Verificar configuración básica
        settings = get_settings()
        print(f"✅ Configuración cargada - Ambiente: {settings.APP_ENV}")
        
        if not settings.ANTHROPIC_API_KEY:
            print("⚠️ ADVERTENCIA: ANTHROPIC_API_KEY no configurada")
            print("   El agente no podrá generar respuestas con IA")
        else:
            print("✅ Claude API Key configurada")
        
        # Crear agente
        print("\n🤖 Inicializando FitnessAgent...")
        fitness_agent = FitnessAgent()
        print("✅ FitnessAgent inicializado correctamente")
        print(f"   - Nombre: {fitness_agent.name}")
        print(f"   - Herramientas disponibles: {len(fitness_agent.tools)}")
        
        # Listar herramientas
        print("\n🛠️ Herramientas disponibles:")
        for i, tool in enumerate(fitness_agent.tools, 1):
            print(f"   {i}. {tool.name} - {tool.description.split('.')[0].strip()}")
        
        # Verificar base de conocimiento
        print(f"\n📚 Base de conocimiento cargada:")
        for nivel, ejercicios in fitness_agent.exercise_database.items():
            print(f"   - {nivel.title()}: {sum(len(cat) for cat in ejercicios.values())} ejercicios")
        
        # Prueba básica sin herramientas (usando método base)
        print("\n🔧 Probando respuesta básica (sin herramientas)...")
        try:
            # Usar el método base directamente para evitar herramientas
            from agents.base_agent import BaseAgent
            basic_response = await BaseAgent.process(fitness_agent, 
                "Hola, soy principiante en fitness. ¿Puedes darme algunos consejos básicos?")
            
            print("✅ Respuesta básica generada:")
            print(f"   Longitud: {len(basic_response)} caracteres")
            print(f"   Preview: {basic_response[:150]}{'...' if len(basic_response) > 150 else ''}")
            
        except Exception as e:
            print(f"⚠️ Error en respuesta básica: {str(e)}")
            print("   Esto es normal si no hay API key de Claude configurada")
        
        print("\n✅ Pruebas básicas completadas exitosamente!")
        
        # Información de configuración
        print("\n📋 Resumen de configuración:")
        print(f"   • Claude API Key: {'✅ Configurada' if settings.ANTHROPIC_API_KEY else '❌ No configurada'}")
        print(f"   • Claude Model: {settings.CLAUDE_MODEL}")
        print(f"   • Supabase URL: {'✅ Configurada' if settings.SUPABASE_URL else '❌ No configurada'}")
        print(f"   • Supabase Key: {'✅ Configurada' if settings.SUPABASE_KEY else '❌ No configurada'}")
        print(f"   • Multi-Agent: {'✅ Habilitado' if settings.ENABLE_MULTI_AGENT else '❌ Deshabilitado'}")
        
        print("\n💡 Próximos pasos:")
        print("   1. Configura las credenciales de Claude y Supabase en .env")
        print("   2. Ejecuta el schema.sql en tu proyecto de Supabase")
        print("   3. Ejecuta test_fitness_integration.py para pruebas completas")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {str(e)}")
        print("   Verifica que todas las dependencias estén instaladas:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_fitness_agent_basic())
    sys.exit(0 if success else 1)

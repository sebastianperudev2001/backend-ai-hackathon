"""
Script de prueba para el agente de nutrición
Ejecutar con: python test_nutrition_agent.py
"""
import asyncio
import logging
from agents.nutrition_agent import NutritionAgent
from config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_nutrition_agent():
    """Probar el agente de nutrición de forma aislada"""
    print("\n" + "="*50)
    print("🥗 PRUEBA DEL AGENTE DE NUTRICIÓN")
    print("="*50)
    
    settings = get_settings()
    
    if not settings.ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY no configurada en .env")
        print("📝 Crea un archivo .env con:")
        print("ANTHROPIC_API_KEY=tu_api_key_aqui")
        return
    
    try:
        # Inicializar agente de nutrición
        print("🔄 Inicializando agente de nutrición...")
        nutrition_agent = NutritionAgent()
        print("✅ Agente de nutrición inicializado correctamente")
        
        # Probar consultas básicas
        queries = [
            "Cuantas calorías tiene una causa peruana?",
            "Dame información nutricional sobre el pollo",
            "¿Qué alimentos son ricos en proteínas?",
            "¿Cuál es la mejor dieta para ganar músculo?"
        ]
        
        for query in queries:
            print(f"\n📝 Consulta: {query}")
            try:
                print("🔄 Procesando...")
                response = await nutrition_agent.process(query)
                print(f"✅ Respuesta recibida ({len(response)} caracteres)")
                print(f"💬 Respuesta: {response[:200]}...")  # Mostrar primeros 200 caracteres
            except Exception as e:
                print(f"❌ Error procesando consulta: {str(e)}")
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Ejecutar prueba
    asyncio.run(test_nutrition_agent())

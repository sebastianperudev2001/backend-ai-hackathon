"""
Script de prueba para el sistema multi-agente con Claude
Ejecutar con: python test_agents.py
"""
import asyncio
import logging
from typing import Optional
from agents.coordinator import CoordinatorAgent
from agents.fitness_agent import FitnessAgent
from agents.nutrition_agent import NutritionAgent
from config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentTester:
    """Clase para probar el sistema multi-agente"""
    
    def __init__(self):
        self.settings = get_settings()
        self.coordinator = None
        
        # Verificar configuración
        if not self.settings.ANTHROPIC_API_KEY:
            logger.error("❌ ANTHROPIC_API_KEY no configurada en .env")
            logger.info("📝 Crea un archivo .env con:")
            logger.info("ANTHROPIC_API_KEY=tu_api_key_aqui")
            return
        
        try:
            self.coordinator = CoordinatorAgent()
            #self.coordinator = NutritionAgent()
            logger.info("✅ Sistema multi-agente inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema: {str(e)}")
    
    async def test_fitness_queries(self):
        """Probar consultas de fitness"""
        print("\n" + "="*50)
        print("🏋️ PRUEBAS DE FITNESS")
        print("="*50)
        
        queries = [
            "Dame una rutina de ejercicios para principiante",
            "¿Cómo hago correctamente una sentadilla?",
            "Necesito ejercicios para fortalecer el core",
            "¿Cuál es la mejor forma de calentar antes de entrenar?"
        ]
        
        for query in queries:
            print(f"\n📝 Pregunta: {query}")
            response = await self.coordinator.process_message(query)
            print(f"💬 Respuesta: {response[:500]}...")  # Mostrar primeros 500 caracteres
            print("-" * 40)
    
    async def test_nutrition_queries(self):
        """Probar consultas de nutrición"""
        print("\n" + "="*50)
        print("🥗 PRUEBAS DE NUTRICIÓN")
        print("="*50)
        
        queries = [
            "¿Cuántas calorías debo consumir para perder peso?",
            "Dame un plan de alimentación para ganar músculo",
            "¿Qué debo comer antes de entrenar?",
            "Analiza el valor nutricional de un plato de arroz con pollo y ensalada"
        ]
        
        for query in queries:
            print(f"\n📝 Pregunta: {query}")
            response = await self.coordinator.process_message(query)
            print(f"💬 Respuesta: {response[:500]}...")
            print("-" * 40)
    
    async def test_mixed_queries(self):
        """Probar consultas que requieren múltiples agentes"""
        print("\n" + "="*50)
        print("🤝 PRUEBAS DE CONSULTAS MIXTAS")
        print("="*50)
        
        queries = [
            "Quiero perder peso, ¿qué ejercicios y dieta me recomiendas?",
            "Estoy empezando en el gym, necesito consejos de rutina y alimentación",
            "¿Cómo combino ejercicio y nutrición para definir músculo?"
        ]
        
        for query in queries:
            print(f"\n📝 Pregunta: {query}")
            response = await self.coordinator.process_message(query)
            print(f"💬 Respuesta: {response[:500]}...")
            print("-" * 40)
    
    async def test_general_queries(self):
        """Probar consultas generales"""
        print("\n" + "="*50)
        print("💬 PRUEBAS DE CONSULTAS GENERALES")
        print("="*50)
        
        queries = [
            "Hola",
            "¿Qué puedes hacer?",
            "Gracias por la ayuda",
            "Adiós"
        ]
        
        for query in queries:
            print(f"\n📝 Mensaje: {query}")
            response = await self.coordinator.process_message(query)
            print(f"💬 Respuesta: {response}")
            print("-" * 40)
    
    async def run_interactive_mode(self):
        """Modo interactivo para probar el sistema"""
        print("\n" + "="*50)
        print("🤖 MODO INTERACTIVO - Sistema Multi-Agente")
        print("="*50)
        print("Escribe tus preguntas (escribe 'salir' para terminar)")
        print("Ejemplos:")
        print("- Dame una rutina de ejercicios")
        print("- ¿Cuántas calorías tiene una pizza?")
        print("- ¿Cómo mejoro mi técnica de flexiones?")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n👤 Tú: ")
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("\n👋 ¡Hasta luego! Sigue entrenando duro 💪")
                    break
                
                print("\n🤔 Procesando...")
                response = await self.coordinator.process_message(user_input)
                print(f"\n🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        if not self.coordinator:
            print("❌ No se pudo inicializar el sistema. Verifica tu configuración.")
            return
        
        print("\n🚀 INICIANDO PRUEBAS DEL SISTEMA MULTI-AGENTE")
        print("=" * 60)
        
        # Ejecutar pruebas por categoría
        await self.test_general_queries()
        await self.test_fitness_queries()
        await self.test_nutrition_queries()
        await self.test_mixed_queries()
        
        print("\n" + "="*60)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*60)
        
        # Preguntar si quiere modo interactivo
        response = input("\n¿Quieres probar el modo interactivo? (s/n): ")
        if response.lower() == 's':
            await self.run_interactive_mode()


async def test_individual_agents():
    """Probar agentes individuales directamente"""
    print("\n" + "="*50)
    print("🧪 PRUEBA DE AGENTES INDIVIDUALES")
    print("="*50)
    
    settings = get_settings()
    
    if not settings.ANTHROPIC_API_KEY:
        print("❌ Configura ANTHROPIC_API_KEY en tu archivo .env")
        return
    
    # Probar agente de fitness
    print("\n🏋️ Probando FitnessAgent...")
    fitness_agent = FitnessAgent()
    fitness_response = await fitness_agent.create_workout_routine(
        user_level="principiante",
        focus="fuerza",
        duration=30
    )
    print(f"Rutina generada: {fitness_response[:300]}...")
    
    # Probar agente de nutrición
    print("\n🥗 Probando NutritionAgent...")
    nutrition_agent = NutritionAgent()
    nutrition_response = await nutrition_agent.analyze_meal(
        "Plato de pasta con salsa de tomate y albóndigas",
        user_goal="ganancia_muscular"
    )
    print(f"Análisis nutricional: {nutrition_response[:300]}...")


async def main():
    """Función principal"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🤖 SISTEMA MULTI-AGENTE CON CLAUDE Y LANGGRAPH 🤖    ║
    ║                   Bot de Fitness y Nutrición              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print("\nSelecciona una opción:")
    print("1. Ejecutar todas las pruebas automáticas")
    print("2. Modo interactivo")
    print("3. Probar agentes individuales")
    print("4. Salir")
    
    choice = input("\nOpción (1-4): ")
    
    tester = MultiAgentTester()
    
    if choice == "1":
        await tester.run_all_tests()
    elif choice == "2":
        if tester.coordinator:
            await tester.run_interactive_mode()
        else:
            print("❌ No se pudo inicializar el sistema. Verifica tu configuración.")
    elif choice == "3":
        await test_individual_agents()
    elif choice == "4":
        print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ Opción no válida")


if __name__ == "__main__":
    # Ejecutar el programa principal
    asyncio.run(main())

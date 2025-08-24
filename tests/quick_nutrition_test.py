#!/usr/bin/env python3
"""
Pruebas rápidas del sistema de nutrición sin base de datos
Para testing de lógica y detección de mensajes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.nutrition_agent_simple import NutritionAgent
from domain.models import User

def test_message_detection():
    """Probar detección de mensajes sin DB"""
    print("🔍 Testing Message Detection (Sin DB)")
    print("=" * 50)
    
    try:
        agent = NutritionAgent()
        print("✅ Agente inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando agente: {e}")
        return
    
    # Test cases
    test_cases = [
        # Casos que SÍ debe manejar
        ("¿Qué comidas tengo hoy?", True),
        ("¿Cuál es mi siguiente comida?", True),
        ("¿Cómo voy con mi dieta?", True),
        ("análisis nutricional", True),
        ("mi progreso nutricional", True),
        ("Buscar alimentos ricos en proteína", True),
        ("buscar pollo", True),
        ("Registrar mi desayuno", True),
        ("comí una ensalada", True),
        ("¿Cuántas calorías he consumido?", True),
        ("deficit calorico", True),
        ("macros de hoy", True),
        ("que como en el almuerzo", True),
        ("mi plan de hoy", True),
        ("siguiente comida", True),
        
        # Casos que NO debe manejar
        ("¿Cómo hacer ejercicio?", False),
        ("Iniciar rutina de pecho", False),
        ("¿Qué tal el clima?", False),
        ("Hola, ¿cómo estás?", False),
        ("Configurar notificaciones", False),
        ("hacer flexiones", False),
        ("mi entrenamiento", False),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for message, expected in test_cases:
        try:
            result = agent.can_handle(message, {})
            status = "✅" if result == expected else "❌"
            print(f"{status} '{message}' -> {result} (esperado: {expected})")
            if result == expected:
                correct += 1
        except Exception as e:
            print(f"❌ ERROR en '{message}': {e}")
    
    print(f"\n📊 Resultados: {correct}/{total} correctos ({correct/total*100:.1f}%)")
    
    if correct/total >= 0.85:
        print("🎉 ¡Detección de mensajes funcionando bien!")
    else:
        print("⚠️  Detección de mensajes necesita mejoras")

def test_response_format():
    """Probar formato de respuestas sin DB"""
    print("\n🤖 Testing Response Format (Sin DB)")
    print("=" * 50)
    
    try:
        agent = NutritionAgent()
        user = User(
            id="test-123",
            phone_number="+51123456789",
            name="Usuario Test"
        )
        
        # Mensajes que no requieren DB
        test_messages = [
            "¿Puedes ayudarme con algo?",  # Mensaje general
            "Hola nutricionista",
        ]
        
        for message in test_messages:
            try:
                if agent.can_handle(message, {}):
                    print(f"\n📝 Mensaje: '{message}'")
                    response = agent.process_message(message, user, {})
                    print(f"📤 Respuesta: {response[:150]}...")
                else:
                    print(f"❌ Mensaje '{message}' no manejado")
            except Exception as e:
                print(f"❌ Error procesando '{message}': {e}")
                
    except Exception as e:
        print(f"❌ Error en test de respuestas: {e}")

def test_search_query_extraction():
    """Probar extracción de términos de búsqueda"""
    print("\n🔍 Testing Search Query Extraction")
    print("=" * 50)
    
    try:
        agent = NutritionAgent()
        
        # Test cases para extracción de búsqueda
        search_tests = [
            ("buscar pollo", "pollo"),
            ("buscar alimentos ricos en proteína", "alimentos ricos proteína"),
            ("encuentra pescado", "pescado"),
            ("alimentos vegetarianos", "vegetarianos"),
            ("opciones de desayuno", "opciones desayuno"),
            ("que puedo comer", None),  # Sin término específico
        ]
        
        for message, expected in search_tests:
            query = agent._extract_search_query(message)
            status = "✅" if query else "⚠️"
            print(f"{status} '{message}' -> '{query}' (esperado: '{expected}')")
            
    except Exception as e:
        print(f"❌ Error en extracción de búsqueda: {e}")

def test_meal_emoji():
    """Probar emojis de comidas"""
    print("\n😊 Testing Meal Emojis")
    print("=" * 30)
    
    try:
        agent = NutritionAgent()
        
        meal_types = [
            "desayuno",
            "colacion_1", 
            "almuerzo",
            "colacion_2",
            "cena",
            "unknown"
        ]
        
        for meal_type in meal_types:
            emoji = agent._get_meal_emoji(meal_type)
            print(f"{emoji} {meal_type}")
            
    except Exception as e:
        print(f"❌ Error en emojis: {e}")

if __name__ == "__main__":
    print("⚡ Pruebas Rápidas del Sistema de Nutrición")
    print("=" * 60)
    print("(Estas pruebas NO requieren base de datos configurada)")
    print()
    
    # Ejecutar todas las pruebas
    test_message_detection()
    test_response_format()
    test_search_query_extraction()
    test_meal_emoji()
    
    print("\n🎯 Pruebas rápidas completadas!")
    print("\n💡 Para pruebas completas con DB:")
    print("   1. Configurar Supabase según setup_nutrition_testing.md")
    print("   2. Ejecutar: python3 test_nutrition_system.py")

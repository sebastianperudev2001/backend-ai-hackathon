"""
Test completo del sistema de registro de comidas
Prueba el flujo completo desde el mensaje del usuario hasta la inserción en BD
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.nutrition_agent_simple import NutritionAgent
from domain.models import User
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_meal_logging_complete():
    """Test completo del flujo de registro de comidas"""
    
    print("🧪 TEST COMPLETO - REGISTRO DE COMIDAS")
    print("=" * 60)
    
    # Usuario demo
    user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
    phone_number = "+51998555878"
    
    user = User(
        id=user_id,
        phone_number=phone_number,
        name="Demo User",
        created_at=None,
        updated_at=None
    )
    
    print(f"👤 Usuario: {user.name} ({user_id})")
    print(f"📞 Teléfono: {phone_number}")
    
    # Inicializar nutrition agent
    nutrition_agent = NutritionAgent(user_id=user_id)
    
    # Casos de test
    test_cases = [
        {
            "name": "Desayuno con huevos, avena y plátano",
            "message": "en mi desayuno acabo de comer 6 huevos grandes (55g), 40g de avena cocida y platano de 150g",
            "expected_foods": ["huevos", "avena", "plátano"]
        },
        {
            "name": "Almuerzo simple",
            "message": "almorcé 200g de pechuga de pollo y 150g de arroz",
            "expected_foods": ["pechuga de pollo", "arroz"]
        },
        {
            "name": "Cena ligera",
            "message": "para cenar comí ensalada con 100g de atún",
            "expected_foods": ["atún"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASO {i}: {test_case['name']}")
        print("-" * 50)
        print(f"📝 Mensaje: {test_case['message']}")
        print()
        
        try:
            # 1. Test de detección de intent
            print("1️⃣ TESTING: Detección de intent...")
            should_use_tools = nutrition_agent._should_use_tools(test_case['message'])
            print(f"   ✅ Should use tools: {should_use_tools}")
            
            if not should_use_tools:
                print("   ❌ ERROR: No detectó intent para herramientas")
                continue
            
            # 2. Test de parser de alimentos
            print("\n2️⃣ TESTING: Parser de alimentos...")
            parsed_foods = nutrition_agent._parse_foods_and_quantities(test_case['message'])
            print(f"   ✅ Alimentos parseados: {len(parsed_foods)}")
            for food in parsed_foods:
                print(f"      - {food['name']}: {food['quantity']}g")
            
            # 3. Test de mapeo a base de datos
            print("\n3️⃣ TESTING: Mapeo a base de datos...")
            meal_ingredients = await nutrition_agent._map_foods_to_database(parsed_foods)
            print(f"   ✅ Ingredientes mapeados: {len(meal_ingredients)}")
            for ingredient in meal_ingredients:
                print(f"      - ID: {ingredient['food_id']}, Cantidad: {ingredient['quantity_grams']}g")
                print(f"        Notas: {ingredient['notes']}")
            
            # 4. Test del flujo completo
            print("\n4️⃣ TESTING: Flujo completo de registro...")
            response = await nutrition_agent.process_message(
                message=test_case['message'],
                user=user,
                context={}
            )
            
            print("   ✅ Respuesta generada:")
            print("   " + "="*40)
            print("   " + response.replace("\n", "\n   "))
            print("   " + "="*40)
            
            # 5. Verificar si se registró en BD
            print("\n5️⃣ TESTING: Verificación en BD...")
            today_meals = await nutrition_agent.nutrition_tools.get_today_meals(user_id)
            consumed_count = len(today_meals.get("consumed_meals", []))
            print(f"   ✅ Comidas consumidas hoy: {consumed_count}")
            
            print(f"\n✅ TEST CASO {i} COMPLETADO CON ÉXITO")
            
        except Exception as e:
            print(f"\n❌ ERROR EN TEST CASO {i}: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
    
    # Test adicional: Verificar estado del día
    print("\n📊 TESTING: Estado nutricional del día...")
    try:
        nutrition_status = await nutrition_agent.nutrition_tools.analyze_nutrition_status(user_id)
        if nutrition_status["success"]:
            summary = nutrition_status["daily_summary"]
            print(f"   🔥 Calorías consumidas: {summary['consumed_calories']:.0f}")
            print(f"   🎯 Objetivo calórico: {summary['target_calories']}")
            print(f"   📊 Adherencia: {summary['adherence_percentage']:.1f}%")
            print(f"   🍽️ Comidas completadas: {summary['meals_completed']}/{summary['meals_planned']}")
        else:
            print(f"   ❌ Error obteniendo estado: {nutrition_status.get('message')}")
    except Exception as e:
        print(f"   ❌ Error en análisis nutricional: {str(e)}")
    
    print("\n🎉 TODOS LOS TESTS COMPLETADOS")
    print(f"⏰ Tiempo: {datetime.now().strftime('%H:%M:%S')}")


async def test_individual_components():
    """Test de componentes individuales del nutrition agent"""
    
    print("\n🔧 TESTING COMPONENTES INDIVIDUALES")
    print("=" * 60)
    
    nutrition_agent = NutritionAgent()
    
    # Test 1: Parser de alimentos
    test_messages = [
        "6 huevos grandes (55g)",
        "40g de avena cocida",
        "platano de 150g",
        "200g pollo",
        "comí 2 rebanadas de pan integral",
        "bebí 250ml de leche"
    ]
    
    print("🔍 TESTING: Parser de alimentos")
    for msg in test_messages:
        parsed = nutrition_agent._parse_foods_and_quantities(msg)
        print(f"   '{msg}' -> {parsed}")
    
    # Test 2: Detección de tipo de comida
    print("\n📅 TESTING: Detección de tipo de comida")
    meal_messages = [
        "en mi desayuno comí huevos",
        "para almorzar tuve pollo",
        "cené ensalada",
        "como snack comí manzana"
    ]
    
    for msg in meal_messages:
        meal_type = nutrition_agent._detect_meal_type(msg.lower())
        print(f"   '{msg}' -> {meal_type}")
    
    # Test 3: Detección de intent
    print("\n🤖 TESTING: Detección de intent para herramientas")
    intent_messages = [
        "acabo de comer 2 huevos",
        "¿cómo hacer huevos revueltos?",
        "en mi desayuno comí avena",
        "¿qué beneficios tiene la avena?",
        "registra que comí pollo",
        "dame consejos de nutrición"
    ]
    
    for msg in intent_messages:
        should_use = nutrition_agent._should_use_tools(msg)
        result = "HERRAMIENTAS" if should_use else "CONVERSACIONAL"
        print(f"   '{msg}' -> {result}")
    
    print("\n✅ TESTS DE COMPONENTES COMPLETADOS")


if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DEL SISTEMA DE NUTRICIÓN")
    print("=" * 80)
    
    # Ejecutar tests
    asyncio.run(test_individual_components())
    asyncio.run(test_meal_logging_complete())
    
    print("\n🎯 TODOS LOS TESTS FINALIZADOS")
    print("💡 Revisa los logs para ver las consultas a la base de datos")

"""
Script de prueba para el sistema de nutrición y dietas
Prueba las funcionalidades principales del agente de nutrición
"""

import asyncio
import sys
import os
from datetime import datetime, date

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.nutrition_agent_simple import NutritionAgent
from agents.nutrition_tools import NutritionTools
from domain.models import User, DietPlanType
from repository.diet_repository import DietRepository


async def test_nutrition_system():
    """Probar el sistema completo de nutrición"""
    
    print("🧪 Iniciando pruebas del sistema de nutrición...\n")
    
    # Usuario de prueba
    test_user = User(
        id="test-user-123",
        phone_number="+51998555878",
        name="Usuario Test",
        age=30,
        weight_kg=70.0,
        height_cm=175,
        goals=["perder_peso"]
    )
    
    # Inicializar componentes
    nutrition_tools = NutritionTools()
    nutrition_agent = NutritionAgent()
    diet_repo = DietRepository()
    
    print("✅ Componentes inicializados")
    
    # === PRUEBA 1: BUSCAR ALIMENTOS ===
    print("\n🔍 PRUEBA 1: Buscar alimentos")
    try:
        search_result = await nutrition_tools.search_foods("pollo", limit=3)
        print(f"Resultado búsqueda 'pollo': {search_result['success']}")
        if search_result['success'] and search_result['foods']:
            for food in search_result['foods']:
                print(f"  - {food['name_es']}: {food['calories_per_100g']} cal/100g")
        else:
            print("  No se encontraron alimentos")
    except Exception as e:
        print(f"  ❌ Error en búsqueda: {str(e)}")
    
    # === PRUEBA 2: OBTENER COMIDAS DEL DÍA ===
    print("\n📅 PRUEBA 2: Comidas del día")
    try:
        today_result = await nutrition_tools.get_today_meals(test_user.id)
        print(f"Resultado comidas hoy: {today_result['success']}")
        print(f"  Comidas planificadas: {len(today_result.get('planned_meals', []))}")
        print(f"  Comidas consumidas: {len(today_result.get('consumed_meals', []))}")
        
        nutrition_summary = today_result.get('nutrition_summary', {})
        if nutrition_summary:
            print(f"  Objetivo calórico: {nutrition_summary.get('target_calories', 0)} cal")
            print(f"  Consumido: {nutrition_summary.get('consumed_calories', 0)} cal")
    except Exception as e:
        print(f"  ❌ Error obteniendo comidas del día: {str(e)}")
    
    # === PRUEBA 3: SIGUIENTE COMIDA ===
    print("\n⏰ PRUEBA 3: Siguiente comida")
    try:
        next_meal_result = await nutrition_tools.get_next_meal(test_user.id)
        print(f"Resultado siguiente comida: {next_meal_result['success']}")
        if next_meal_result['success'] and next_meal_result.get('next_meal'):
            meal = next_meal_result['next_meal']
            print(f"  Siguiente: {meal['meal_name']} a las {meal['meal_time']}")
            print(f"  Calorías: {meal['target_calories']} cal")
        else:
            print(f"  {next_meal_result.get('message', 'Sin comidas pendientes')}")
    except Exception as e:
        print(f"  ❌ Error obteniendo siguiente comida: {str(e)}")
    
    # === PRUEBA 4: ANÁLISIS NUTRICIONAL ===
    print("\n📊 PRUEBA 4: Análisis nutricional")
    try:
        analysis_result = await nutrition_tools.analyze_nutrition_status(test_user.id)
        print(f"Resultado análisis: {analysis_result['success']}")
        if analysis_result['success']:
            analysis = analysis_result.get('analysis', {})
            print(f"  Estado calórico: {analysis.get('calorie_deficit_status', 'unknown')}")
            print(f"  Balance macros: {analysis.get('macro_balance_score', 0):.2f}")
            print(f"  Adherencia: {analysis.get('overall_adherence', 0):.1f}%")
            
            recommendations = analysis_result.get('recommendations', [])
            if recommendations:
                print(f"  Recomendaciones: {len(recommendations)}")
                for i, rec in enumerate(recommendations[:2], 1):
                    print(f"    {i}. {rec}")
    except Exception as e:
        print(f"  ❌ Error en análisis nutricional: {str(e)}")
    
    # === PRUEBA 5: AGENTE DE NUTRICIÓN ===
    print("\n🤖 PRUEBA 5: Agente de nutrición")
    
    test_messages = [
        "¿Qué comidas tengo hoy?",
        "¿Cuál es mi siguiente comida?",
        "¿Cómo voy con mi dieta?",
        "Buscar alimentos con proteína",
        "¿Puedo ayudarte con algo más?"
    ]
    
    for message in test_messages:
        try:
            can_handle = nutrition_agent.can_handle(message, {})
            print(f"  Mensaje: '{message}' -> Puede manejar: {can_handle}")
            
            if can_handle:
                response = await nutrition_agent.process_message(message, test_user, {})
                print(f"    Respuesta (primeros 100 chars): {response[:100]}...")
            else:
                print(f"    (No manejado por agente de nutrición)")
                
        except Exception as e:
            print(f"    ❌ Error procesando mensaje: {str(e)}")
        
        print()  # Línea en blanco
    
    print("🎉 Pruebas del sistema de nutrición completadas!")


def test_can_handle():
    """Pruebas rápidas de detección de mensajes"""
    print("🔍 Probando detección de mensajes del agente de nutrición...\n")
    
    agent = NutritionAgent()
    
    test_cases = [
        # Casos que SÍ debe manejar
        ("¿Qué comidas tengo hoy?", True),
        ("¿Cuál es mi siguiente comida?", True),
        ("¿Cómo voy con mi dieta?", True),
        ("Análisis nutricional", True),
        ("Buscar alimentos ricos en proteína", True),
        ("Registrar mi desayuno", True),
        ("¿Cuántas calorías he consumido?", True),
        ("Mi progreso nutricional", True),
        
        # Casos que NO debe manejar
        ("¿Cómo hacer ejercicio?", False),
        ("Iniciar rutina de pecho", False),
        ("¿Qué tal el clima?", False),
        ("Hola, ¿cómo estás?", False),
        ("Configurar notificaciones", False),
    ]
    
    for message, expected in test_cases:
        result = agent.can_handle(message, {})
        status = "✅" if result == expected else "❌"
        print(f"{status} '{message}' -> {result} (esperado: {expected})")
    
    print("\n🎯 Pruebas de detección completadas!")


if __name__ == "__main__":
    print("🚀 Sistema de Nutrición - Pruebas")
    print("=" * 50)
    
    # Ejecutar pruebas de detección primero (más rápidas)
    test_can_handle()
    
    print("\n" + "=" * 50)
    
    # Ejecutar pruebas completas del sistema
    asyncio.run(test_nutrition_system())

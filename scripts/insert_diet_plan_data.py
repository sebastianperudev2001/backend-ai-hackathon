"""
Script para insertar un plan de dieta completo con comidas planificadas
Esto permite probar todas las funcionalidades del sistema de nutrición
"""

import asyncio
import sys
import os
from datetime import datetime, date

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.supabase_client import get_supabase_client
from repository.diet_repository import DietRepository
from domain.models import CreateDietPlanRequest, DietPlanType, MealType


async def insert_complete_diet_plan():
    """Insertar plan de dieta completo para el usuario demo"""
    
    print("🍽️ CREANDO PLAN DE DIETA COMPLETO PARA PRUEBAS")
    print("=" * 60)
    
    supabase = get_supabase_client()
    diet_repo = DietRepository()
    
    # Usuario demo
    user_id = "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
    
    print(f"👤 Usuario: {user_id}")
    
    # 1. Verificar/obtener alimentos disponibles
    print("\n1. 🍎 Obteniendo alimentos disponibles...")
    try:
        foods_result = supabase.table('foods').select('id, name_es, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g').execute()
        
        if not foods_result.data or len(foods_result.data) < 10:
            print("   ❌ No hay suficientes alimentos. Ejecuta primero: python3 scripts/insert_common_foods.py")
            return False
            
        foods = {food['name_es']: food for food in foods_result.data}
        print(f"   ✅ Alimentos disponibles: {len(foods)}")
        
        # Mostrar algunos alimentos
        for name in list(foods.keys())[:5]:
            print(f"      - {name}: {foods[name]['calories_per_100g']} cal/100g")
            
    except Exception as e:
        print(f"   ❌ Error obteniendo alimentos: {e}")
        return False
    
    # 2. Crear plan de dieta
    print("\n2. 📋 Creando plan de dieta...")
    try:
        # Eliminar planes anteriores del usuario
        supabase.table('diet_plans').update({'is_active': False}).eq('user_id', user_id).execute()
        
        diet_plan_request = CreateDietPlanRequest(
            user_id=user_id,
            name="Plan de Pérdida de Peso - Demo",
            description="Plan balanceado para pérdida de peso con déficit calórico moderado",
            plan_type=DietPlanType.PERDIDA_PESO,
            target_calories=1800,  # Déficit moderado
            target_protein_g=120,  # 26.7% de calorías
            target_carbs_g=180,    # 40% de calorías  
            target_fat_g=60,       # 30% de calorías
            dietary_restrictions=[],
            food_allergies=[],
            disliked_foods=[]
        )
        
        diet_plan = await diet_repo.create_diet_plan(diet_plan_request)
        
        if diet_plan:
            print(f"   ✅ Plan creado: {diet_plan.name}")
            print(f"   🎯 Objetivo: {diet_plan.target_calories} cal/día")
            print(f"   📊 Macros: {diet_plan.target_protein_g}g proteína, {diet_plan.target_carbs_g}g carbos, {diet_plan.target_fat_g}g grasas")
        else:
            print("   ❌ Error creando plan de dieta")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creando plan: {e}")
        return False
    
    # 3. Crear comidas planificadas
    print("\n3. 🍽️ Creando comidas planificadas...")
    
    meals_to_create = [
        {
            "meal_type": MealType.DESAYUNO,
            "meal_name": "Desayuno Proteico",
            "meal_time": "07:00",
            "target_calories": 450,  # 25% de 1800
            "ingredients": [
                {"food": "Avena", "quantity": 40},
                {"food": "Plátano", "quantity": 120},
                {"food": "Yogur griego", "quantity": 150},
                {"food": "Almendras", "quantity": 15}
            ],
            "instructions": "Mezclar la avena con yogur griego, agregar plátano en rodajas y almendras picadas."
        },
        {
            "meal_type": MealType.COLACION_1,
            "meal_name": "Colación Matutina",
            "meal_time": "10:00", 
            "target_calories": 180,  # 10% de 1800
            "ingredients": [
                {"food": "Huevos", "quantity": 100},  # 2 huevos
                {"food": "Tomate", "quantity": 100}
            ],
            "instructions": "Huevos revueltos con tomate picado."
        },
        {
            "meal_type": MealType.ALMUERZO,
            "meal_name": "Almuerzo Balanceado",
            "meal_time": "13:00",
            "target_calories": 540,  # 30% de 1800
            "ingredients": [
                {"food": "Pechuga de pollo", "quantity": 120},
                {"food": "Arroz integral", "quantity": 100},
                {"food": "Brócoli", "quantity": 150},
                {"food": "Aceite de oliva", "quantity": 8}
            ],
            "instructions": "Pollo a la plancha, arroz integral hervido, brócoli al vapor, aliñar con aceite de oliva."
        },
        {
            "meal_type": MealType.COLACION_2,
            "meal_name": "Colación Vespertina", 
            "meal_time": "16:00",
            "target_calories": 180,  # 10% de 1800
            "ingredients": [
                {"food": "Aguacate", "quantity": 75},  # 1/2 aguacate
                {"food": "Pan integral", "quantity": 30}  # 1 rebanada
            ],
            "instructions": "Tostada integral con aguacate machacado."
        },
        {
            "meal_type": MealType.CENA,
            "meal_name": "Cena Ligera",
            "meal_time": "19:00",
            "target_calories": 450,  # 25% de 1800
            "ingredients": [
                {"food": "Salmón", "quantity": 100},
                {"food": "Espinaca", "quantity": 200},
                {"food": "Camote/Batata", "quantity": 150},
                {"food": "Aceite de oliva", "quantity": 5}
            ],
            "instructions": "Salmón a la plancha, ensalada de espinacas, camote horneado con un toque de aceite."
        }
    ]
    
    created_meals = 0
    
    for meal_data in meals_to_create:
        try:
            print(f"\n   🍽️ Creando: {meal_data['meal_name']} ({meal_data['meal_time']})")
            
            # Preparar ingredientes con IDs
            ingredients = []
            total_cal = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for ing in meal_data["ingredients"]:
                food_name = ing["food"]
                quantity = ing["quantity"]
                
                if food_name in foods:
                    food = foods[food_name]
                    
                    # Calcular valores nutricionales
                    cal = (quantity / 100) * food['calories_per_100g']
                    protein = (quantity / 100) * food['protein_per_100g'] 
                    carbs = (quantity / 100) * food['carbs_per_100g']
                    fat = (quantity / 100) * food['fat_per_100g']
                    
                    ingredients.append({
                        'food_id': food['id'],
                        'quantity_grams': quantity,
                        'notes': f"{quantity}g de {food_name}"
                    })
                    
                    total_cal += cal
                    total_protein += protein
                    total_carbs += carbs
                    total_fat += fat
                    
                    print(f"      - {food_name}: {quantity}g ({cal:.0f} cal)")
                else:
                    print(f"      ⚠️ Alimento no encontrado: {food_name}")
            
            # Crear comida planificada
            if ingredients:
                planned_meal = await diet_repo.create_planned_meal(
                    diet_plan_id=diet_plan.id,
                    meal_type=meal_data["meal_type"],
                    meal_name=meal_data["meal_name"],
                    meal_time=meal_data["meal_time"],
                    ingredients=ingredients
                )
                
                if planned_meal:
                    print(f"      ✅ Comida creada: {total_cal:.0f} cal, {total_protein:.1f}g proteína")
                    created_meals += 1
                else:
                    print(f"      ❌ Error creando comida")
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n   📊 Comidas creadas: {created_meals}/{len(meals_to_create)}")
    
    # 4. Verificar el plan completo
    print("\n4. ✅ Verificando plan completo...")
    try:
        planned_meals = await diet_repo.get_today_planned_meals(user_id)
        
        print(f"   📅 Comidas planificadas para hoy: {len(planned_meals)}")
        
        total_cal = 0
        total_protein = 0
        
        for meal in planned_meals:
            print(f"   • {meal.meal_time} - {meal.meal_name}: {meal.target_calories} cal")
            total_cal += meal.target_calories
            total_protein += float(meal.target_protein_g)
        
        print(f"\n   📊 TOTALES DEL PLAN:")
        print(f"   🔥 Calorías totales: {total_cal} cal (objetivo: {diet_plan.target_calories})")
        print(f"   🥩 Proteína total: {total_protein:.1f}g (objetivo: {diet_plan.target_protein_g}g)")
        
        # Calcular próxima comida
        next_meal, time_until = await diet_repo.get_next_planned_meal(user_id)
        if next_meal:
            print(f"   ⏰ Siguiente comida: {next_meal.meal_name} a las {next_meal.meal_time}")
        
    except Exception as e:
        print(f"   ❌ Error verificando plan: {e}")
    
    # 5. Crear resumen nutricional inicial
    print("\n5. 📈 Creando resumen nutricional...")
    try:
        summary = await diet_repo.get_daily_nutrition_summary(user_id)
        if summary:
            print(f"   ✅ Resumen creado: {summary.target_calories} cal objetivo")
        
    except Exception as e:
        print(f"   ❌ Error creando resumen: {e}")
    
    print("\n🎉 ¡PLAN DE DIETA COMPLETO CREADO!")
    print("\n✅ DATOS INSERTADOS:")
    print(f"   - 1 Plan de dieta activo ({diet_plan.target_calories} cal)")
    print(f"   - {created_meals} Comidas planificadas")
    print(f"   - Horarios: 07:00, 10:00, 13:00, 16:00, 19:00")
    print(f"   - Resumen nutricional inicializado")
    
    print("\n🧪 AHORA PUEDES PROBAR:")
    print("   • '¿Qué comidas tengo hoy?' -> Mostrará las 5 comidas")
    print("   • '¿Cuál es mi siguiente comida?' -> Próxima comida según hora")
    print("   • '¿Cómo voy con mi dieta?' -> Análisis nutricional")
    print("   • 'Buscar alimentos' -> Búsqueda en catálogo")
    
    return True


if __name__ == "__main__":
    print("📋 Insertar Plan de Dieta Completo")
    print("=" * 50)
    print("Este script crea un plan completo para el usuario demo")
    print()
    
    success = asyncio.run(insert_complete_diet_plan())
    
    if success:
        print("\n🎯 ¡PLAN INSERTADO EXITOSAMENTE!")
        print("   El sistema de nutrición está listo para pruebas completas")
    else:
        print("\n❌ Error insertando plan")
        print("   Verificar que los alimentos estén insertados primero")

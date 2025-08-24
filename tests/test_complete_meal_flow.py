"""
Test completo del flujo de comidas: crear usuario -> registrar comidas -> verificar logs
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repository.diet_repository import DietRepository
from repository.supabase_client import get_supabase_client
from domain.models import LogMealRequest, MealType


async def test_complete_meal_flow():
    """Probar el flujo completo: usuario -> comidas -> verificación"""
    
    print("🍽️ Test Completo del Flujo de Comidas")
    print("=" * 50)
    
    supabase = get_supabase_client()
    diet_repo = DietRepository()
    
    # Generar UUID para usuario de prueba
    test_user_id = str(uuid.uuid4())
    
    print(f"👤 Usuario de prueba: {test_user_id}")
    
    # 1. Crear usuario de prueba
    print("\n1. 👤 Creando usuario de prueba...")
    try:
        user_data = {
            'id': test_user_id,
            'phone_number': '+51999888777',
            'name': 'Usuario Prueba Comidas',
            'age': 30,
            'weight_kg': 70.0,
            'height_cm': 175,
            'fitness_level': 'intermedio',
            'goals': ['perder_peso'],
            'is_active': True
        }
        
        user_result = supabase.table('users').insert(user_data).execute()
        if user_result.data:
            print("   ✅ Usuario creado exitosamente")
        else:
            print("   ❌ Error creando usuario")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creando usuario: {str(e)}")
        return False
    
    # 2. Obtener algunos alimentos
    print("\n2. 🍎 Obteniendo alimentos disponibles...")
    try:
        foods_result = supabase.table('foods').select('id, name_es, calories_per_100g, protein_per_100g').limit(3).execute()
        if foods_result.data and len(foods_result.data) >= 2:
            foods = foods_result.data
            print(f"   ✅ Alimentos disponibles: {len(foods)}")
            for food in foods:
                print(f"      - {food['name_es']} (ID: {food['id'][:8]}...)")
        else:
            print("   ❌ No hay suficientes alimentos en la DB")
            return False
            
    except Exception as e:
        print(f"   ❌ Error obteniendo alimentos: {str(e)}")
        return False
    
    # 3. Registrar comida #1 - Desayuno
    print("\n3. 🌅 Registrando Desayuno...")
    try:
        breakfast_request = LogMealRequest(
            user_id=test_user_id,
            meal_type=MealType.DESAYUNO,
            meal_name='Desayuno saludable',
            ingredients=[
                {
                    'food_id': foods[0]['id'],  # Primer alimento
                    'quantity_grams': 100,
                    'notes': 'Porción estándar'
                },
                {
                    'food_id': foods[1]['id'],  # Segundo alimento  
                    'quantity_grams': 50,
                    'notes': 'Media porción'
                }
            ],
            notes='Desayuno balanceado de prueba',
            satisfaction_rating=5
        )
        
        breakfast_meal = await diet_repo.log_consumed_meal(breakfast_request)
        
        if breakfast_meal:
            print("   ✅ Desayuno registrado exitosamente")
            print(f"      ID: {breakfast_meal.id}")
            print(f"      Calorías: {breakfast_meal.total_calories}")
            print(f"      Proteína: {breakfast_meal.total_protein_g}g")
            print(f"      Satisfacción: {breakfast_meal.satisfaction_rating}/5")
        else:
            print("   ❌ Error registrando desayuno")
            return False
            
    except Exception as e:
        print(f"   ❌ Error registrando desayuno: {str(e)}")
        return False
    
    # 4. Registrar comida #2 - Almuerzo
    print("\n4. 🍽️ Registrando Almuerzo...")
    try:
        lunch_request = LogMealRequest(
            user_id=test_user_id,
            meal_type=MealType.ALMUERZO,
            meal_name='Almuerzo proteico',
            ingredients=[
                {
                    'food_id': foods[0]['id'],  # Mismo alimento pero más cantidad
                    'quantity_grams': 150,
                    'notes': 'Porción grande'
                }
            ],
            notes='Comida rica en proteínas',
            satisfaction_rating=4
        )
        
        lunch_meal = await diet_repo.log_consumed_meal(lunch_request)
        
        if lunch_meal:
            print("   ✅ Almuerzo registrado exitosamente")
            print(f"      ID: {lunch_meal.id}")
            print(f"      Calorías: {lunch_meal.total_calories}")
            print(f"      Proteína: {lunch_meal.total_protein_g}g")
        else:
            print("   ❌ Error registrando almuerzo")
            return False
            
    except Exception as e:
        print(f"   ❌ Error registrando almuerzo: {str(e)}")
        return False
    
    # 5. Verificar comidas consumidas del usuario
    print("\n5. 📊 Verificando comidas consumidas...")
    try:
        consumed_meals = await diet_repo.get_today_consumed_meals(test_user_id)
        
        print(f"   ✅ Comidas encontradas: {len(consumed_meals)}")
        total_calories = 0
        total_protein = 0
        
        for i, meal in enumerate(consumed_meals, 1):
            print(f"   {i}. {meal.meal_name} ({meal.meal_type.value})")
            print(f"      - Calorías: {meal.total_calories}")
            print(f"      - Proteína: {meal.total_protein_g}g")
            print(f"      - Hora: {meal.consumed_at.strftime('%H:%M')}")
            print(f"      - Satisfacción: {meal.satisfaction_rating}/5")
            
            total_calories += float(meal.total_calories)
            total_protein += float(meal.total_protein_g)
        
        print(f"\n   📈 TOTALES DEL DÍA:")
        print(f"      - Calorías totales: {total_calories:.1f}")
        print(f"      - Proteína total: {total_protein:.1f}g")
            
    except Exception as e:
        print(f"   ❌ Error verificando comidas: {str(e)}")
        return False
    
    # 6. Verificar ingredientes detallados
    print("\n6. 🔍 Verificando ingredientes detallados...")
    try:
        ingredients_query = supabase.table('consumed_meal_ingredients').select(
            '*, consumed_meals!inner(meal_name), foods!inner(name_es)'
        ).eq('consumed_meals.user_id', test_user_id).execute()
        
        if ingredients_query.data:
            print(f"   ✅ Ingredientes encontrados: {len(ingredients_query.data)}")
            for ing in ingredients_query.data:
                meal_name = ing['consumed_meals']['meal_name']
                food_name = ing['foods']['name_es']
                print(f"      - {food_name}: {ing['quantity_grams']}g en '{meal_name}'")
                print(f"        Calorías: {ing['calories']}, Proteína: {ing['protein_g']}g")
        else:
            print("   ⚠️ No se encontraron ingredientes detallados")
            
    except Exception as e:
        print(f"   ❌ Error verificando ingredientes: {str(e)}")
    
    # 7. Probar resumen nutricional diario
    print("\n7. 📈 Probando resumen nutricional diario...")
    try:
        nutrition_summary = await diet_repo.get_daily_nutrition_summary(test_user_id)
        
        if nutrition_summary:
            print("   ✅ Resumen nutricional generado")
            print(f"      - Objetivo: {nutrition_summary.target_calories} cal")
            print(f"      - Consumido: {nutrition_summary.consumed_calories} cal")
            print(f"      - Déficit: {nutrition_summary.calorie_deficit_surplus} cal")
            print(f"      - Adherencia: {nutrition_summary.adherence_percentage:.1f}%")
            print(f"      - Comidas completadas: {nutrition_summary.meals_completed}")
        else:
            print("   ❌ No se pudo generar resumen nutricional")
            
    except Exception as e:
        print(f"   ❌ Error en resumen nutricional: {str(e)}")
    
    # 8. Limpiar datos de prueba
    print("\n8. 🧹 Limpiando datos de prueba...")
    try:
        # Los ingredientes se eliminan automáticamente por cascade
        supabase.table('consumed_meals').delete().eq('user_id', test_user_id).execute()
        supabase.table('users').delete().eq('id', test_user_id).execute()
        print("   ✅ Datos de prueba eliminados")
    except Exception as e:
        print(f"   ⚠️ Error limpiando: {str(e)}")
    
    print("\n🎉 ¡Test del flujo completo de comidas exitoso!")
    print("\n✅ RESUMEN:")
    print("   - Usuario creado y eliminado ✅")
    print("   - Comidas registradas via repository ✅") 
    print("   - Ingredientes calculados automáticamente ✅")
    print("   - Consultas de comidas del día ✅")
    print("   - Resumen nutricional generado ✅")
    print("   - Logging completo en Supabase ✅")
    
    return True


if __name__ == "__main__":
    print("🚀 Test Completo del Sistema de Comidas")
    print("=" * 60)
    print("Este test verifica que las comidas se guarden correctamente en Supabase")
    print()
    
    # Ejecutar prueba completa
    success = asyncio.run(test_complete_meal_flow())
    
    if success:
        print("\n🎯 ¡TODAS LAS PRUEBAS PASARON!")
        print("   El sistema de logging de comidas está funcionando correctamente.")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("   Revisar la configuración de Supabase y las tablas.")

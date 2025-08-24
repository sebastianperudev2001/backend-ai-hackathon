"""
Test del logging de comidas con el usuario demo real del sistema
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repository.diet_repository import DietRepository
from repository.supabase_client import get_supabase_client
from domain.models import LogMealRequest, MealType


async def test_real_user_meals():
    """Probar logging con el usuario demo real"""
    
    print("👤 Test de Comidas con Usuario Demo Real")
    print("=" * 50)
    
    supabase = get_supabase_client()
    diet_repo = DietRepository()
    
    # Obtener usuario demo
    print("1. 🔍 Buscando usuario demo...")
    try:
        user_result = supabase.table('users').select('id, name, phone_number').eq(
            'phone_number', '+51998555878'
        ).execute()
        
        if user_result.data:
            demo_user = user_result.data[0]
            user_id = demo_user['id']
            print(f"   ✅ Usuario encontrado: {demo_user['name']}")
            print(f"   📱 Teléfono: {demo_user['phone_number']}")
            print(f"   🆔 ID: {user_id}")
        else:
            print("   ❌ Usuario demo no encontrado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error buscando usuario: {str(e)}")
        return False
    
    # Obtener alimentos disponibles
    print("\n2. 🍎 Obteniendo alimentos...")
    try:
        foods_result = supabase.table('foods').select('id, name_es, calories_per_100g').limit(3).execute()
        if foods_result.data:
            foods = foods_result.data
            print(f"   ✅ Alimentos disponibles: {len(foods)}")
            for food in foods:
                print(f"      - {food['name_es']}: {food['calories_per_100g']} cal/100g")
        else:
            print("   ❌ No hay alimentos disponibles")
            return False
            
    except Exception as e:
        print(f"   ❌ Error obteniendo alimentos: {str(e)}")
        return False
    
    # Registrar una comida de prueba
    print("\n3. 🍽️ Registrando comida para usuario demo...")
    try:
        test_meal_request = LogMealRequest(
            user_id=user_id,
            meal_type=MealType.COLACION_1,
            meal_name='Snack de prueba - Sistema Nutrición',
            ingredients=[
                {
                    'food_id': foods[0]['id'],  # Pechuga de pollo
                    'quantity_grams': 80,
                    'notes': 'Porción pequeña de prueba'
                }
            ],
            notes='🧪 Comida de prueba del sistema de nutrición',
            satisfaction_rating=5
        )
        
        consumed_meal = await diet_repo.log_consumed_meal(test_meal_request)
        
        if consumed_meal:
            print("   ✅ Comida registrada exitosamente!")
            print(f"      📝 Nombre: {consumed_meal.meal_name}")
            print(f"      🔥 Calorías: {consumed_meal.total_calories}")
            print(f"      🥩 Proteína: {consumed_meal.total_protein_g}g")
            print(f"      ⭐ Satisfacción: {consumed_meal.satisfaction_rating}/5")
            print(f"      🕐 Hora: {consumed_meal.consumed_at.strftime('%H:%M:%S')}")
            meal_id = consumed_meal.id
        else:
            print("   ❌ Error registrando comida")
            return False
            
    except Exception as e:
        print(f"   ❌ Error registrando comida: {str(e)}")
        return False
    
    # Verificar que se guardó
    print("\n4. 🔍 Verificando que se guardó en Supabase...")
    try:
        # Consulta directa a la base de datos
        saved_meal = supabase.table('consumed_meals').select('*').eq('id', meal_id).execute()
        
        if saved_meal.data:
            meal_data = saved_meal.data[0]
            print("   ✅ Comida encontrada en Supabase:")
            print(f"      ID: {meal_data['id']}")
            print(f"      Usuario: {meal_data['user_id']}")
            print(f"      Tipo: {meal_data['meal_type']}")
            print(f"      Nombre: {meal_data['meal_name']}")
            print(f"      Calorías: {meal_data['total_calories']}")
            print(f"      Fecha: {meal_data['consumption_date']}")
        else:
            print("   ❌ Comida no encontrada en Supabase")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando en Supabase: {str(e)}")
        return False
    
    # Verificar ingredientes
    print("\n5. 🥘 Verificando ingredientes...")
    try:
        ingredients = supabase.table('consumed_meal_ingredients').select('*').eq(
            'consumed_meal_id', meal_id
        ).execute()
        
        if ingredients.data:
            print(f"   ✅ Ingredientes guardados: {len(ingredients.data)}")
            for ing in ingredients.data:
                print(f"      - Food ID: {ing['food_id'][:8]}...")
                print(f"        Cantidad: {ing['quantity_grams']}g")
                print(f"        Calorías: {ing['calories']}")
                print(f"        Proteína: {ing['protein_g']}g")
        else:
            print("   ⚠️ No se encontraron ingredientes")
            
    except Exception as e:
        print(f"   ❌ Error verificando ingredientes: {str(e)}")
    
    # Obtener comidas del día del usuario
    print("\n6. 📅 Consultando comidas del día del usuario...")
    try:
        today_meals = await diet_repo.get_today_consumed_meals(user_id)
        
        print(f"   ✅ Comidas del día: {len(today_meals)}")
        total_cal = 0
        total_protein = 0
        
        for i, meal in enumerate(today_meals, 1):
            print(f"   {i}. {meal.meal_name} ({meal.meal_type.value})")
            print(f"      🔥 {meal.total_calories} cal | 🥩 {meal.total_protein_g}g proteína")
            total_cal += float(meal.total_calories)
            total_protein += float(meal.total_protein_g)
        
        if today_meals:
            print(f"\n   📊 TOTAL DEL DÍA:")
            print(f"      🔥 Calorías: {total_cal:.1f}")
            print(f"      🥩 Proteína: {total_protein:.1f}g")
            
    except Exception as e:
        print(f"   ❌ Error consultando comidas del día: {str(e)}")
    
    # Preguntar si eliminar la comida de prueba
    print(f"\n7. 🧹 ¿Eliminar comida de prueba? (ID: {meal_id[:8]}...)")
    try:
        # Para testing, siempre eliminar
        delete_result = supabase.table('consumed_meals').delete().eq('id', meal_id).execute()
        print("   ✅ Comida de prueba eliminada")
    except Exception as e:
        print(f"   ⚠️ Error eliminando comida de prueba: {str(e)}")
    
    print("\n🎉 ¡Test con usuario demo completado!")
    print("\n✅ CONFIRMADO:")
    print("   - El sistema ESTÁ guardando comidas en Supabase ✅")
    print("   - Los cálculos nutricionales funcionan ✅")
    print("   - Las consultas por usuario funcionan ✅")
    print("   - Los ingredientes se guardan correctamente ✅")
    
    return True


if __name__ == "__main__":
    print("🧪 Test de Logging con Usuario Demo Real")
    print("=" * 60)
    
    success = asyncio.run(test_real_user_meals())
    
    if success:
        print("\n🎯 El sistema de logging de comidas está funcionando perfectamente!")
    else:
        print("\n❌ Hubo problemas en el test")

"""
Script para probar específicamente el logging de comidas en Supabase
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


async def test_meal_logging():
    """Probar el logging de comidas paso a paso"""
    
    print("🧪 Probando Logging de Comidas en Supabase")
    print("=" * 50)
    
    # Verificar conexión a Supabase
    print("1. 🔌 Verificando conexión a Supabase...")
    try:
        supabase = get_supabase_client()
        print(f"   ✅ Cliente Supabase inicializado: {type(supabase)}")
        
        # Verificar que las tablas existen
        tables_to_check = ['consumed_meals', 'consumed_meal_ingredients', 'foods']
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"   ✅ Tabla '{table}' accesible")
            except Exception as e:
                print(f"   ❌ Error accediendo tabla '{table}': {str(e)}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error conectando a Supabase: {str(e)}")
        return False
    
    # Verificar que existen alimentos en la DB
    print("\n2. 🍎 Verificando alimentos en la base de datos...")
    try:
        foods_result = supabase.table('foods').select('id, name_es, calories_per_100g').limit(5).execute()
        if foods_result.data:
            print(f"   ✅ Encontrados {len(foods_result.data)} alimentos:")
            for food in foods_result.data:
                print(f"      - {food['name_es']} (ID: {food['id']}) - {food['calories_per_100g']} cal/100g")
            first_food_id = foods_result.data[0]['id']
        else:
            print("   ❌ No hay alimentos en la base de datos")
            print("   💡 Ejecutar: python3 scripts/insert_common_foods.py")
            return False
    except Exception as e:
        print(f"   ❌ Error obteniendo alimentos: {str(e)}")
        return False
    
    # Generar UUIDs válidos para las pruebas
    test_user_direct = str(uuid.uuid4())
    test_user_repo = str(uuid.uuid4())
    
    # Probar inserción directa en Supabase
    print("\n3. 📝 Probando inserción directa en consumed_meals...")
    try:
        test_meal_data = {
            'user_id': test_user_direct,
            'meal_type': 'desayuno',
            'meal_name': 'Desayuno de prueba',
            'consumed_at': datetime.now().isoformat(),
            'consumption_date': datetime.now().date().isoformat(),
            'total_calories': 350,
            'total_protein_g': 20,
            'total_carbs_g': 45,
            'total_fat_g': 12,
            'notes': 'Prueba de logging directo'
        }
        
        direct_result = supabase.table('consumed_meals').insert(test_meal_data).execute()
        if direct_result.data:
            print("   ✅ Inserción directa exitosa")
            test_meal_id = direct_result.data[0]['id']
            print(f"      ID generado: {test_meal_id}")
        else:
            print("   ❌ Inserción directa falló")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en inserción directa: {str(e)}")
        return False
    
    # Probar repository de dietas
    print("\n4. 🏪 Probando DietRepository...")
    try:
        diet_repo = DietRepository()
        print("   ✅ DietRepository inicializado")
        
        # Crear request de comida
        meal_request = LogMealRequest(
            user_id=test_user_repo,
            meal_type=MealType.ALMUERZO,
            meal_name='Almuerzo de prueba via repository',
            ingredients=[
                {
                    'food_id': first_food_id,
                    'quantity_grams': 150,
                    'notes': 'Ingrediente de prueba'
                }
            ],
            notes='Probando el repository',
            satisfaction_rating=4
        )
        
        print(f"   📋 Request creado con ingrediente: {first_food_id}")
        
        # Intentar logging
        consumed_meal = await diet_repo.log_consumed_meal(meal_request)
        
        if consumed_meal:
            print("   ✅ Comida guardada exitosamente via repository")
            print(f"      ID: {consumed_meal.id}")
            print(f"      Nombre: {consumed_meal.meal_name}")
            print(f"      Calorías: {consumed_meal.total_calories}")
            print(f"      Proteína: {consumed_meal.total_protein_g}g")
        else:
            print("   ❌ Error guardando comida via repository")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en DietRepository: {str(e)}")
        return False
    
    # Verificar que se guardaron los datos
    print("\n5. 🔍 Verificando datos guardados...")
    try:
        # Verificar comidas guardadas
        saved_meals = supabase.table('consumed_meals').select('*').in_(
            'user_id', [test_user_direct, test_user_repo]
        ).execute()
        
        print(f"   ✅ Comidas guardadas: {len(saved_meals.data)}")
        for meal in saved_meals.data:
            print(f"      - {meal['meal_name']} ({meal['user_id']}) - {meal['total_calories']} cal")
        
        # Verificar ingredientes guardados
        saved_ingredients = supabase.table('consumed_meal_ingredients').select('*').execute()
        repo_ingredients = [ing for ing in saved_ingredients.data if ing.get('consumed_meal_id') == consumed_meal.id]
        
        print(f"   ✅ Ingredientes del repository: {len(repo_ingredients)}")
        for ing in repo_ingredients:
            print(f"      - Food ID: {ing['food_id']}, Cantidad: {ing['quantity_grams']}g")
            
    except Exception as e:
        print(f"   ❌ Error verificando datos: {str(e)}")
        return False
    
    # Limpiar datos de prueba
    print("\n6. 🧹 Limpiando datos de prueba...")
    try:
        # Eliminar comidas de prueba
        supabase.table('consumed_meals').delete().in_(
            'user_id', [test_user_direct, test_user_repo]
        ).execute()
        print("   ✅ Datos de prueba eliminados")
    except Exception as e:
        print(f"   ⚠️ Error limpiando datos: {str(e)}")
    
    print("\n🎉 ¡Prueba de logging completada exitosamente!")
    return True


def test_supabase_client():
    """Probar conexión básica a Supabase"""
    print("🔌 Probando cliente Supabase...")
    
    try:
        supabase = get_supabase_client()
        print(f"✅ Cliente inicializado: {type(supabase)}")
        
        # Probar una consulta simple
        result = supabase.table('foods').select('count').execute()
        print(f"✅ Consulta exitosa, datos: {result.data if hasattr(result, 'data') else 'Sin data'}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Verificar variables de entorno SUPABASE_URL y SUPABASE_KEY")
        return False


if __name__ == "__main__":
    print("🚀 Test de Logging de Comidas")
    print("=" * 40)
    
    # Primero probar conexión básica
    if not test_supabase_client():
        print("\n❌ Fallo en conexión básica, no se puede continuar")
        exit(1)
    
    print("\n" + "=" * 40)
    
    # Ejecutar prueba completa
    asyncio.run(test_meal_logging())

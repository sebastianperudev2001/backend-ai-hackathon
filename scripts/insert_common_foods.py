"""
Script para insertar alimentos comunes en la base de datos
Datos nutricionales basados en USDA y tablas nutricionales estándar
"""

import asyncio
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.supabase_client import get_supabase_client

# Datos de alimentos comunes con información nutricional completa por 100g
COMMON_FOODS = [
    # PROTEÍNAS ANIMALES
    {
        "name": "chicken_breast",
        "name_es": "Pechuga de pollo",
        "category": "proteinas",
        "calories_per_100g": 165,
        "protein_per_100g": 31.0,
        "carbs_per_100g": 0,
        "fat_per_100g": 3.6,
        "fiber_per_100g": 0,
        "common_serving_size_g": 150,
        "serving_description": "1 pechuga mediana",
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_high_protein": True
    },
    {
        "name": "salmon",
        "name_es": "Salmón",
        "category": "proteinas",
        "calories_per_100g": 208,
        "protein_per_100g": 25.4,
        "carbs_per_100g": 0,
        "fat_per_100g": 12.4,
        "fiber_per_100g": 0,
        "common_serving_size_g": 120,
        "serving_description": "1 filete",
        "is_vegetarian": False,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_high_protein": True
    },
    {
        "name": "eggs",
        "name_es": "Huevos",
        "category": "proteinas",
        "calories_per_100g": 155,
        "protein_per_100g": 13.0,
        "carbs_per_100g": 1.1,
        "fat_per_100g": 11.0,
        "fiber_per_100g": 0,
        "common_serving_size_g": 50,
        "serving_description": "1 huevo grande",
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "greek_yogurt",
        "name_es": "Yogur griego",
        "category": "lacteos",
        "calories_per_100g": 97,
        "protein_per_100g": 10.0,
        "carbs_per_100g": 4.0,
        "fat_per_100g": 5.0,
        "fiber_per_100g": 0,
        "calcium_mg_per_100g": 110,
        "common_serving_size_g": 170,
        "serving_description": "1 envase individual",
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_dairy_free": False
    },
    
    # CARBOHIDRATOS
    {
        "name": "brown_rice",
        "name_es": "Arroz integral",
        "category": "granos",
        "calories_per_100g": 112,
        "protein_per_100g": 2.6,
        "carbs_per_100g": 23.0,
        "fat_per_100g": 0.9,
        "fiber_per_100g": 1.8,
        "glycemic_index": 50,
        "common_serving_size_g": 150,
        "serving_description": "3/4 taza cocido",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "white_rice",
        "name_es": "Arroz blanco",
        "category": "granos",
        "calories_per_100g": 130,
        "protein_per_100g": 2.7,
        "carbs_per_100g": 28.0,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 0.4,
        "glycemic_index": 73,
        "common_serving_size_g": 150,
        "serving_description": "3/4 taza cocido",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "oats",
        "name_es": "Avena",
        "category": "granos",
        "calories_per_100g": 389,
        "protein_per_100g": 16.9,
        "carbs_per_100g": 66.3,
        "fat_per_100g": 6.9,
        "fiber_per_100g": 10.6,
        "glycemic_index": 55,
        "common_serving_size_g": 40,
        "serving_description": "1/2 taza seca",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": False,  # Puede contener gluten por contaminación cruzada
        "is_dairy_free": True
    },
    {
        "name": "sweet_potato",
        "name_es": "Camote/Batata",
        "category": "verduras",
        "calories_per_100g": 86,
        "protein_per_100g": 1.6,
        "carbs_per_100g": 20.1,
        "fat_per_100g": 0.1,
        "fiber_per_100g": 3.0,
        "glycemic_index": 63,
        "vitamin_c_mg_per_100g": 2.4,
        "potassium_mg_per_100g": 337,
        "common_serving_size_g": 150,
        "serving_description": "1 camote mediano",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "banana",
        "name_es": "Plátano",
        "category": "frutas",
        "calories_per_100g": 89,
        "protein_per_100g": 1.1,
        "carbs_per_100g": 22.8,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 2.6,
        "sugar_per_100g": 12.2,
        "glycemic_index": 51,
        "potassium_mg_per_100g": 358,
        "vitamin_c_mg_per_100g": 8.7,
        "common_serving_size_g": 120,
        "serving_description": "1 plátano mediano",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    
    # GRASAS SALUDABLES
    {
        "name": "avocado",
        "name_es": "Aguacate",
        "category": "grasas",
        "calories_per_100g": 160,
        "protein_per_100g": 2.0,
        "carbs_per_100g": 8.5,
        "fat_per_100g": 14.7,
        "fiber_per_100g": 6.7,
        "glycemic_index": 15,
        "potassium_mg_per_100g": 485,
        "common_serving_size_g": 75,
        "serving_description": "1/2 aguacate mediano",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "almonds",
        "name_es": "Almendras",
        "category": "grasas",
        "calories_per_100g": 579,
        "protein_per_100g": 21.2,
        "carbs_per_100g": 21.6,
        "fat_per_100g": 49.9,
        "fiber_per_100g": 12.5,
        "calcium_mg_per_100g": 269,
        "common_serving_size_g": 28,
        "serving_description": "1 puñado (23 almendras)",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_high_protein": True
    },
    {
        "name": "olive_oil",
        "name_es": "Aceite de oliva",
        "category": "grasas",
        "calories_per_100g": 884,
        "protein_per_100g": 0,
        "carbs_per_100g": 0,
        "fat_per_100g": 100.0,
        "fiber_per_100g": 0,
        "common_serving_size_g": 14,
        "serving_description": "1 cucharada",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    
    # VERDURAS
    {
        "name": "broccoli",
        "name_es": "Brócoli",
        "category": "verduras",
        "calories_per_100g": 34,
        "protein_per_100g": 2.8,
        "carbs_per_100g": 7.0,
        "fat_per_100g": 0.4,
        "fiber_per_100g": 2.6,
        "vitamin_c_mg_per_100g": 89.2,
        "calcium_mg_per_100g": 47,
        "iron_mg_per_100g": 0.73,
        "common_serving_size_g": 85,
        "serving_description": "1 taza",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_low_carb": True
    },
    {
        "name": "spinach",
        "name_es": "Espinaca",
        "category": "verduras",
        "calories_per_100g": 23,
        "protein_per_100g": 2.9,
        "carbs_per_100g": 3.6,
        "fat_per_100g": 0.4,
        "fiber_per_100g": 2.2,
        "vitamin_c_mg_per_100g": 28.1,
        "calcium_mg_per_100g": 99,
        "iron_mg_per_100g": 2.71,
        "common_serving_size_g": 30,
        "serving_description": "1 taza cruda",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_low_carb": True
    },
    {
        "name": "tomato",
        "name_es": "Tomate",
        "category": "verduras",
        "calories_per_100g": 18,
        "protein_per_100g": 0.9,
        "carbs_per_100g": 3.9,
        "fat_per_100g": 0.2,
        "fiber_per_100g": 1.2,
        "sugar_per_100g": 2.6,
        "vitamin_c_mg_per_100g": 13.7,
        "potassium_mg_per_100g": 237,
        "common_serving_size_g": 150,
        "serving_description": "1 tomate mediano",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True,
        "is_low_carb": True
    },
    
    # LEGUMBRES
    {
        "name": "black_beans",
        "name_es": "Frijoles negros",
        "category": "legumbres",
        "calories_per_100g": 132,
        "protein_per_100g": 8.9,
        "carbs_per_100g": 23.0,
        "fat_per_100g": 0.5,
        "fiber_per_100g": 8.7,
        "glycemic_index": 30,
        "iron_mg_per_100g": 2.1,
        "common_serving_size_g": 172,
        "serving_description": "3/4 taza cocidos",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "lentils",
        "name_es": "Lentejas",
        "category": "legumbres",
        "calories_per_100g": 116,
        "protein_per_100g": 9.0,
        "carbs_per_100g": 20.1,
        "fat_per_100g": 0.4,
        "fiber_per_100g": 7.9,
        "glycemic_index": 32,
        "iron_mg_per_100g": 3.3,
        "common_serving_size_g": 200,
        "serving_description": "1 taza cocidas",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    
    # OTROS ALIMENTOS COMUNES
    {
        "name": "quinoa",
        "name_es": "Quinoa",
        "category": "granos",
        "calories_per_100g": 120,
        "protein_per_100g": 4.4,
        "carbs_per_100g": 22.0,
        "fat_per_100g": 1.9,
        "fiber_per_100g": 2.8,
        "glycemic_index": 53,
        "iron_mg_per_100g": 1.5,
        "common_serving_size_g": 185,
        "serving_description": "1 taza cocida",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": True,
        "is_dairy_free": True
    },
    {
        "name": "whole_wheat_bread",
        "name_es": "Pan integral",
        "category": "granos",
        "calories_per_100g": 247,
        "protein_per_100g": 13.0,
        "carbs_per_100g": 41.0,
        "fat_per_100g": 4.2,
        "fiber_per_100g": 7.0,
        "glycemic_index": 74,
        "common_serving_size_g": 28,
        "serving_description": "1 rebanada",
        "is_vegetarian": True,
        "is_vegan": True,
        "is_gluten_free": False,
        "is_dairy_free": True
    },
    {
        "name": "milk_whole",
        "name_es": "Leche entera",
        "category": "lacteos",
        "calories_per_100g": 61,
        "protein_per_100g": 3.2,
        "carbs_per_100g": 4.8,
        "fat_per_100g": 3.3,
        "fiber_per_100g": 0,
        "sugar_per_100g": 4.8,
        "calcium_mg_per_100g": 113,
        "common_serving_size_g": 240,
        "serving_description": "1 taza",
        "is_vegetarian": True,
        "is_vegan": False,
        "is_gluten_free": True,
        "is_dairy_free": False
    }
]

async def insert_foods():
    """Insertar alimentos comunes en la base de datos"""
    try:
        supabase = get_supabase_client()
        
        print("Insertando alimentos comunes en la base de datos...")
        
        for food_data in COMMON_FOODS:
            try:
                # Insertar o actualizar si ya existe
                result = supabase.table('foods').upsert(
                    food_data,
                    on_conflict='name'
                ).execute()
                
                print(f"✓ Insertado: {food_data['name_es']} ({food_data['name']})")
                
            except Exception as e:
                print(f"✗ Error insertando {food_data['name_es']}: {str(e)}")
                continue
        
        print(f"\n¡Completado! Se procesaron {len(COMMON_FOODS)} alimentos.")
        
        # Verificar inserción
        result = supabase.table('foods').select('count').execute()
        total_foods = len(result.data) if result.data else 0
        print(f"Total de alimentos en la base de datos: {total_foods}")
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(insert_foods())

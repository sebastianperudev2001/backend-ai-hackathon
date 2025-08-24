"""
Repository para el manejo de datos de dietas y nutrición
Incluye operaciones CRUD para todos los aspectos del sistema de dietas
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from .supabase_client import get_supabase_client
from domain.models import (
    Food, DietPlan, PlannedMeal, PlannedMealIngredient,
    ConsumedMeal, ConsumedMealIngredient, DailyNutritionSummary,
    FoodSubstitution, FoodCategory, DietPlanType, MealType,
    CreateDietPlanRequest, LogMealRequest, AdjustDietRequest
)

logger = logging.getLogger(__name__)


class DietRepository:
    """Repository para operaciones de dietas y nutrición"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    # ==================== OPERACIONES DE ALIMENTOS ====================
    
    async def get_food_by_id(self, food_id: str) -> Optional[Food]:
        """Obtener un alimento por ID"""
        try:
            result = self.supabase.table('foods').select('*').eq('id', food_id).execute()
            
            if result.data:
                return Food(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo alimento {food_id}: {str(e)}")
            return None
    
    async def search_foods(
        self, 
        query: str, 
        category: Optional[FoodCategory] = None,
        dietary_filters: Optional[Dict[str, bool]] = None,
        limit: int = 20
    ) -> List[Food]:
        """Buscar alimentos por nombre o categoría"""
        try:
            # Construir la consulta base
            supabase_query = self.supabase.table('foods').select('*')
            
            # Filtrar por nombre (buscar en nombre y nombre_es)
            if query:
                supabase_query = supabase_query.or_(
                    f"name.ilike.%{query}%,name_es.ilike.%{query}%"
                )
            
            # Filtrar por categoría
            if category:
                supabase_query = supabase_query.eq('category', category.value)
            
            # Aplicar filtros dietéticos
            if dietary_filters:
                for filter_key, filter_value in dietary_filters.items():
                    if filter_key in ['is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_dairy_free']:
                        supabase_query = supabase_query.eq(filter_key, filter_value)
            
            # Limitar resultados y ordenar
            supabase_query = supabase_query.limit(limit).order('name_es')
            
            result = supabase_query.execute()
            return [Food(**food_data) for food_data in result.data]
            
        except Exception as e:
            logger.error(f"Error buscando alimentos con query '{query}': {str(e)}")
            return []
    
    async def get_foods_by_category(self, category: FoodCategory, limit: int = 50) -> List[Food]:
        """Obtener alimentos por categoría"""
        try:
            result = self.supabase.table('foods').select('*').eq(
                'category', category.value
            ).limit(limit).order('name_es').execute()
            
            return [Food(**food_data) for food_data in result.data]
            
        except Exception as e:
            logger.error(f"Error obteniendo alimentos de categoría {category}: {str(e)}")
            return []
    
    # ==================== OPERACIONES DE PLANES DE DIETA ====================
    
    async def create_diet_plan(self, plan_request: CreateDietPlanRequest) -> Optional[DietPlan]:
        """Crear un nuevo plan de dieta"""
        try:
            # Desactivar planes anteriores del usuario
            await self._deactivate_user_diet_plans(plan_request.user_id)
            
            # Crear el nuevo plan
            plan_data = {
                'user_id': plan_request.user_id,
                'name': plan_request.name,
                'description': plan_request.description,
                'plan_type': plan_request.plan_type.value,
                'target_calories': plan_request.target_calories,
                'target_protein_g': plan_request.target_protein_g,
                'target_carbs_g': plan_request.target_carbs_g,
                'target_fat_g': plan_request.target_fat_g,
                'dietary_restrictions': plan_request.dietary_restrictions,
                'food_allergies': plan_request.food_allergies,
                'disliked_foods': plan_request.disliked_foods,
                'is_active': True,
                'start_date': datetime.now().date().isoformat()
            }
            
            result = self.supabase.table('diet_plans').insert(plan_data).execute()
            
            if result.data:
                return DietPlan(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error creando plan de dieta: {str(e)}")
            return None
    
    async def get_active_diet_plan(self, user_id: str) -> Optional[DietPlan]:
        """Obtener el plan de dieta activo del usuario"""
        try:
            result = self.supabase.table('diet_plans').select('*').eq(
                'user_id', user_id
            ).eq('is_active', True).execute()
            
            if result.data:
                return DietPlan(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo plan activo para usuario {user_id}: {str(e)}")
            return None
    
    async def _deactivate_user_diet_plans(self, user_id: str) -> bool:
        """Desactivar todos los planes de dieta del usuario"""
        try:
            result = self.supabase.table('diet_plans').update({
                'is_active': False,
                'end_date': datetime.now().date().isoformat()
            }).eq('user_id', user_id).eq('is_active', True).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error desactivando planes de usuario {user_id}: {str(e)}")
            return False
    
    # ==================== OPERACIONES DE COMIDAS PLANIFICADAS ====================
    
    async def create_planned_meal(
        self, 
        diet_plan_id: str, 
        meal_type: MealType,
        meal_name: str,
        meal_time: str,
        ingredients: List[Dict[str, Any]]
    ) -> Optional[PlannedMeal]:
        """Crear una comida planificada con sus ingredientes"""
        try:
            # Crear la comida planificada
            meal_data = {
                'diet_plan_id': diet_plan_id,
                'meal_type': meal_type.value,
                'meal_name': meal_name,
                'meal_time': meal_time,
                'target_calories': 0,  # Se calculará automáticamente
                'target_protein_g': 0,
                'target_carbs_g': 0,
                'target_fat_g': 0
            }
            
            meal_result = self.supabase.table('planned_meals').insert(meal_data).execute()
            
            if not meal_result.data:
                return None
            
            planned_meal_id = meal_result.data[0]['id']
            
            # Agregar ingredientes
            for ingredient in ingredients:
                await self._add_planned_meal_ingredient(
                    planned_meal_id, 
                    ingredient['food_id'], 
                    ingredient['quantity_grams'],
                    ingredient.get('notes'),
                    ingredient.get('is_optional', False)
                )
            
            # Obtener la comida completa con totales calculados
            return await self.get_planned_meal_by_id(planned_meal_id)
            
        except Exception as e:
            logger.error(f"Error creando comida planificada: {str(e)}")
            return None
    
    async def _add_planned_meal_ingredient(
        self, 
        planned_meal_id: str, 
        food_id: str, 
        quantity_grams: float,
        notes: Optional[str] = None,
        is_optional: bool = False
    ) -> bool:
        """Agregar un ingrediente a una comida planificada"""
        try:
            ingredient_data = {
                'planned_meal_id': planned_meal_id,
                'food_id': food_id,
                'quantity_grams': quantity_grams,
                'notes': notes,
                'is_optional': is_optional
            }
            
            result = self.supabase.table('planned_meal_ingredients').insert(ingredient_data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error agregando ingrediente a comida planificada: {str(e)}")
            return False
    
    async def get_planned_meal_by_id(self, planned_meal_id: str) -> Optional[PlannedMeal]:
        """Obtener una comida planificada por ID"""
        try:
            result = self.supabase.table('planned_meals').select('*').eq(
                'id', planned_meal_id
            ).execute()
            
            if result.data:
                return PlannedMeal(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo comida planificada {planned_meal_id}: {str(e)}")
            return None
    
    async def get_today_planned_meals(self, user_id: str, target_date: Optional[date] = None) -> List[PlannedMeal]:
        """Obtener comidas planificadas para hoy"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # Primero obtener el plan activo
            diet_plan = await self.get_active_diet_plan(user_id)
            if not diet_plan:
                return []
            
            # Obtener comidas planificadas del plan
            result = self.supabase.table('planned_meals').select('*').eq(
                'diet_plan_id', diet_plan.id
            ).order('meal_time').execute()
            
            return [PlannedMeal(**meal_data) for meal_data in result.data]
            
        except Exception as e:
            logger.error(f"Error obteniendo comidas planificadas para usuario {user_id}: {str(e)}")
            return []
    
    async def get_next_planned_meal(self, user_id: str) -> Tuple[Optional[PlannedMeal], Optional[int]]:
        """Obtener la siguiente comida planificada y minutos hasta ella"""
        try:
            current_time = datetime.now().time()
            planned_meals = await self.get_today_planned_meals(user_id)
            
            # Encontrar la siguiente comida
            next_meal = None
            min_time_diff = float('inf')
            
            for meal in planned_meals:
                meal_time = datetime.strptime(meal.meal_time, "%H:%M").time()
                
                # Calcular diferencia en minutos
                current_datetime = datetime.combine(date.today(), current_time)
                meal_datetime = datetime.combine(date.today(), meal_time)
                
                # Si la comida ya pasó hoy, considerarla para mañana
                if meal_datetime <= current_datetime:
                    meal_datetime += timedelta(days=1)
                
                time_diff = (meal_datetime - current_datetime).total_seconds() / 60
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    next_meal = meal
            
            time_until_next = int(min_time_diff) if next_meal else None
            return next_meal, time_until_next
            
        except Exception as e:
            logger.error(f"Error obteniendo siguiente comida para usuario {user_id}: {str(e)}")
            return None, None
    
    # ==================== OPERACIONES DE COMIDAS CONSUMIDAS ====================
    
    async def log_consumed_meal(self, meal_request: LogMealRequest) -> Optional[ConsumedMeal]:
        """Registrar una comida consumida"""
        try:
            # Crear la comida consumida
            meal_data = {
                'user_id': meal_request.user_id,
                'meal_type': meal_request.meal_type.value,
                'meal_name': meal_request.meal_name,
                'consumed_at': datetime.now().isoformat(),
                'consumption_date': datetime.now().date().isoformat(),
                'notes': meal_request.notes,
                'satisfaction_rating': meal_request.satisfaction_rating,
                'total_calories': 0,  # Se calculará automáticamente
                'total_protein_g': 0,
                'total_carbs_g': 0,
                'total_fat_g': 0,
                'total_fiber_g': 0
            }
            
            meal_result = self.supabase.table('consumed_meals').insert(meal_data).execute()
            
            if not meal_result.data:
                return None
            
            consumed_meal_id = meal_result.data[0]['id']
            
            # Agregar ingredientes
            for ingredient in meal_request.ingredients:
                await self._add_consumed_meal_ingredient(
                    consumed_meal_id,
                    ingredient['food_id'],
                    ingredient['quantity_grams'],
                    ingredient.get('notes'),
                    ingredient.get('was_planned', False)
                )
            
            # Actualizar resumen nutricional diario
            await self._update_daily_nutrition_summary(meal_request.user_id)
            
            # Obtener la comida completa con totales calculados
            return await self.get_consumed_meal_by_id(consumed_meal_id)
            
        except Exception as e:
            logger.error(f"Error registrando comida consumida: {str(e)}")
            return None
    
    async def _add_consumed_meal_ingredient(
        self,
        consumed_meal_id: str,
        food_id: str,
        quantity_grams: float,
        notes: Optional[str] = None,
        was_planned: bool = False
    ) -> bool:
        """Agregar un ingrediente a una comida consumida"""
        try:
            ingredient_data = {
                'consumed_meal_id': consumed_meal_id,
                'food_id': food_id,
                'quantity_grams': quantity_grams,
                'notes': notes,
                'was_planned': was_planned
            }
            
            result = self.supabase.table('consumed_meal_ingredients').insert(ingredient_data).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error agregando ingrediente a comida consumida: {str(e)}")
            return False
    
    async def get_consumed_meal_by_id(self, consumed_meal_id: str) -> Optional[ConsumedMeal]:
        """Obtener una comida consumida por ID"""
        try:
            result = self.supabase.table('consumed_meals').select('*').eq(
                'id', consumed_meal_id
            ).execute()
            
            if result.data:
                return ConsumedMeal(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo comida consumida {consumed_meal_id}: {str(e)}")
            return None
    
    async def get_today_consumed_meals(self, user_id: str, target_date: Optional[date] = None) -> List[ConsumedMeal]:
        """Obtener comidas consumidas para una fecha específica"""
        try:
            if target_date is None:
                target_date = date.today()
            
            result = self.supabase.table('consumed_meals').select('*').eq(
                'user_id', user_id
            ).eq('consumption_date', target_date.isoformat()).order('consumed_at').execute()
            
            return [ConsumedMeal(**meal_data) for meal_data in result.data]
            
        except Exception as e:
            logger.error(f"Error obteniendo comidas consumidas para usuario {user_id}: {str(e)}")
            return []
    
    # ==================== OPERACIONES DE RESUMEN NUTRICIONAL ====================
    
    async def get_daily_nutrition_summary(
        self, 
        user_id: str, 
        target_date: Optional[date] = None
    ) -> Optional[DailyNutritionSummary]:
        """Obtener resumen nutricional diario"""
        try:
            if target_date is None:
                target_date = date.today()
            
            result = self.supabase.table('daily_nutrition_summary').select('*').eq(
                'user_id', user_id
            ).eq('summary_date', target_date.isoformat()).execute()
            
            if result.data:
                return DailyNutritionSummary(**result.data[0])
            
            # Si no existe, crear uno nuevo
            return await self._create_daily_nutrition_summary(user_id, target_date)
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen nutricional para usuario {user_id}: {str(e)}")
            return None
    
    async def _create_daily_nutrition_summary(
        self, 
        user_id: str, 
        target_date: date
    ) -> Optional[DailyNutritionSummary]:
        """Crear un resumen nutricional diario inicial"""
        try:
            # Obtener objetivos del plan activo
            diet_plan = await self.get_active_diet_plan(user_id)
            
            summary_data = {
                'user_id': user_id,
                'diet_plan_id': diet_plan.id if diet_plan else None,
                'summary_date': target_date.isoformat(),
                'target_calories': diet_plan.target_calories if diet_plan else 2000,
                'target_protein_g': float(diet_plan.target_protein_g) if diet_plan else 150,
                'target_carbs_g': float(diet_plan.target_carbs_g) if diet_plan else 200,
                'target_fat_g': float(diet_plan.target_fat_g) if diet_plan else 70,
                'consumed_calories': 0,
                'consumed_protein_g': 0,
                'consumed_carbs_g': 0,
                'consumed_fat_g': 0,
                'consumed_fiber_g': 0,
                'calorie_deficit_surplus': 0,
                'adherence_percentage': 0,
                'meals_completed': 0,
                'meals_planned': 5 if diet_plan else 3
            }
            
            result = self.supabase.table('daily_nutrition_summary').insert(summary_data).execute()
            
            if result.data:
                return DailyNutritionSummary(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error creando resumen nutricional: {str(e)}")
            return None
    
    async def _update_daily_nutrition_summary(self, user_id: str, target_date: Optional[date] = None) -> bool:
        """Actualizar el resumen nutricional diario basado en comidas consumidas"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # Obtener todas las comidas consumidas del día
            consumed_meals = await self.get_today_consumed_meals(user_id, target_date)
            
            # Calcular totales
            total_calories = sum(float(meal.total_calories) for meal in consumed_meals)
            total_protein = sum(float(meal.total_protein_g) for meal in consumed_meals)
            total_carbs = sum(float(meal.total_carbs_g) for meal in consumed_meals)
            total_fat = sum(float(meal.total_fat_g) for meal in consumed_meals)
            total_fiber = sum(float(meal.total_fiber_g) for meal in consumed_meals)
            
            # Obtener el resumen existente
            summary = await self.get_daily_nutrition_summary(user_id, target_date)
            if not summary:
                return False
            
            # Calcular déficit/superávit y adherencia
            calorie_deficit = summary.target_calories - total_calories
            adherence = min(100, (total_calories / summary.target_calories) * 100) if summary.target_calories > 0 else 0
            
            # Actualizar el resumen
            update_data = {
                'consumed_calories': total_calories,
                'consumed_protein_g': total_protein,
                'consumed_carbs_g': total_carbs,
                'consumed_fat_g': total_fat,
                'consumed_fiber_g': total_fiber,
                'calorie_deficit_surplus': calorie_deficit,
                'adherence_percentage': adherence,
                'meals_completed': len(consumed_meals),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('daily_nutrition_summary').update(update_data).eq(
                'id', summary.id
            ).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error actualizando resumen nutricional: {str(e)}")
            return False
    
    # ==================== OPERACIONES DE SUSTITUCIONES ====================
    
    async def find_food_substitutions(
        self, 
        original_food_id: str, 
        dietary_restrictions: Optional[List[str]] = None
    ) -> List[Tuple[Food, FoodSubstitution]]:
        """Encontrar sustituciones para un alimento"""
        try:
            # Buscar sustituciones directas en la tabla
            result = self.supabase.table('food_substitutions').select(
                '*, substitute_food:foods!substitute_food_id(*)'
            ).eq('original_food_id', original_food_id).execute()
            
            substitutions = []
            for sub_data in result.data:
                substitution = FoodSubstitution(
                    id=sub_data['id'],
                    original_food_id=sub_data['original_food_id'],
                    substitute_food_id=sub_data['substitute_food_id'],
                    conversion_factor=Decimal(str(sub_data['conversion_factor'])),
                    substitution_type=sub_data['substitution_type'],
                    notes=sub_data['notes'],
                    confidence_score=Decimal(str(sub_data['confidence_score'])),
                    created_at=sub_data['created_at']
                )
                
                substitute_food = Food(**sub_data['substitute_food'])
                
                # Filtrar por restricciones dietéticas si se proporcionan
                if dietary_restrictions:
                    if self._food_meets_dietary_restrictions(substitute_food, dietary_restrictions):
                        substitutions.append((substitute_food, substitution))
                else:
                    substitutions.append((substitute_food, substitution))
            
            return substitutions
            
        except Exception as e:
            logger.error(f"Error buscando sustituciones para alimento {original_food_id}: {str(e)}")
            return []
    
    def _food_meets_dietary_restrictions(self, food: Food, restrictions: List[str]) -> bool:
        """Verificar si un alimento cumple con las restricciones dietéticas"""
        restriction_checks = {
            'vegetariano': food.is_vegetarian,
            'vegano': food.is_vegan,
            'sin_gluten': food.is_gluten_free,
            'sin_lactosa': food.is_dairy_free,
            'bajo_carbohidratos': food.is_low_carb
        }
        
        for restriction in restrictions:
            if restriction in restriction_checks:
                if not restriction_checks[restriction]:
                    return False
        
        return True
    
    # ==================== OPERACIONES DE ANÁLISIS ====================
    
    async def calculate_macro_balance_score(self, user_id: str, target_date: Optional[date] = None) -> float:
        """Calcular puntuación de balance de macronutrientes (0.0 - 1.0)"""
        try:
            summary = await self.get_daily_nutrition_summary(user_id, target_date)
            if not summary:
                return 0.0
            
            # Calcular desviaciones de los objetivos (en porcentaje)
            protein_deviation = abs(float(summary.consumed_protein_g) - float(summary.target_protein_g)) / float(summary.target_protein_g) if summary.target_protein_g > 0 else 1.0
            carbs_deviation = abs(float(summary.consumed_carbs_g) - float(summary.target_carbs_g)) / float(summary.target_carbs_g) if summary.target_carbs_g > 0 else 1.0
            fat_deviation = abs(float(summary.consumed_fat_g) - float(summary.target_fat_g)) / float(summary.target_fat_g) if summary.target_fat_g > 0 else 1.0
            
            # Calcular puntuación promedio (1.0 = perfecto, 0.0 = muy desbalanceado)
            average_deviation = (protein_deviation + carbs_deviation + fat_deviation) / 3
            score = max(0.0, 1.0 - average_deviation)
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculando balance de macros para usuario {user_id}: {str(e)}")
            return 0.0
    
    async def get_calorie_deficit_status(self, user_id: str, target_date: Optional[date] = None) -> str:
        """Obtener estado del déficit calórico"""
        try:
            summary = await self.get_daily_nutrition_summary(user_id, target_date)
            if not summary:
                return 'unknown'
            
            deficit = float(summary.calorie_deficit_surplus)
            
            # Rangos para clasificar el estado
            if -100 <= deficit <= 100:  # Dentro de +/- 100 calorías del objetivo
                return 'on_track'
            elif deficit > 100:  # Más de 100 calorías por debajo del objetivo
                return 'under'
            else:  # Más de 100 calorías por encima del objetivo
                return 'over'
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de déficit calórico: {str(e)}")
            return 'unknown'

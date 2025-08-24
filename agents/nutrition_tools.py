"""
Herramientas específicas para el agente de nutrición
Incluye funciones para consultar comidas, planificar dietas y hacer ajustes nutricionales
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from repository.diet_repository import DietRepository
from domain.models import (
    MealType, FoodCategory, DietPlanType,
    CreateDietPlanRequest, LogMealRequest, GetTodayMealsRequest,
    GetNextMealRequest, AdjustDietRequest,
    TodayMealsResponse, NextMealResponse, DietAdjustmentResponse,
    NutritionAnalysisResponse, DietPlanResponse
)

logger = logging.getLogger(__name__)


class NutritionTools:
    """Herramientas para el agente de nutrición"""
    
    def __init__(self):
        self.diet_repo = DietRepository()
    
    async def get_today_meals(self, user_id: str, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener las comidas programadas para hoy y el progreso nutricional
        
        Args:
            user_id: ID del usuario
            target_date: Fecha objetivo en formato YYYY-MM-DD (opcional, por defecto hoy)
        
        Returns:
            Dict con comidas planificadas, consumidas y resumen nutricional (valores en kcal)
        """
        try:
            # Convertir fecha si se proporciona
            parsed_date = None
            if target_date:
                try:
                    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                except ValueError:
                    parsed_date = date.today()
            else:
                parsed_date = date.today()
            
            # Obtener comidas planificadas
            planned_meals = await self.diet_repo.get_today_planned_meals(user_id, parsed_date)
            
            # Obtener comidas consumidas
            consumed_meals = await self.diet_repo.get_today_consumed_meals(user_id, parsed_date)
            
            # Obtener resumen nutricional
            nutrition_summary = await self.diet_repo.get_daily_nutrition_summary(user_id, parsed_date)
            
            # Organizar comidas por tipo
            planned_by_type = {meal.meal_type.value: meal for meal in planned_meals}
            consumed_by_type = {}
            for meal in consumed_meals:
                if meal.meal_type.value not in consumed_by_type:
                    consumed_by_type[meal.meal_type.value] = []
                consumed_by_type[meal.meal_type.value].append(meal)
            
            # Calcular estadísticas
            total_planned_calories = sum(meal.target_calories for meal in planned_meals)
            total_consumed_calories = float(nutrition_summary.consumed_calories) if nutrition_summary else 0
            
            # Determinar estado del día
            completion_status = "on_track"
            if nutrition_summary:
                deficit = float(nutrition_summary.calorie_deficit_surplus)
                if deficit > 200:
                    completion_status = "under_eating"
                elif deficit < -200:
                    completion_status = "over_eating"
            
            return {
                "success": True,
                "date": parsed_date.strftime("%Y-%m-%d"),
                "planned_meals": [
                    {
                        "id": meal.id,
                        "meal_type": meal.meal_type.value,
                        "meal_name": meal.meal_name,
                        "meal_time": meal.meal_time,
                        "target_calories": meal.target_calories,
                        "target_protein_g": float(meal.target_protein_g),
                        "target_carbs_g": float(meal.target_carbs_g),
                        "target_fat_g": float(meal.target_fat_g),
                        "preparation_instructions": meal.preparation_instructions,
                        "difficulty_level": meal.difficulty_level
                    }
                    for meal in planned_meals
                ],
                "consumed_meals": [
                    {
                        "id": meal.id,
                        "meal_type": meal.meal_type.value,
                        "meal_name": meal.meal_name,
                        "consumed_at": meal.consumed_at.strftime("%H:%M"),
                        "total_calories": float(meal.total_calories),
                        "total_protein_g": float(meal.total_protein_g),
                        "total_carbs_g": float(meal.total_carbs_g),
                        "total_fat_g": float(meal.total_fat_g),
                        "satisfaction_rating": meal.satisfaction_rating,
                        "notes": meal.notes
                    }
                    for meal in consumed_meals
                ],
                "nutrition_summary": {
                    "target_calories": nutrition_summary.target_calories if nutrition_summary else 0,  # kcal
                    "consumed_calories": float(nutrition_summary.consumed_calories) if nutrition_summary else 0,  # kcal
                    "calorie_deficit_surplus": float(nutrition_summary.calorie_deficit_surplus) if nutrition_summary else 0,  # kcal
                    "target_protein_g": float(nutrition_summary.target_protein_g) if nutrition_summary else 0,
                    "consumed_protein_g": float(nutrition_summary.consumed_protein_g) if nutrition_summary else 0,
                    "target_carbs_g": float(nutrition_summary.target_carbs_g) if nutrition_summary else 0,
                    "consumed_carbs_g": float(nutrition_summary.consumed_carbs_g) if nutrition_summary else 0,
                    "target_fat_g": float(nutrition_summary.target_fat_g) if nutrition_summary else 0,
                    "consumed_fat_g": float(nutrition_summary.consumed_fat_g) if nutrition_summary else 0,
                    "adherence_percentage": float(nutrition_summary.adherence_percentage) if nutrition_summary else 0,
                    "meals_completed": nutrition_summary.meals_completed if nutrition_summary else 0,
                    "meals_planned": nutrition_summary.meals_planned if nutrition_summary else 0
                },
                "status": completion_status,
                "pending_meals": [
                    meal_type for meal_type in planned_by_type.keys()
                    if meal_type not in consumed_by_type
                ],
                "message": f"Tienes {len(planned_meals)} comidas planificadas y {len(consumed_meals)} consumidas para {parsed_date.strftime('%d/%m/%Y')}"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo comidas del día: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo comidas: {str(e)}",
                "message": "No se pudieron obtener las comidas del día"
            }
    
    async def get_next_meal(self, user_id: str) -> Dict[str, Any]:
        """
        Obtener la siguiente comida programada según la hora actual
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Dict con información de la siguiente comida y tiempo restante
        """
        try:
            next_meal, time_until_next = await self.diet_repo.get_next_planned_meal(user_id)
            
            if not next_meal:
                return {
                    "success": True,
                    "next_meal": None,
                    "message": "No hay más comidas programadas para hoy. ¡Buen trabajo completando tu plan!"
                }
            
            # Obtener ingredientes de la comida (si existen)
            ingredients = await self._get_meal_ingredients(next_meal.id)
            
            # Formatear tiempo restante
            time_message = ""
            if time_until_next is not None:
                hours = time_until_next // 60
                minutes = time_until_next % 60
                
                if hours > 0:
                    time_message = f"en {hours}h {minutes}min"
                elif minutes > 0:
                    time_message = f"en {minutes} minutos"
                else:
                    time_message = "¡Ahora!"
            
            return {
                "success": True,
                "next_meal": {
                    "id": next_meal.id,
                    "meal_type": next_meal.meal_type.value,
                    "meal_name": next_meal.meal_name,
                    "meal_time": next_meal.meal_time,
                    "target_calories": next_meal.target_calories,
                    "target_protein_g": float(next_meal.target_protein_g),
                    "target_carbs_g": float(next_meal.target_carbs_g),
                    "target_fat_g": float(next_meal.target_fat_g),
                    "preparation_instructions": next_meal.preparation_instructions,
                    "cooking_time_minutes": next_meal.cooking_time_minutes,
                    "difficulty_level": next_meal.difficulty_level,
                    "ingredients": ingredients
                },
                "time_until_next_meal_minutes": time_until_next,
                "time_message": time_message,
                "message": f"Tu siguiente comida es {next_meal.meal_name} ({next_meal.meal_type.value}) programada para las {next_meal.meal_time} {time_message}"
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo siguiente comida: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo siguiente comida: {str(e)}",
                "message": "No se pudo obtener información de la siguiente comida"
            }
    
    async def _get_meal_ingredients(self, planned_meal_id: str) -> List[Dict[str, Any]]:
        """Obtener ingredientes de una comida planificada"""
        try:
            # Nota: Esta función necesitaría implementarse en el repository
            # Por ahora retornamos una lista vacía
            return []
        except Exception as e:
            logger.error(f"Error obteniendo ingredientes: {str(e)}")
            return []
    
    async def analyze_nutrition_status(self, user_id: str, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Analizar el estado nutricional actual y dar recomendaciones
        
        Args:
            user_id: ID del usuario
            target_date: Fecha objetivo (opcional)
        
        Returns:
            Dict con análisis nutricional y recomendaciones (valores en kcal)
        """
        try:
            # Convertir fecha si se proporciona
            parsed_date = None
            if target_date:
                try:
                    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                except ValueError:
                    parsed_date = date.today()
            else:
                parsed_date = date.today()
            
            # Obtener resumen nutricional
            summary = await self.diet_repo.get_daily_nutrition_summary(user_id, parsed_date)
            if not summary:
                return {
                    "success": False,
                    "message": "No se encontró plan de dieta activo"
                }
            
            # Calcular métricas adicionales
            macro_balance_score = await self.diet_repo.calculate_macro_balance_score(user_id, parsed_date)
            calorie_status = await self.diet_repo.get_calorie_deficit_status(user_id, parsed_date)
            
            # Generar recomendaciones
            recommendations = await self._generate_nutrition_recommendations(summary, macro_balance_score)
            
            # Calcular porcentajes de macros
            total_consumed_calories = float(summary.consumed_calories)
            macro_percentages = {
                "protein_percent": 0,
                "carbs_percent": 0,
                "fat_percent": 0
            }
            
            if total_consumed_calories > 0:
                protein_calories = float(summary.consumed_protein_g) * 4  # 4 kcal/g protein
                carbs_calories = float(summary.consumed_carbs_g) * 4      # 4 kcal/g carbohydrates  
                fat_calories = float(summary.consumed_fat_g) * 9          # 9 kcal/g fat
                
                macro_percentages = {
                    "protein_percent": round((protein_calories / total_consumed_calories) * 100, 1),
                    "carbs_percent": round((carbs_calories / total_consumed_calories) * 100, 1),
                    "fat_percent": round((fat_calories / total_consumed_calories) * 100, 1)
                }
            
            return {
                "success": True,
                "date": parsed_date.strftime("%Y-%m-%d"),
                "daily_summary": {
                    "target_calories": summary.target_calories,  # kcal
                    "consumed_calories": float(summary.consumed_calories),  # kcal
                    "remaining_calories": summary.target_calories - float(summary.consumed_calories),  # kcal
                    "calorie_deficit_surplus": float(summary.calorie_deficit_surplus),  # kcal
                    "adherence_percentage": float(summary.adherence_percentage),
                    "meals_completed": summary.meals_completed,
                    "meals_planned": summary.meals_planned,
                    "macros": {
                        "protein": {
                            "target_g": float(summary.target_protein_g),
                            "consumed_g": float(summary.consumed_protein_g),
                            "remaining_g": float(summary.target_protein_g) - float(summary.consumed_protein_g),
                            "percentage_of_calories": macro_percentages["protein_percent"]
                        },
                        "carbs": {
                            "target_g": float(summary.target_carbs_g),
                            "consumed_g": float(summary.consumed_carbs_g),
                            "remaining_g": float(summary.target_carbs_g) - float(summary.consumed_carbs_g),
                            "percentage_of_calories": macro_percentages["carbs_percent"]
                        },
                        "fat": {
                            "target_g": float(summary.target_fat_g),
                            "consumed_g": float(summary.consumed_fat_g),
                            "remaining_g": float(summary.target_fat_g) - float(summary.consumed_fat_g),
                            "percentage_of_calories": macro_percentages["fat_percent"]
                        }
                    },
                    "fiber_g": float(summary.consumed_fiber_g)
                },
                "analysis": {
                    "calorie_deficit_status": calorie_status,
                    "macro_balance_score": round(macro_balance_score, 2),
                    "overall_adherence": float(summary.adherence_percentage)
                },
                "recommendations": recommendations,
                "message": f"Análisis nutricional para {parsed_date.strftime('%d/%m/%Y')}: {calorie_status.replace('_', ' ').title()}"
            }
            
        except Exception as e:
            logger.error(f"Error analizando estado nutricional: {str(e)}")
            return {
                "success": False,
                "error": f"Error en análisis: {str(e)}",
                "message": "No se pudo realizar el análisis nutricional"
            }
    
    async def _generate_nutrition_recommendations(
        self, 
        summary, 
        macro_balance_score: float
    ) -> List[str]:
        """Generar recomendaciones nutricionales personalizadas"""
        recommendations = []
        
        try:
            # Análisis calórico
            calorie_deficit = float(summary.calorie_deficit_surplus)
            if calorie_deficit > 300:
                recommendations.append("Estás consumiendo pocas kcal. Considera agregar una colación saludable.")
            elif calorie_deficit < -300:
                recommendations.append("Has excedido tu objetivo de kcal. Trata de reducir las porciones en la próxima comida.")
            elif -100 <= calorie_deficit <= 100:
                recommendations.append("¡Excelente! Estás muy cerca de tu objetivo de kcal.")
            
            # Análisis de proteínas
            protein_deficit = float(summary.target_protein_g) - float(summary.consumed_protein_g)
            if protein_deficit > 20:
                recommendations.append("Te falta proteína para alcanzar tu objetivo. Considera agregar pollo, pescado, huevos o legumbres.")
            elif protein_deficit < -10:
                recommendations.append("Has consumido más proteína de la necesaria, ¡excelente para la recuperación muscular!")
            
            # Análisis de balance de macros
            if macro_balance_score < 0.6:
                recommendations.append("Tus macronutrientes están desbalanceados. Intenta incluir una variedad de alimentos en tus comidas.")
            elif macro_balance_score > 0.8:
                recommendations.append("¡Perfecto balance de macronutrientes! Mantén esta distribución.")
            
            # Análisis de adherencia
            adherence = float(summary.adherence_percentage)
            if adherence < 70:
                recommendations.append("Tu adherencia al plan está baja. Intenta preparar las comidas con anticipación.")
            elif adherence > 90:
                recommendations.append("¡Excelente adherencia al plan! Sigue así.")
            
            # Recomendaciones de fibra
            if float(summary.consumed_fiber_g) < 20:
                recommendations.append("Aumenta tu consumo de fibra incluyendo más verduras, frutas y granos integrales.")
            
            # Si no hay recomendaciones específicas, dar una general
            if not recommendations:
                recommendations.append("Continúa siguiendo tu plan nutricional. ¡Vas por buen camino!")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return ["Continúa siguiendo tu plan nutricional."]
    
    async def search_foods(
        self, 
        query: str, 
        category: Optional[str] = None,
        dietary_filters: Optional[Dict[str, bool]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Buscar alimentos en la base de datos
        
        Args:
            query: Término de búsqueda
            category: Categoría de alimento (opcional)
            dietary_filters: Filtros dietéticos (vegetariano, vegano, etc.)
            limit: Límite de resultados
        
        Returns:
            Dict con lista de alimentos encontrados
        """
        try:
            # Convertir categoría string a enum si se proporciona
            food_category = None
            if category:
                try:
                    food_category = FoodCategory(category.lower())
                except ValueError:
                    logger.warning(f"Categoría inválida: {category}")
            
            # Buscar alimentos
            foods = await self.diet_repo.search_foods(
                query=query,
                category=food_category,
                dietary_filters=dietary_filters,
                limit=limit
            )
            
            return {
                "success": True,
                "foods": [
                    {
                        "id": food.id,
                        "name": food.name,
                        "name_es": food.name_es,
                        "category": food.category.value,
                        "calories_per_100g": float(food.calories_per_100g),  # kcal per 100g
                        "protein_per_100g": float(food.protein_per_100g),
                        "carbs_per_100g": float(food.carbs_per_100g),
                        "fat_per_100g": float(food.fat_per_100g),
                        "fiber_per_100g": float(food.fiber_per_100g),
                        "common_serving_size_g": float(food.common_serving_size_g) if food.common_serving_size_g else None,
                        "serving_description": food.serving_description,
                        "is_vegetarian": food.is_vegetarian,
                        "is_vegan": food.is_vegan,
                        "is_gluten_free": food.is_gluten_free,
                        "is_dairy_free": food.is_dairy_free
                    }
                    for food in foods
                ],
                "total_found": len(foods),
                "message": f"Se encontraron {len(foods)} alimentos para '{query}'"
            }
            
        except Exception as e:
            logger.error(f"Error buscando alimentos: {str(e)}")
            return {
                "success": False,
                "foods": [],
                "error": f"Error en búsqueda: {str(e)}",
                "message": "No se pudieron buscar alimentos"
            }
    
    async def log_meal(
        self,
        user_id: str,
        meal_type: str,
        meal_name: str,
        ingredients: List[Dict[str, Any]],
        notes: Optional[str] = None,
        satisfaction_rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Registrar una comida consumida
        
        Args:
            user_id: ID del usuario
            meal_type: Tipo de comida (desayuno, almuerzo, etc.)
            meal_name: Nombre de la comida
            ingredients: Lista de ingredientes con food_id y quantity_grams
            notes: Notas adicionales
            satisfaction_rating: Calificación de satisfacción (1-5)
        
        Returns:
            Dict con resultado del registro
        """
        try:
            # Convertir meal_type string a enum
            try:
                meal_type_enum = MealType(meal_type.lower())
            except ValueError:
                return {
                    "success": False,
                    "error": f"Tipo de comida inválido: {meal_type}",
                    "message": "Tipo de comida no reconocido"
                }
            
            # Crear request
            meal_request = LogMealRequest(
                user_id=user_id,
                meal_type=meal_type_enum,
                meal_name=meal_name,
                ingredients=ingredients,
                notes=notes,
                satisfaction_rating=satisfaction_rating
            )
            
            # Registrar comida
            consumed_meal = await self.diet_repo.log_consumed_meal(meal_request)
            
            if consumed_meal:
                return {
                    "success": True,
                    "consumed_meal": {
                        "id": consumed_meal.id,
                        "meal_name": consumed_meal.meal_name,
                        "meal_type": consumed_meal.meal_type.value,
                        "total_calories": float(consumed_meal.total_calories),  # kcal
                        "total_protein_g": float(consumed_meal.total_protein_g),
                        "total_carbs_g": float(consumed_meal.total_carbs_g),
                        "total_fat_g": float(consumed_meal.total_fat_g),
                        "consumed_at": consumed_meal.consumed_at.strftime("%H:%M"),
                        "satisfaction_rating": consumed_meal.satisfaction_rating
                    },
                    "message": f"Comida '{meal_name}' registrada exitosamente con {float(consumed_meal.total_calories)} kcal"
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo registrar la comida",
                    "message": "Error al guardar la comida en la base de datos"
                }
            
        except Exception as e:
            logger.error(f"Error registrando comida: {str(e)}")
            return {
                "success": False,
                "error": f"Error registrando comida: {str(e)}",
                "message": "No se pudo registrar la comida"
            }
    
    async def suggest_meal_adjustments(
        self,
        user_id: str,
        meal_type: str,
        food_changes: List[Dict[str, Any]],
        maintain_calories: bool = True
    ) -> Dict[str, Any]:
        """
        Sugerir ajustes a una comida para mantener el balance nutricional
        
        Args:
            user_id: ID del usuario
            meal_type: Tipo de comida a ajustar
            food_changes: Lista de cambios a realizar
            maintain_calories: Si mantener las calorías totales
        
        Returns:
            Dict con sugerencias de ajuste
        """
        try:
            # Esta sería una función compleja que calcularía substituciones
            # Por ahora retornamos una respuesta básica
            
            return {
                "success": True,
                "adjustments": {
                    "original_meal": meal_type,
                    "suggested_changes": [
                        "Sustituir 100g de arroz blanco por 100g de quinoa (+2g proteína, +3g fibra)",
                        "Agregar 50g de brócoli para aumentar fibra y vitaminas",
                        "Reducir aceite de 15ml a 10ml para mantener calorías objetivo"
                    ],
                    "nutrition_impact": {
                        "calorie_change": -15,  # kcal
                        "protein_change": +2.5,
                        "carbs_change": -3.2,
                        "fat_change": -0.8,
                        "fiber_change": +4.1
                    }
                },
                "message": "Se generaron sugerencias para optimizar tu comida manteniendo el objetivo de kcal"
            }
            
        except Exception as e:
            logger.error(f"Error sugiriendo ajustes: {str(e)}")
            return {
                "success": False,
                "error": f"Error generando sugerencias: {str(e)}",
                "message": "No se pudieron generar sugerencias de ajuste"
            }

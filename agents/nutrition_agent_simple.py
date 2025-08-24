"""
Agente especializado en nutrición y dietas (versión simplificada)
Maneja consultas sobre comidas, planificación nutricional y seguimiento de dietas
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from .base_agent import BaseAgent
from .nutrition_tools import NutritionTools
from domain.models import User

logger = logging.getLogger(__name__)


class NutritionAgent(BaseAgent):
    """Agente especializado en nutrición y dietas"""
    
    def __init__(self):
        system_prompt = """
        Eres un nutricionista virtual especializado en ayudar con dietas y alimentación.
        Puedes consultar comidas del día, analizar progreso nutricional, buscar alimentos,
        y dar recomendaciones personalizadas para cumplir objetivos nutricionales.
        """
        super().__init__(
            name="nutrition_agent",
            system_prompt=system_prompt
        )
        self.nutrition_tools = NutritionTools()
    
    def can_handle(self, message: str, context: Dict[str, Any]) -> bool:
        """Determinar si este agente puede manejar el mensaje"""
        
        nutrition_keywords = [
            'comida', 'comidas', 'desayuno', 'almuerzo', 'cena', 'dieta', 'nutrición',
            'calorias', 'calorías', 'macros', 'proteinas', 'siguiente comida',
            'que como hoy', 'plan de hoy', 'deficit', 'alimento', 'registrar'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in nutrition_keywords)
    
    async def process_message(self, message: str, user: User, context: Dict[str, Any]) -> str:
        """Procesar mensaje relacionado con nutrición"""
        
        try:
            message_lower = message.lower()
            user_id = user.id
            
            # Comidas del día
            if any(phrase in message_lower for phrase in [
                'comidas de hoy', 'que como hoy', 'plan de hoy'
            ]):
                result = await self.nutrition_tools.get_today_meals(user_id)
                return self._format_today_meals(result)
            
            # Siguiente comida
            elif any(phrase in message_lower for phrase in [
                'siguiente comida', 'próxima comida', 'cuándo como'
            ]):
                result = await self.nutrition_tools.get_next_meal(user_id)
                return self._format_next_meal(result)
            
            # Análisis nutricional
            elif any(phrase in message_lower for phrase in [
                'análisis', 'progreso', 'cómo voy', 'deficit'
            ]):
                result = await self.nutrition_tools.analyze_nutrition_status(user_id)
                return self._format_nutrition_analysis(result)
            
            # Búsqueda de alimentos
            elif 'buscar' in message_lower:
                query = self._extract_search_query(message)
                if query:
                    result = await self.nutrition_tools.search_foods(query, limit=5)
                    return self._format_food_search(result, query)
                else:
                    return "¿Qué alimento te gustaría buscar?"
            
            else:
                return self._provide_nutrition_help(user)
            
        except Exception as e:
            logger.error(f"Error en nutrition agent: {str(e)}")
            return "Lo siento, hubo un error. ¿Podrías intentar de nuevo?"
    
    def _format_today_meals(self, result: Dict[str, Any]) -> str:
        """Formatear respuesta de comidas del día"""
        if not result["success"]:
            return f"❌ {result.get('message', 'No se pudieron obtener las comidas')}"
        
        response = f"🗓️ **Comidas para {result['date']}**\n\n"
        
        if result["planned_meals"]:
            response += "📅 **Programadas:**\n"
            for meal in result["planned_meals"]:
                emoji = self._get_meal_emoji(meal["meal_type"])
                response += f"{emoji} {meal['meal_name']} ({meal['meal_time']}) - {meal['target_calories']} cal\n"
        
        if result["consumed_meals"]:
            response += "\n✅ **Consumidas:**\n"
            for meal in result["consumed_meals"]:
                emoji = self._get_meal_emoji(meal["meal_type"])
                response += f"{emoji} {meal['meal_name']} - {meal['total_calories']} cal\n"
        
        nutrition = result["nutrition_summary"]
        response += f"\n📊 **Resumen:** {nutrition['consumed_calories']}/{nutrition['target_calories']} cal"
        
        return response
    
    def _format_next_meal(self, result: Dict[str, Any]) -> str:
        """Formatear respuesta de siguiente comida"""
        if not result["success"] or not result["next_meal"]:
            return "🎉 ¡No tienes más comidas programadas para hoy!"
        
        meal = result["next_meal"]
        emoji = self._get_meal_emoji(meal["meal_type"])
        
        response = f"{emoji} **Siguiente: {meal['meal_name']}**\n"
        response += f"🕐 Horario: {meal['meal_time']} {result.get('time_message', '')}\n"
        response += f"🔥 Calorías: {meal['target_calories']} cal\n"
        
        return response
    
    def _format_nutrition_analysis(self, result: Dict[str, Any]) -> str:
        """Formatear análisis nutricional"""
        if not result["success"]:
            return "❌ No se pudo realizar el análisis nutricional"
        
        daily = result["daily_summary"]
        response = f"📊 **Análisis Nutricional**\n\n"
        response += f"🔥 Calorías: {daily['consumed_calories']:.0f}/{daily['target_calories']}\n"
        
        deficit = daily["calorie_deficit_surplus"]
        if deficit > 0:
            response += f"✅ Déficit: {deficit:.0f} cal\n"
        elif deficit < 0:
            response += f"⚠️ Exceso: {abs(deficit):.0f} cal\n"
        
        response += f"📈 Adherencia: {daily['adherence_percentage']:.1f}%\n"
        
        if result["recommendations"]:
            response += "\n💡 **Recomendaciones:**\n"
            for rec in result["recommendations"][:3]:
                response += f"• {rec}\n"
        
        return response
    
    def _format_food_search(self, result: Dict[str, Any], query: str) -> str:
        """Formatear búsqueda de alimentos"""
        if not result["success"] or not result["foods"]:
            return f"❌ No se encontraron alimentos para '{query}'"
        
        response = f"🔍 **Resultados para '{query}':**\n\n"
        
        for food in result["foods"][:5]:
            response += f"• **{food['name_es']}** - {food['calories_per_100g']:.0f} cal/100g\n"
            response += f"  Proteína: {food['protein_per_100g']:.1f}g | Carbos: {food['carbs_per_100g']:.1f}g\n\n"
        
        return response
    
    def _extract_search_query(self, message: str) -> Optional[str]:
        """Extraer término de búsqueda"""
        words = message.lower().split()
        try:
            idx = words.index('buscar')
            if idx + 1 < len(words):
                return ' '.join(words[idx + 1:idx + 3])  # Máximo 2 palabras
        except ValueError:
            pass
        return None
    
    def _get_meal_emoji(self, meal_type: str) -> str:
        """Emoji según tipo de comida"""
        emojis = {
            "desayuno": "🌅",
            "colacion_1": "🍎", 
            "almuerzo": "🍽️",
            "colacion_2": "🥨",
            "cena": "🌙"
        }
        return emojis.get(meal_type, "🍽️")
    
    def _provide_nutrition_help(self, user: User) -> str:
        """Ayuda general de nutrición"""
        return f"""
👋 ¡Hola {user.name or 'Usuario'}! Soy tu nutricionista virtual.

🥗 **Puedo ayudarte con:**
• "¿Qué comidas tengo hoy?"
• "¿Cuál es mi siguiente comida?"
• "Análisis de mi progreso nutricional"
• "Buscar alimentos ricos en proteína"

💡 **¿En qué te puedo ayudar con tu alimentación?**
        """

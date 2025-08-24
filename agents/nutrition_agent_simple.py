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
    
    def __init__(self, user_id: Optional[str] = None):
        system_prompt = """
        Eres un nutricionista virtual especializado en ayudar con dietas y alimentación.
        Puedes consultar comidas del día, analizar progreso nutricional, buscar alimentos,
        y dar recomendaciones personalizadas para cumplir objetivos nutricionales.
        """
        super().__init__(
            name="nutrition_agent",
            system_prompt=system_prompt,
            user_id=user_id
        )
        self.nutrition_tools = NutritionTools()
        self.user_id = user_id
    
    def can_handle(self, message: str, context: Dict[str, Any]) -> bool:
        """Determinar si este agente puede manejar el mensaje"""
        
        nutrition_keywords = [
            'comida', 'comidas', 'desayuno', 'almuerzo', 'cena', 'dieta', 'nutrición',
            'calorias', 'calorías', 'macros', 'proteinas', 'siguiente comida',
            'que como hoy', 'plan de hoy', 'deficit', 'alimento', 'registrar',
            'plan de dieta', 'plan activo', 'dieta activa', 'mi plan', 'plan que tengo',
            'dieta que tengo', 'mi dieta', 'plan actual', 'dieta actual'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in nutrition_keywords)
    
    async def process_message(self, message: str, user: User, context: Dict[str, Any]) -> str:
        """Procesar mensaje relacionado con nutrición"""
        
        try:
            user_id = user.id
            
            # Determinar si debemos usar herramientas o responder directamente
            if self._should_use_tools(message):
                logger.info(f"🔧 Usando herramientas para: '{message[:50]}...'")
                return await self._process_with_tools(message, user_id, context)
            else:
                logger.info(f"💬 Respuesta conversacional para: '{message[:50]}...'")
                return await self._process_general_query(message, user, context)
            
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
    
    def _format_diet_plan(self, result: Dict[str, Any]) -> str:
        """Formatear respuesta del plan de dieta activo"""
        if not result["success"]:
            return f"❌ {result.get('message', 'No se pudo obtener el plan de dieta')}"
        
        if not result.get("planned_meals"):
            return "📋 No tienes un plan de dieta activo. ¿Te gustaría que te ayude a crear uno?"
        
        # Obtener información del plan desde nutrition_summary
        nutrition_summary = result.get("nutrition_summary", {})
        target_calories = nutrition_summary.get("target_calories", 0)
        
        response = f"📋 **Tu Plan de Dieta Activo**\n\n"
        response += f"🎯 **Objetivo:** {target_calories} calorías diarias\n"
        response += f"📅 **Fecha:** {result['date']}\n\n"
        
        response += "🍽️ **Comidas Planificadas:**\n"
        
        # Agrupar comidas por tipo y ordenar por hora
        planned_meals = sorted(result["planned_meals"], key=lambda x: x["meal_time"])
        
        total_planned_calories = 0
        for meal in planned_meals:
            meal_type_emoji = {
                "desayuno": "🌅",
                "colacion_1": "☀️", 
                "almuerzo": "🍽️",
                "colacion_2": "🌇",
                "cena": "🌙"
            }.get(meal["meal_type"], "🍴")
            
            response += f"{meal_type_emoji} **{meal['meal_time']}** - {meal['meal_name']}\n"
            response += f"   📊 {meal['target_calories']} cal | "
            response += f"🥩 {meal['target_protein_g']:.1f}g proteína | "
            response += f"🍞 {meal['target_carbs_g']:.1f}g carbos | "
            response += f"🥑 {meal['target_fat_g']:.1f}g grasas\n"
            
            if meal.get("preparation_instructions"):
                response += f"   📝 {meal['preparation_instructions'][:100]}...\n"
            response += "\n"
            
            total_planned_calories += meal['target_calories']
        
        # Resumen del plan
        response += f"📊 **Resumen del Plan:**\n"
        response += f"🔥 Total de calorías planificadas: {total_planned_calories} cal\n"
        response += f"🎯 Objetivo calórico: {target_calories} cal\n"
        
        # Estado actual
        consumed_calories = nutrition_summary.get("consumed_calories", 0)
        if consumed_calories > 0:
            response += f"✅ Calorías consumidas hoy: {consumed_calories:.0f} cal\n"
            remaining = target_calories - consumed_calories
            if remaining > 0:
                response += f"⏳ Faltan por consumir: {remaining:.0f} cal\n"
            else:
                response += f"🎯 ¡Objetivo alcanzado! Exceso: {abs(remaining):.0f} cal\n"
        
        response += f"\n💡 **Próximos pasos:**\n"
        response += f"• Pregunta '¿Cuál es mi siguiente comida?' para ver detalles\n"
        response += f"• Pregunta '¿Cómo voy con mi dieta?' para análisis completo\n"
        
        return response
    
    def _should_use_tools(self, message: str) -> bool:
        """
        Determinar si el mensaje requiere usar herramientas específicas de nutrición
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            True si debe usar herramientas, False si es consulta general
        """
        message_lower = message.lower()
        logger.info(f"🔍 Analizando mensaje para herramientas: '{message[:50]}...'") 
        
        # Palabras clave que indican uso de herramientas de consulta
        tool_keywords = [
            # Consultas específicas sobre comidas/plan
            "comidas de hoy", "que como hoy", "plan de hoy", "comidas programadas",
            "siguiente comida", "próxima comida", "cuándo como", "cuándo debo comer",
            "plan de dieta", "plan activo", "dieta activa", "mi plan", "plan que tengo",
            "dieta que tengo", "mi dieta", "plan actual", "dieta actual",
            
            # Análisis y progreso
            "análisis", "progreso", "cómo voy", "deficit", "adherencia", "resumen",
            "estado nutricional", "balance", "macros consumidos",
            
            # Búsqueda y registro
            "buscar alimento", "buscar comida", "buscar ingrediente",
            "registrar comida", "anotar comida", "logear", "consumí"
        ]
        
        # Palabras que indican consultas generales (NO usar herramientas)
        general_keywords = [
            "cómo hacer", "cómo preparar", "receta", "consejos", "beneficios",
            "qué es", "para qué sirve", "cuánto debería", "recomendaciones",
            "plan para", "dieta para", "rutina para", "crea una", "diseña",
            "suplementos", "vitaminas", "nutrientes", "ayuda con"
        ]
        
        # Verificar palabras generales primero (tienen prioridad)
        for keyword in general_keywords:
            if keyword in message_lower:
                return False
        
        # Verificar palabras de herramientas
        for keyword in tool_keywords:
            if keyword in message_lower:
                logger.info(f"✅ Detectado keyword para herramientas: '{keyword}'")
                return True
        
        # Frases de acción específica
        action_phrases = ["dame", "muéstrame", "dime", "necesito saber", "quiero ver"]
        specific_targets = ["plan", "comidas", "progreso", "análisis", "siguiente"]
        
        for phrase in action_phrases:
            if phrase in message_lower:
                for target in specific_targets:
                    if target in message_lower:
                        logger.info(f"✅ Detectado frase de acción: '{phrase}' + '{target}'")
                        return True
        
        # Por defecto, no usar herramientas para consultas ambiguas
        logger.info(f"❌ No se detectó intent para herramientas - respuesta conversacional")
        return False
    
    async def _process_with_tools(self, message: str, user_id: str, context: Dict[str, Any]) -> str:
        """Procesar mensaje usando herramientas específicas"""
        message_lower = message.lower()
        logger.info(f"🔧 Iniciando procesamiento con herramientas para user_id: {user_id}")
        
        # Detectar tipo de consulta y usar la herramienta apropiada
        if any(phrase in message_lower for phrase in [
            'comidas de hoy', 'que como hoy', 'plan de hoy', 'comidas programadas'
        ]):
            result = await self.nutrition_tools.get_today_meals(user_id)
            return self._format_today_meals(result)
        
        elif any(phrase in message_lower for phrase in [
            'siguiente comida', 'próxima comida', 'cuándo como', 'cuándo debo comer'
        ]):
            result = await self.nutrition_tools.get_next_meal(user_id)
            return self._format_next_meal(result)
        
        elif any(phrase in message_lower for phrase in [
            'plan de dieta', 'plan activo', 'dieta activa', 'mi plan', 'plan que tengo',
            'dieta que tengo', 'mi dieta', 'plan actual', 'dieta actual'
        ]):
            logger.info(f"📋 Consultando plan de dieta para user_id: {user_id}")
            result = await self.nutrition_tools.get_today_meals(user_id)
            return self._format_diet_plan(result)
        
        elif any(phrase in message_lower for phrase in [
            'análisis', 'progreso', 'cómo voy', 'deficit', 'adherencia', 'resumen',
            'estado nutricional', 'balance'
        ]):
            result = await self.nutrition_tools.analyze_nutrition_status(user_id)
            return self._format_nutrition_analysis(result)
        
        elif any(phrase in message_lower for phrase in ['buscar']):
            query = self._extract_search_query(message)
            if query:
                result = await self.nutrition_tools.search_foods(query, limit=5)
                return self._format_food_search(result, query)
            else:
                return "¿Qué alimento te gustaría buscar?"
        
        else:
            # Si llegamos aquí, es una consulta específica pero no reconocida
            # Usar la herramienta más apropiada por defecto
            result = await self.nutrition_tools.get_today_meals(user_id)
            return self._format_today_meals(result)
    
    async def _process_general_query(self, message: str, user: User, context: Dict[str, Any]) -> str:
        """Procesar consulta general sin herramientas específicas"""
        # Delegar al agente base para respuesta conversacional
        return await self.process(message, context)

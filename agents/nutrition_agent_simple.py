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
        ¡Hola! Soy Luna, tu coach de nutrición en FaiTracker 🌙✨
        
        Soy una nutricionista certificada especializada en alimentación saludable y nutrición deportiva.
        Mi misión es ayudarte a alcanzar tus objetivos a través de una alimentación inteligente y balanceada.
        
        🥗 En FaiTracker puedo ayudarte con:
        - 📊 Consultar tus comidas del día y progreso nutricional
        - 🔍 Registrar automáticamente lo que comes con análisis de macros
        - 📈 Analizar tu adherencia al plan y darte recomendaciones personalizadas
        - 🍎 Buscar alimentos en nuestra extensa base de datos nutricional
        - 🎯 Ajustar tu plan según tus objetivos (pérdida de peso, ganancia muscular, etc.)
        
        💫 Mi enfoque como Luna:
        - 🎯 Personalizo cada recomendación según tus objetivos específicos
        - 🔬 Base mis consejos en evidencia científica actualizada
        - 💝 Soy comprensiva - entiendo que cada persona tiene su ritmo
        - 🌟 Te motivo sin juzgar, celebrando cada pequeño progreso
        - 🥗 Hago que la alimentación saludable sea práctica y deliciosa
        - 📱 Uso la tecnología de FaiTracker para hacer tu seguimiento más fácil
        
        🚀 HERRAMIENTAS FAITRACKER que uso para ti:
        - Registro inteligente de comidas con análisis automático de macros
        - Consulta de tu plan de dieta personalizado
        - Análisis de progreso nutricional en tiempo real
        - Base de datos de alimentos con información nutricional precisa
        - Recomendaciones personalizadas basadas en tu adherencia
        
        ⚠️ IMPORTANTE: Mis recomendaciones complementan, no reemplazan, 
        la consulta con un profesional de la salud para condiciones específicas.
        
        ¡Estoy aquí para hacer tu viaje nutricional más fácil y exitoso! 🌟
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
¡Hola! Soy Luna 🌙, tu coach de nutrición en FaiTracker ✨

🥗 **Puedo ayudarte con:**
• "¿Qué comidas tengo hoy?" - Ver tu plan del día
• "¿Cuál es mi siguiente comida?" - Próxima comida programada
• "Acabo de comer..." - Registrar comidas automáticamente
• "¿Cómo voy con mi dieta?" - Análisis de tu progreso
• "Buscar alimentos" - Consultar nuestra base de datos

🌟 **¿En qué puedo ayudarte hoy con tu alimentación?**
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
            "registrar comida", "anotar comida", "logear", "consumí",
            
            # Creación y cambio de dietas
            "crear dieta", "nueva dieta", "cambiar dieta", "cambiar plan",
            "quiero una dieta", "quiero crear", "necesito una dieta", "hacer una dieta",
            "diseñar dieta", "plan personalizado", "activar dieta", "crear una dieta",
            
            # Registro de comidas (frases más naturales)
            "acabo de comer", "comí", "desayuné", "almorcé", "cené",
            "me comí", "tomé", "bebí", "en mi desayuno", "en mi almuerzo", 
            "en mi cena", "para desayunar", "para almorzar", "para cenar",
            "hice mi desayuno", "hice mi almuerzo", "hice mi cena"
        ]
        
        # Palabras que indican consultas generales (NO usar herramientas)
        general_keywords = [
            "cómo hacer", "cómo preparar", "receta", "consejos", "beneficios",
            "qué es", "para qué sirve", "cuánto debería", "recomendaciones",
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
        
        elif any(phrase in message_lower for phrase in [
            'crear dieta', 'nueva dieta', 'cambiar dieta', 'cambiar plan',
            'quiero una dieta', 'quiero crear', 'necesito una dieta', 'hacer una dieta',
            'diseñar dieta', 'plan personalizado', 'activar dieta', 'crear una dieta'
        ]):
            logger.info(f"🎯 Detectado request de creación de dieta para user_id: {user_id}")
            return await self._handle_diet_creation_request(message, user_id)
        
        elif any(phrase in message_lower for phrase in ['buscar']):
            query = self._extract_search_query(message)
            if query:
                result = await self.nutrition_tools.search_foods(query, limit=5)
                return self._format_food_search(result, query)
            else:
                return "¿Qué alimento te gustaría buscar?"
        
        # Registro de comidas
        elif any(phrase in message_lower for phrase in [
            'acabo de comer', 'comí', 'desayuné', 'almorcé', 'cené',
            'me comí', 'en mi desayuno', 'en mi almuerzo', 'en mi cena',
            'para desayunar', 'para almorzar', 'para cenar',
            'hice mi desayuno', 'hice mi almuerzo', 'hice mi cena',
            'registrar comida', 'anotar comida', 'consumí'
        ]):
            logger.info(f"🍽️ Detectado registro de comida para user_id: {user_id}")
            return await self._process_meal_logging(message, user_id)
        
        else:
            # Si llegamos aquí, es una consulta específica pero no reconocida
            # Usar la herramienta más apropiada por defecto
            result = await self.nutrition_tools.get_today_meals(user_id)
            return self._format_today_meals(result)
    
    async def _process_meal_logging(self, message: str, user_id: str) -> str:
        """
        Procesar el registro de una comida consumida
        
        Args:
            message: Mensaje del usuario describiendo la comida
            user_id: ID del usuario
            
        Returns:
            Respuesta con el resultado del registro
        """
        try:
            logger.info(f"🍽️ Iniciando registro de comida para user_id: {user_id}")
            message_lower = message.lower()
            
            # 1. Detectar tipo de comida
            meal_type = self._detect_meal_type(message_lower)
            logger.info(f"📅 Tipo de comida detectado: {meal_type}")
            
            # 2. Parser inteligente de alimentos y cantidades
            parsed_foods = self._parse_foods_and_quantities(message)
            logger.info(f"🔍 Alimentos parseados: {len(parsed_foods)} items")
            
            if not parsed_foods:
                return "🤔 No pude identificar alimentos específicos en tu mensaje. ¿Podrías ser más específico? Por ejemplo: 'comí 2 huevos de 60g cada uno'"
            
            # 3. Mapear a base de datos y calcular macros
            meal_ingredients = await self._map_foods_to_database(parsed_foods)
            logger.info(f"🍎 Ingredientes mapeados: {len(meal_ingredients)} válidos")
            
            if not meal_ingredients:
                return "❌ No encontré esos alimentos en mi base de datos. Intenta con: huevos, avena, plátano, pollo, arroz, etc."
            
            # 4. Registrar comida en base de datos
            meal_name = self._generate_meal_name(parsed_foods)
            result = await self.nutrition_tools.log_meal(
                user_id=user_id,
                meal_type=meal_type,
                meal_name=meal_name,
                ingredients=meal_ingredients
            )
            
            if result["success"]:
                logger.info(f"✅ Comida registrada exitosamente: {result['consumed_meal']['id']}")
                return self._format_meal_logged_response(result, meal_type)
            else:
                logger.error(f"❌ Error registrando comida: {result.get('error')}")
                return f"❌ No pude registrar tu comida: {result.get('message', 'Error desconocido')}"
            
        except Exception as e:
            logger.error(f"❌ Error procesando registro de comida: {str(e)}")
            return "❌ Hubo un error registrando tu comida. Intenta de nuevo."
    
    def _detect_meal_type(self, message_lower: str) -> str:
        """Detectar el tipo de comida del mensaje"""
        if any(word in message_lower for word in ["desayuno", "desayuné", "en mi desayuno", "para desayunar"]):
            return "desayuno"
        elif any(word in message_lower for word in ["almuerzo", "almorcé", "en mi almuerzo", "para almorzar"]):
            return "almuerzo"
        elif any(word in message_lower for word in ["cena", "cené", "en mi cena", "para cenar"]):
            return "cena"
        elif any(word in message_lower for word in ["colacion", "snack", "merienda"]):
            return "colacion_1"
        else:
            return "desayuno"  # default
    
    def _parse_foods_and_quantities(self, message: str) -> List[Dict[str, Any]]:
        """
        Parser inteligente de alimentos y cantidades
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Lista de diccionarios con {name, quantity, unit}
        """
        import re
        
        message_lower = message.lower()
        parsed_foods = []
        
        # Patrones para detectar alimentos con cantidades
        patterns = [
            # "6 huevos grandes (55g)"
            r"(\d+)\s*(huevos?)\s*(?:grandes?|medianos?|pequeños?)?\s*(?:\((\d+)g?\))?",
            # "40g de avena" - Match multiple words for compound foods
            r"(\d+)g?\s*de\s*([\w\s]+?)(?:\s|$)",
            # "platano de 150g"
            r"([\w\s]+?)\s*de\s*(\d+)g?",
            # "150g platano" - But exclude common prepositions
            r"(\d+)g?\s*(?!de\s)([\w\s]+?)(?:\s|$)",
        ]
        
        # Mapeo de nombres comunes a nombres estándar
        food_mapping = {
            "huevo": "huevos", "huevos": "huevos",
            "avena": "avena", "avena cocida": "avena",
            "platano": "plátano", "plátano": "plátano", "banana": "plátano",
            "pan": "pan", "pan integral": "pan integral",
            "leche": "leche", "yogur": "yogur griego",
            "pollo": "pechuga de pollo", "pechuga": "pechuga de pollo"
        }
        
        # Lista de palabras a excluir (preposiciones, artículos, etc.)
        exclude_words = {"de", "del", "la", "el", "un", "una", "y", "con", "sin", "para", "por", "en"}
        
        for pattern in patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                food = None
                total_weight = None
                
                if len(match) == 3:  # cantidad, alimento, peso extra
                    quantity, food, extra_weight = match
                    if extra_weight:
                        total_weight = int(quantity) * int(extra_weight)
                    else:
                        total_weight = int(quantity) * 50  # peso promedio
                elif len(match) == 2:
                    first, second = match
                    if first.isdigit():
                        quantity, food = first, second
                        total_weight = int(quantity)
                    else:
                        food, quantity = first, second
                        total_weight = int(quantity)
                else:
                    continue
                
                # Limpiar el nombre del alimento
                if food:
                    food = food.strip()
                    # Excluir palabras comunes que no son alimentos
                    if food.lower() in exclude_words or len(food) < 3:
                        continue
                        
                    # Normalizar nombre del alimento
                    normalized_food = food_mapping.get(food, food)
                    
                    # Evitar duplicados
                    existing_food = next((f for f in parsed_foods if f["name"] == normalized_food), None)
                    if not existing_food:
                        parsed_foods.append({
                            "name": normalized_food,
                            "quantity": total_weight,
                            "unit": "g"
                        })
        
        # Log de lo que se parseó
        logger.info(f"🔍 Parsed foods: {parsed_foods}")
        return parsed_foods
    
    async def _map_foods_to_database(self, parsed_foods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mapear alimentos parseados a la base de datos
        
        Args:
            parsed_foods: Lista de alimentos parseados
            
        Returns:
            Lista de ingredientes válidos para log_meal
        """
        meal_ingredients = []
        
        for food_item in parsed_foods:
            food_name = food_item["name"]
            quantity_grams = food_item["quantity"]
            
            # Buscar el alimento en la base de datos
            search_result = await self.nutrition_tools.search_foods(food_name, limit=1)
            
            if search_result["success"] and search_result["foods"]:
                food_data = search_result["foods"][0]
                
                meal_ingredients.append({
                    "food_id": food_data["id"],
                    "quantity_grams": quantity_grams,
                    "notes": f"{quantity_grams}g de {food_data['name_es']}"
                })
                
                logger.info(f"✅ Mapeado: {food_name} -> {food_data['name_es']} ({quantity_grams}g)")
            else:
                logger.warning(f"❌ No encontrado en BD: {food_name}")
        
        return meal_ingredients
    
    def _generate_meal_name(self, parsed_foods: List[Dict[str, Any]]) -> str:
        """Generar nombre descriptivo para la comida"""
        if not parsed_foods:
            return "Comida registrada"
        
        food_names = [food["name"] for food in parsed_foods[:3]]  # Max 3 nombres
        if len(parsed_foods) > 3:
            return f"{', '.join(food_names)} y más"
        else:
            return ', '.join(food_names)
    
    def _format_meal_logged_response(self, result: Dict[str, Any], meal_type: str) -> str:
        """Formatear respuesta para WhatsApp después de registrar comida"""
        consumed_meal = result["consumed_meal"]
        
        response = f"✅ ¡Perfecto! Registré tu comida en FaiTracker\n\n"
        response += f"🍽️ {consumed_meal['meal_name']}\n"
        response += f"⏰ {meal_type.title()} - {consumed_meal['consumed_at']}\n\n"
        response += f"📊 Análisis nutricional:\n"
        response += f"🔥 {consumed_meal['total_calories']:.0f} calorías\n"
        response += f"🥩 {consumed_meal['total_protein_g']:.1f}g proteína\n"
        response += f"🍞 {consumed_meal['total_carbs_g']:.1f}g carbohidratos\n"
        response += f"🥑 {consumed_meal['total_fat_g']:.1f}g grasas\n"
        
        if consumed_meal.get("satisfaction_rating"):
            response += f"⭐ Satisfacción: {consumed_meal['satisfaction_rating']}/5\n"
        
        response += f"\n🌟 Luna dice: ¡Excelente registro! Escribe '¿cómo voy con mi dieta?' para ver tu progreso completo"
        
        return response
    
    async def _process_general_query(self, message: str, user: User, context: Dict[str, Any]) -> str:
        """Procesar consulta general sin herramientas específicas"""
        # Delegar al agente base para respuesta conversacional
        return await self.process(message, context)
    
    async def _handle_diet_creation_request(self, message: str, user_id: str) -> str:
        """
        Manejar solicitudes de creación de dietas de forma inteligente
        
        Args:
            message: Mensaje del usuario
            user_id: ID del usuario
            
        Returns:
            Respuesta con el plan creado o solicitud de información
        """
        message_lower = message.lower()
        
        # Por simplicidad, crear un plan básico por defecto
        # En una implementación más avanzada, esto podría extraer parámetros del mensaje
        # o hacer preguntas al usuario para personalizar
        
        # Detectar tipo de objetivo básico del mensaje
        plan_type = "perdida_peso"  # Default
        target_calories = 2000  # Default
        plan_name = "Mi Plan Personalizado"
        
        if any(word in message_lower for word in ["subir peso", "ganar peso", "masa muscular", "volumen"]):
            plan_type = "ganancia_peso"
            target_calories = 2500
            plan_name = "Plan de Ganancia de Peso"
        elif any(word in message_lower for word in ["bajar peso", "perder peso", "adelgazar", "deficit"]):
            plan_type = "perdida_peso"
            target_calories = 1800
            plan_name = "Plan de Pérdida de Peso"
        elif any(word in message_lower for word in ["mantener", "mantenimiento", "equilibrio"]):
            plan_type = "mantenimiento"
            target_calories = 2000
            plan_name = "Plan de Mantenimiento"
        
        # Calcular macros básicos (aproximación estándar)
        protein_percent = 0.25  # 25% proteína
        carbs_percent = 0.45    # 45% carbohidratos
        fat_percent = 0.30      # 30% grasas
        
        target_protein_g = (target_calories * protein_percent) / 4  # 4 kcal/g
        target_carbs_g = (target_calories * carbs_percent) / 4      # 4 kcal/g
        target_fat_g = (target_calories * fat_percent) / 9          # 9 kcal/g
        
        try:
            # Crear el plan usando las herramientas
            result = await self.nutrition_tools.create_diet_plan(
                user_id=user_id,
                plan_name=plan_name,
                plan_type=plan_type,
                target_calories=target_calories,
                target_protein_g=target_protein_g,
                target_carbs_g=target_carbs_g,
                target_fat_g=target_fat_g,
                description=f"Plan personalizado basado en tu solicitud"
            )
            
            if result["success"]:
                return self._format_diet_creation_response(result)
            else:
                return f"❌ {result.get('message', 'No se pudo crear el plan de dieta')}"
                
        except Exception as e:
            logger.error(f"Error creando dieta: {str(e)}")
            return "Lo siento, hubo un error al crear tu plan de dieta. ¿Podrías intentar de nuevo?"
    
    def _format_diet_creation_response(self, result: Dict[str, Any]) -> str:
        """Formatear respuesta de creación de dieta"""
        diet_plan = result["diet_plan"]
        
        response = f"🎉 **¡Plan de dieta creado exitosamente!**\n\n"
        response += f"📋 **{diet_plan['name']}**\n"
        response += f"🎯 **Objetivo:** {diet_plan['plan_type'].replace('_', ' ').title()}\n"
        response += f"📅 **Fecha inicio:** {diet_plan['start_date']}\n\n"
        
        response += f"📊 **Objetivos nutricionales diarios:**\n"
        response += f"🔥 {diet_plan['target_calories']} kcal totales\n"
        response += f"🥩 {diet_plan['target_protein_g']:.0f}g proteína ({(diet_plan['target_protein_g']*4/diet_plan['target_calories']*100):.0f}%)\n"
        response += f"🍞 {diet_plan['target_carbs_g']:.0f}g carbohidratos ({(diet_plan['target_carbs_g']*4/diet_plan['target_calories']*100):.0f}%)\n"
        response += f"🥑 {diet_plan['target_fat_g']:.0f}g grasas ({(diet_plan['target_fat_g']*9/diet_plan['target_calories']*100):.0f}%)\n\n"
        
        response += f"✅ **Tu plan está ahora activo y reemplaza cualquier plan anterior.**\n\n"
        response += f"💡 **Próximos pasos:**\n"
        response += f"• Pregunta '¿Qué comidas tengo hoy?' para ver tu plan diario\n"
        response += f"• Registra tus comidas con 'acabo de comer...'\n"
        response += f"• Pregunta '¿Cómo voy con mi dieta?' para seguimiento\n\n"
        response += f"🌟 **¡Luna te ayudará a alcanzar tus objetivos!** 🌙✨"
        
        return response

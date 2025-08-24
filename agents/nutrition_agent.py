"""
Agente especializado en nutrición y alimentación saludable
"""
import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class NutritionAgent(BaseAgent):
    """
    Agente experto en nutrición, dietas y alimentación saludable
    """
    
    def __init__(self, user_id: Optional[str] = None):
        system_prompt = """
        Eres un nutricionista certificado experto en alimentación saludable y nutrición deportiva.
        Tu objetivo es proporcionar:
        
        1. Planes de alimentación personalizados según objetivos
        2. Información nutricional precisa sobre alimentos
        3. Recetas saludables y balanceadas
        4. Consejos de suplementación (siempre sugiriendo consultar con un médico)
        5. Estrategias para mejorar hábitos alimenticios
        
        Características de tus respuestas:
        - Basa tus recomendaciones en evidencia científica
        - Considera restricciones dietéticas y alergias
        - Proporciona información sobre macronutrientes y micronutrientes
        - Incluye opciones prácticas y accesibles
        - Usa emojis relevantes para hacer el contenido más visual (🥗🍎🥑)
        - Evita dietas extremas o restrictivas sin supervisión médica
        
        IMPORTANTE: Siempre recuerda que no reemplazas la consulta con un profesional 
        de la salud para condiciones médicas específicas.
        
        Responde siempre en español y de forma clara y estructurada.
        """
        
        super().__init__(name="NutritionAgent", system_prompt=system_prompt, user_id=user_id)
        
        # Base de conocimiento nutricional
        self.nutrition_database = {
            "objetivos": {
                "perdida_peso": {
                    "deficit_calorico": "300-500 kcal/día",
                    "proteina": "1.6-2.2 g/kg peso corporal",
                    "tips": ["Aumentar fibra", "Hidratación adecuada", "Comidas frecuentes"]
                },
                "ganancia_muscular": {
                    "superavit_calorico": "200-400 kcal/día",
                    "proteina": "1.8-2.5 g/kg peso corporal",
                    "tips": ["Proteína post-entreno", "Carbohidratos complejos", "Grasas saludables"]
                },
                "mantenimiento": {
                    "calorias": "TDEE",
                    "proteina": "1.2-1.6 g/kg peso corporal",
                    "tips": ["Balance de macros", "Variedad alimentaria", "80/20 rule"]
                }
            }
        }
    
    async def create_meal_plan(self, user_info: Dict[str, Any], days: int = 7) -> str:
        """
        Crear un plan de alimentación personalizado
        
        Args:
            user_info: Información del usuario (peso, altura, objetivo, restricciones)
            days: Número de días del plan
            
        Returns:
            Plan de alimentación detallado
        """
        prompt = f"""
        Crea un plan de alimentación detallado con la siguiente información:
        Información del usuario: {user_info}
        Días: {days}
        
        Incluye para cada día:
        1. Desayuno con calorías y macros
        2. Snack de media mañana
        3. Almuerzo con calorías y macros
        4. Snack de tarde
        5. Cena con calorías y macros
        6. Total de calorías y distribución de macros del día
        
        Considera:
        - Variedad en las comidas
        - Alimentos accesibles
        - Preparación práctica
        - Balance nutricional
        """
        
        return await self.process(prompt, user_info)
    
    async def analyze_meal(self, meal_description: str, user_goal: Optional[str] = None) -> str:
        """
        Analizar una comida y proporcionar información nutricional
        
        Args:
            meal_description: Descripción de la comida
            user_goal: Objetivo del usuario (opcional)
            
        Returns:
            Análisis nutricional de la comida
        """
        context = {"objetivo": user_goal} if user_goal else {}
        
        prompt = f"""
        Analiza la siguiente comida: {meal_description}
        
        Proporciona:
        1. Estimación de calorías totales
        2. Distribución de macronutrientes (proteínas, carbohidratos, grasas)
        3. Micronutrientes destacados
        4. Puntos positivos de la comida
        5. Sugerencias de mejora si las hay
        6. Calificación general (1-10) basada en valor nutricional
        """
        
        return await self.process(prompt, context)
    
    async def calculate_calories(self, user_stats: Dict[str, Any]) -> str:
        """
        Calcular necesidades calóricas del usuario
        
        Args:
            user_stats: Estadísticas del usuario (peso, altura, edad, sexo, actividad)
            
        Returns:
            Cálculo de calorías y recomendaciones
        """
        prompt = f"""
        Con las siguientes estadísticas del usuario:
        {user_stats}
        
        Calcula y proporciona:
        1. TMB (Tasa Metabólica Basal)
        2. TDEE (Gasto Energético Diario Total)
        3. Calorías recomendadas según objetivo
        4. Distribución ideal de macronutrientes
        5. Timing de comidas recomendado
        6. Ajustes según nivel de actividad
        """
        
        return await self.process(prompt, user_stats)
    
    async def suggest_recipes(self, preferences: Dict[str, Any], meal_type: str) -> str:
        """
        Sugerir recetas saludables según preferencias
        
        Args:
            preferences: Preferencias dietéticas del usuario
            meal_type: Tipo de comida (desayuno, almuerzo, cena, snack)
            
        Returns:
            Recetas sugeridas con instrucciones
        """
        prompt = f"""
        Sugiere 3 recetas saludables para {meal_type} considerando:
        Preferencias: {preferences}
        
        Para cada receta incluye:
        1. Nombre de la receta
        2. Ingredientes con cantidades
        3. Instrucciones paso a paso
        4. Información nutricional (calorías, proteínas, carbohidratos, grasas)
        5. Tiempo de preparación
        6. Tips de preparación o variaciones
        """
        
        return await self.process(prompt, preferences)
    
    async def hydration_plan(self, user_info: Dict[str, Any]) -> str:
        """
        Crear un plan de hidratación personalizado
        
        Args:
            user_info: Información del usuario
            
        Returns:
            Plan de hidratación detallado
        """
        prompt = f"""
        Crea un plan de hidratación personalizado considerando:
        {user_info}
        
        Incluye:
        1. Cantidad diaria de agua recomendada
        2. Distribución a lo largo del día
        3. Ajustes según actividad física
        4. Señales de deshidratación a vigilar
        5. Bebidas recomendadas además del agua
        6. Tips para mantener buena hidratación
        """
        
        return await self.process(prompt, user_info)
    
    async def supplement_advice(self, goal: str, current_diet: Optional[str] = None) -> str:
        """
        Proporcionar consejos sobre suplementación
        
        Args:
            goal: Objetivo del usuario
            current_diet: Descripción de la dieta actual
            
        Returns:
            Consejos sobre suplementación
        """
        context = {"dieta_actual": current_diet} if current_diet else {}
        
        prompt = f"""
        Proporciona consejos sobre suplementación para el objetivo: {goal}
        
        Incluye:
        1. Suplementos potencialmente beneficiosos
        2. Dosis recomendadas y timing
        3. Posibles interacciones o contraindicaciones
        4. Prioridad de cada suplemento (esencial, útil, opcional)
        5. Alternativas naturales en alimentos
        
        IMPORTANTE: Recomienda siempre consultar con un profesional de la salud
        antes de comenzar cualquier suplementación.
        """
        
        return await self.process(prompt, context)

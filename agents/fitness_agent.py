"""
Agente especializado en fitness y ejercicio
"""
import logging
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FitnessAgent(BaseAgent):
    """
    Agente experto en rutinas de ejercicio, técnicas de entrenamiento y fitness
    """
    
    def __init__(self):
        system_prompt = """
        Eres un entrenador personal experto en fitness y ejercicio físico. 
        Tu objetivo es proporcionar:
        
        1. Rutinas de ejercicio personalizadas según el nivel del usuario
        2. Técnicas correctas de ejecución de ejercicios
        3. Planes de entrenamiento progresivos
        4. Consejos de recuperación y prevención de lesiones
        5. Motivación y seguimiento del progreso
        
        Características de tus respuestas:
        - Siempre prioriza la seguridad y la técnica correcta
        - Adapta las recomendaciones al nivel de fitness del usuario
        - Incluye calentamiento y enfriamiento en las rutinas
        - Usa emojis relevantes para hacer el contenido más visual (💪🏋️🔥)
        - Proporciona alternativas para ejercicios que requieran equipo especial
        - Sé motivador pero realista con las expectativas
        
        Si el usuario menciona dolor, lesiones o condiciones médicas, recomienda 
        consultar con un profesional de la salud antes de continuar.
        
        Responde siempre en español y de forma clara y estructurada.
        """
        
        super().__init__(name="FitnessAgent", system_prompt=system_prompt)
        
        # Base de conocimiento de ejercicios
        self.exercise_database = {
            "principiante": {
                "fuerza": ["flexiones de rodillas", "sentadillas con silla", "plancha modificada"],
                "cardio": ["caminata rápida", "marcha en el lugar", "jumping jacks modificados"],
                "flexibilidad": ["estiramientos básicos", "yoga suave", "rotaciones articulares"]
            },
            "intermedio": {
                "fuerza": ["flexiones estándar", "sentadillas", "plancha", "lunges"],
                "cardio": ["trote ligero", "burpees", "mountain climbers"],
                "flexibilidad": ["yoga intermedio", "estiramientos dinámicos", "foam rolling"]
            },
            "avanzado": {
                "fuerza": ["flexiones diamante", "pistol squats", "muscle ups", "dominadas"],
                "cardio": ["HIIT", "sprints", "box jumps", "burpees con salto"],
                "flexibilidad": ["yoga avanzado", "estiramientos PNF", "movilidad articular compleja"]
            }
        }
    
    async def create_workout_routine(self, user_level: str, focus: str, duration: int = 30) -> str:
        """
        Crear una rutina de ejercicio personalizada
        
        Args:
            user_level: Nivel del usuario (principiante, intermedio, avanzado)
            focus: Enfoque del entrenamiento (fuerza, cardio, flexibilidad, completo)
            duration: Duración en minutos
            
        Returns:
            Rutina de ejercicio formateada
        """
        prompt = f"""
        Crea una rutina de ejercicio detallada con las siguientes características:
        - Nivel: {user_level}
        - Enfoque: {focus}
        - Duración: {duration} minutos
        
        Incluye:
        1. Calentamiento (5 minutos)
        2. Ejercicios principales con series, repeticiones y tiempo de descanso
        3. Enfriamiento (5 minutos)
        4. Consejos de técnica para cada ejercicio
        5. Modificaciones si es necesario
        """
        
        return await self.process(prompt)
    
    async def analyze_form(self, exercise: str, description: str) -> str:
        """
        Analizar y corregir la técnica de un ejercicio
        
        Args:
            exercise: Nombre del ejercicio
            description: Descripción de cómo lo está haciendo el usuario
            
        Returns:
            Análisis y correcciones de la técnica
        """
        prompt = f"""
        El usuario está realizando: {exercise}
        Descripción de su ejecución: {description}
        
        Proporciona:
        1. Análisis de posibles errores en la técnica
        2. Correcciones específicas paso a paso
        3. Consejos para evitar lesiones
        4. Ejercicios preparatorios si necesita mejorar movilidad/fuerza
        """
        
        return await self.process(prompt)
    
    async def track_progress(self, workout_history: Dict[str, Any]) -> str:
        """
        Analizar el progreso del usuario y proporcionar recomendaciones
        
        Args:
            workout_history: Historial de entrenamientos del usuario
            
        Returns:
            Análisis del progreso y recomendaciones
        """
        prompt = f"""
        Analiza el siguiente historial de entrenamientos:
        {workout_history}
        
        Proporciona:
        1. Resumen del progreso
        2. Logros destacados
        3. Áreas de mejora
        4. Recomendaciones para las próximas semanas
        5. Ajustes sugeridos en la rutina
        """
        
        return await self.process(prompt)
    
    async def injury_prevention(self, activity: str, user_info: Optional[Dict] = None) -> str:
        """
        Proporcionar consejos de prevención de lesiones
        
        Args:
            activity: Tipo de actividad o ejercicio
            user_info: Información adicional del usuario
            
        Returns:
            Consejos de prevención de lesiones
        """
        context = {"actividad": activity}
        if user_info:
            context.update(user_info)
            
        prompt = f"""
        Proporciona consejos específicos de prevención de lesiones para: {activity}
        
        Incluye:
        1. Calentamiento específico recomendado
        2. Errores comunes que causan lesiones
        3. Señales de advertencia a las que prestar atención
        4. Ejercicios de fortalecimiento preventivo
        5. Protocolo de recuperación post-ejercicio
        """
        
        return await self.process(prompt, context)

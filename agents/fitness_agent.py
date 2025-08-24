"""
Agente especializado en fitness y ejercicio
"""
import logging
from typing import Dict, Any, Optional, List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from .base_agent import BaseAgent
from .fitness_tools import get_fitness_tools

logger = logging.getLogger(__name__)


class FitnessAgent(BaseAgent):
    """
    Agente experto en rutinas de ejercicio, técnicas de entrenamiento y fitness
    """
    
    def __init__(self):
        system_prompt = """
        Eres un entrenador personal experto en fitness y ejercicio físico con acceso a herramientas 
        para registrar y hacer seguimiento de rutinas de ejercicio.
        
        Tu objetivo es proporcionar:
        
        1. Rutinas de ejercicio personalizadas según el nivel del usuario
        2. Técnicas correctas de ejecución de ejercicios
        3. Planes de entrenamiento progresivos
        4. Consejos de recuperación y prevención de lesiones
        5. Motivación y seguimiento del progreso
        6. **REGISTRO Y SEGUIMIENTO DE RUTINAS EN TIEMPO REAL**
        
        HERRAMIENTAS DISPONIBLES:
        - start_workout: Para iniciar una nueva rutina de ejercicio
        - end_workout: Para finalizar una rutina activa
        - add_set: Para registrar cada serie completada
        - get_active_workout: Para verificar si hay una rutina en progreso
        - get_exercises: Para consultar ejercicios disponibles
        
        FLUJO DE TRABAJO RECOMENDADO:
        1. Cuando el usuario quiera entrenar, usa get_active_workout para verificar rutinas activas
        2. Si no hay rutina activa, usa start_workout para iniciar una nueva
        3. Durante el entrenamiento, usa add_set para registrar cada serie completada
        4. Al finalizar, usa end_workout para cerrar la rutina y mostrar resumen
        
        Características de tus respuestas:
        - Siempre prioriza la seguridad y la técnica correcta
        - Adapta las recomendaciones al nivel de fitness del usuario
        - Incluye calentamiento y enfriamiento en las rutinas
        - Usa emojis relevantes para hacer el contenido más visual (💪🏋️🔥)
        - Proporciona alternativas para ejercicios que requieran equipo especial
        - Sé motivador pero realista con las expectativas
        - **USA LAS HERRAMIENTAS para registrar el progreso del usuario automáticamente**
        
        IMPORTANTE: 
        - Siempre usa las herramientas disponibles para registrar rutinas y series
        - El phone_number es el número de WhatsApp del usuario (ej: +51998555878)
        - Registra cada serie inmediatamente después de que el usuario la complete
        - Proporciona feedback motivador después de cada serie registrada
        
        Si el usuario menciona dolor, lesiones o condiciones médicas, recomienda 
        consultar con un profesional de la salud antes de continuar.
        
        Responde siempre en español y de forma clara y estructurada.
        """
        
        super().__init__(name="FitnessAgent", system_prompt=system_prompt)
        
        # Inicializar herramientas y agente executor
        self.tools = get_fitness_tools()
        self.agent_executor = None
        self._setup_agent_executor()
        
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
    
    def _setup_agent_executor(self):
        """
        Configurar el agent executor con las herramientas
        """
        try:
            if self.llm is None:
                logger.warning("⚠️ LLM no disponible, agent executor no se configurará")
                self.agent_executor = None
                return
            
            # Crear prompt template para el agente con herramientas
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Crear agente con herramientas
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            
            # Crear executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            logger.info(f"✅ Agent executor configurado para {self.name} con {len(self.tools)} herramientas")
            
        except Exception as e:
            logger.error(f"❌ Error configurando agent executor: {str(e)}")
            self.agent_executor = None
    
    async def process_with_tools(self, input_text: str, phone_number: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Procesar entrada usando herramientas (método principal para fitness)
        
        Args:
            input_text: Texto de entrada del usuario
            phone_number: Número de teléfono del usuario (WhatsApp)
            context: Contexto adicional opcional
            
        Returns:
            Respuesta generada por el agente con herramientas
        """
        try:
            if not self.agent_executor:
                logger.warning("⚠️ Agent executor no disponible, usando método base")
                return await super().process(input_text, context)
            
            # Preparar input con contexto de usuario
            full_input = f"Número de teléfono: {phone_number}\n\n{input_text}"
            
            if context:
                context_str = self._format_context(context)
                full_input += f"\n\nContexto adicional: {context_str}"
            
            # Ejecutar agente con herramientas
            result = await self.agent_executor.ainvoke({
                "input": full_input
            })
            
            response = result.get("output", "Lo siento, no pude procesar tu solicitud.")
            
            # Guardar en memoria
            self.memory.save_context(
                {"input": input_text},
                {"output": response}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en process_with_tools: {str(e)}")
            # Fallback al método base si hay error
            return await super().process(input_text, context)
    
    async def process(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Método process sobrescrito para usar herramientas por defecto
        Para mantener compatibilidad, pero se recomienda usar process_with_tools
        """
        # Intentar extraer phone_number del contexto
        phone_number = "+51998555878"  # Usuario demo por defecto
        if context and "phone_number" in context:
            phone_number = context["phone_number"]
        elif context and "from_number" in context:
            phone_number = context["from_number"]
        elif context and "user_id" in context:
            phone_number = context["user_id"]  # Compatibilidad hacia atrás
        
        return await self.process_with_tools(input_text, phone_number, context)

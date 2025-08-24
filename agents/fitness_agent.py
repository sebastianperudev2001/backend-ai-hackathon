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
    
    def __init__(self, user_id: Optional[str] = None):
        system_prompt = """
        ¡Hola! Soy Sebastián, tu entrenador personal en FaiTracker 💪
        
        Soy un entrenador experto en fitness y ejercicio físico con acceso a herramientas avanzadas 
        para registrar y hacer seguimiento de tus rutinas de ejercicio en tiempo real.
        
        🏋️ Mi misión es ayudarte a alcanzar tus objetivos fitness proporcionando:
        
        1. 🎯 Rutinas de ejercicio personalizadas según tu nivel y objetivos
        2. ✅ Técnicas correctas de ejecución para maximizar resultados
        3. 📈 Planes de entrenamiento progresivos que evolucionan contigo
        4. 🛡️ Consejos de recuperación y prevención de lesiones
        5. 💪 Motivación constante y seguimiento detallado de tu progreso
        6. 📱 **REGISTRO EN TIEMPO REAL** de tus entrenamientos en FaiTracker
        
        🔧 HERRAMIENTAS FAITRACKER (úsalas cuando sea necesario para acciones específicas):
        - get_active_workout: Verificar si tienes una rutina activa en FaiTracker
        - start_workout: Iniciar nueva sesión de entrenamiento
        - add_set_simple: Registrar series completadas en tiempo real
        - end_active_workout: Finalizar y guardar tu sesión de entrenamiento
        - get_exercises: Consultar nuestra base de 98+ ejercicios profesionales
        - get_progressive_overload: Analizar tu progreso y recomendaciones de sobrecarga
        
        🚫 PROHIBIDO SIMULAR HERRAMIENTAS:
        1. NUNCA escribas JSON fake como {{"action": "get_active_workout"}}
        2. NUNCA simules respuestas de herramientas
        3. Si decides usar herramientas, LangChain las ejecutará automáticamente
        4. Si no usas herramientas, responde directamente como entrenador personal
        5. TODAS las herramientas principales requieren phone_number como parámetro
        
        EJERCICIOS DISPONIBLES EN LA BASE DE DATOS (98+ ejercicios):
        
        **PECHO**: Press de Banca, Press Inclinado, Aperturas con Mancuernas, Cruces en Polea, Flexiones, Peck Deck
        **ESPALDA**: Peso Muerto, Dominadas, Remo con Barra, Remo con Mancuerna, Jalones al Pecho, Face Pulls
        **HOMBROS**: Press Militar, Elevaciones Laterales, Elevaciones Frontales, Pájaros, Press Arnold
        **BÍCEPS**: Curl con Barra, Curl con Mancuernas, Curl Martillo, Curl Concentrado
        **TRÍCEPS**: Press Francés, Fondos en Paralelas, Extensiones en Polea, Patadas de Tríceps  
        **PIERNAS**: Sentadillas, Prensa de Piernas, Lunges, Peso Muerto Rumano, Curl de Piernas
        **GLÚTEOS**: Hip Thrust, Puentes de Glúteo, Sentadillas Sumo
        **CORE**: Plancha, Abdominales, Russian Twists, Elevaciones de Piernas
        **CARDIO**: Correr, Burpees, Jumping Jacks, Mountain Climbers, Bicicleta Estática
        
        IMPORTANTE: Estos son SOLO ALGUNOS ejemplos. La base de datos contiene 98+ ejercicios.
        Si un usuario menciona un ejercicio que no reconoces de esta lista, USA LA HERRAMIENTA 
        get_exercises para consultar TODOS los ejercicios disponibles antes de decir que no existe.
        
        ⚠️ DECISIÓN SOBRE USO DE HERRAMIENTAS:
        
        Tienes herramientas disponibles, pero NO las uses automáticamente. Evalúa cada mensaje:
        
        USA HERRAMIENTAS cuando el usuario quiera hacer acciones específicas:
        ✅ INICIAR una rutina ("quiero empezar a entrenar", "vamos a iniciar")
        ✅ REGISTRAR una serie concreta ("hice 10 flexiones de 80kg", "registra mi serie")  
        ✅ FINALIZAR entrenamiento ("terminé mi rutina", "acabé de entrenar")
        ✅ CONSULTAR rutina activa específicamente ("¿tengo rutina activa?")
        ✅ VER lista de ejercicios específicamente ("¿qué ejercicios disponibles hay?")
        ✅ ANALIZAR PROGRESO y SOBRECARGA PROGRESIVA ("¿cómo progreso en sentadillas?", "cuánto peso debo subir en press de banca?", "¿debo aumentar peso o repeticiones?")
        
        NO USES HERRAMIENTAS cuando sea solo conversación/información:
        ❌ Solo menciona un ejercicio sin pedir registro ("hice remo", "terminé mis flexiones")
        ❌ Preguntas sobre técnica ("¿cómo hacer flexiones?")
        ❌ Consultas generales ("beneficios del cardio", "cuánto entrenar")
        ❌ Pide rutinas teóricas ("crea rutina para principiantes")
        ❌ Busca consejos ("qué comer antes de entrenar")
        
        REGLA DE ORO: Si el usuario solo comenta/informa sobre ejercicio → Responde con consejos/motivación
        Si pide explícitamente registrar/iniciar/finalizar → Usa herramientas
        
        EJEMPLO DE RESPUESTA SIN HERRAMIENTAS:
        Usuario: "Acabo de hacer 10 reps de 90kg de remo con barra"
        Respuesta correcta: "¡Excelente trabajo con el remo con barra! 💪 90kg por 10 repeticiones es impresionante. El remo es fundamental para desarrollar la espalda... [consejos sobre técnica, descanso, etc.]"
        Respuesta INCORRECTA: "Permíteme ayudarte a registrar... {{action: get_active_workout}}"
        
        FLUJO DE TRABAJO:
        1. ANALIZA la intención del usuario ANTES de usar herramientas
        2. Si es consulta general → Responde directamente SIN herramientas
        3. Si quiere entrenar → Usa get_active_workout primero, luego start_workout si es necesario
        4. Durante entrenamiento → Usa add_set_simple para registrar series
        5. Al finalizar → Usa end_active_workout
        6. Si menciona un ejercicio no reconocido → Usa get_exercises para verificar disponibilidad
        
        💬 Mi estilo como Sebastián, tu entrenador en FaiTracker:
        - 🛡️ Siempre priorizo tu seguridad y la técnica correcta
        - 🎯 Adapto mis recomendaciones a tu nivel y objetivos personales
        - 🔥 Incluyo calentamiento y enfriamiento en todas las rutinas
        - 💪 Uso emojis para hacer nuestras conversaciones más dinámicas
        - 🏠 Te doy alternativas si no tienes equipo especializado
        - 🚀 Soy motivador pero siempre realista con las expectativas
        - 📱 Uso las herramientas de FaiTracker solo para acciones específicas de entrenamiento
        
        🎯 PROTOCOLO FAITRACKER:
        - Recibo tu número de WhatsApp para personalizar el seguimiento
        - Para dudas generales, comparto mi conocimiento directamente
        - Las herramientas las uso solo para registrar entrenamientos reales
        - Te explico qué voy a hacer antes de usar cualquier herramienta
        - Si mencionas un ejercicio, verifico en nuestra base de 98+ ejercicios profesionales
        - Si no existe el ejercicio, te sugiero alternativas similares de FaiTracker
        - NUNCA descarto un ejercicio sin verificar primero en nuestra base de datos
        
        ⚠️ IMPORTANTE PARA TU SEGURIDAD:
        Si mencionas dolor, lesiones o condiciones médicas, te recomendaré 
        consultar con un profesional de la salud antes de continuar.
        
        ¡Siempre respondo en español de forma clara y motivadora! 💪
        
        ¿Listo para entrenar con FaiTracker?
        """
        
        super().__init__(name="FitnessAgent", system_prompt=system_prompt, user_id=user_id)
        
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
    
    def _detect_tool_intent(self, input_text: str) -> bool:
        """
        Detectar si el usuario tiene intención de usar herramientas específicas
        
        Args:
            input_text: Texto de entrada del usuario
            
        Returns:
            True si debe usar herramientas, False si es consulta general
        """
        input_lower = input_text.lower()
        
        # Palabras clave que indican uso de herramientas
        tool_keywords = [
            # Iniciar rutina
            "empezar a entrenar", "comenzar rutina", "iniciar workout", "empezar entrenamiento",
            "quiero entrenar", "vamos a entrenar", "inicio rutina", "comenzar a ejercitarme",
            
            # Terminar rutina
            "terminar rutina", "finalizar rutina", "finalizar entrenamiento", "acabé de entrenar", "terminé",
            "finalizar workout", "cerrar rutina",
            
            # Registrar series
            "hice", "completé", "registra", "anotar serie", "terminé serie", "acabé serie",
            "registrar ejercicio", "anotar ejercicio", "realicé", "acabé de hacer",
            "terminé de hacer", "hice una serie", "completé una serie", "hice ejercicio",
            "dominadas", "sentadillas", "flexiones", "plancha",
            
            # Consultar rutina activa
            "rutina activa", "qué rutina estoy haciendo", "tengo rutina", "rutina en progreso",
            "entrenamiento activo",
            
            # Ver ejercicios disponibles
            "qué ejercicios hay", "muestra ejercicios", "ejercicios disponibles", "lista de ejercicios",
            
            # Sobrecarga progresiva
            "sobrecarga progresiva", "cómo progresar", "aumentar peso", "subir peso", "incrementar peso",
            "aumentar repeticiones", "subir reps", "cómo mejorar", "progreso en ejercicio",
            "cuánto peso subir", "debo aumentar", "siguiente nivel", "progresión"
        ]
        
        # Palabras que indican consultas generales (NO usar herramientas)
        general_keywords = [
            "cómo hacer", "cómo se hace", "técnica de", "forma correcta", "consejos",
            "beneficios", "qué es", "para qué sirve", "cuánto", "cuándo", "dónde",
            "rutina para", "plan de", "programa de", "ejercicios para", "crea una rutina",
            "diseña una rutina", "recomienda ejercicios", "qué comer", "nutrición",
            "dieta", "alimentación", "suplementos", "descanso", "recuperación"
        ]
        
        # Verificar palabras de consulta general primero (tienen prioridad)
        for keyword in general_keywords:
            if keyword in input_lower:
                return False
        
        # Verificar palabras de herramientas
        for keyword in tool_keywords:
            if keyword in input_lower:
                return True
        
        # Si no encuentra palabras clave específicas, analizar contexto
        # Frases que sugieren acción inmediata (usar herramientas)
        action_phrases = ["voy a", "quiero", "necesito", "puedes", "ayúdame a"]
        action_verbs = ["empezar", "comenzar", "iniciar", "terminar", "finalizar", "registrar", "anotar"]
        
        for phrase in action_phrases:
            if phrase in input_lower:
                for verb in action_verbs:
                    if verb in input_lower:
                        return True
        
        # Por defecto, para consultas ambiguas, no usar herramientas
        return False
    
    def _extract_text_from_response(self, response) -> str:
        """
        Extraer texto limpio de respuestas complejas del agent executor
        
        Args:
            response: Respuesta compleja del agent executor
            
        Returns:
            String limpio con el texto de la respuesta
        """
        try:
            # Si es una lista, buscar elementos de texto
            if isinstance(response, list):
                text_parts = []
                for item in response:
                    if isinstance(item, dict):
                        # Buscar campo 'text'
                        if 'text' in item:
                            text_parts.append(item['text'])
                        # Buscar otros campos de texto posibles
                        elif 'content' in item:
                            text_parts.append(item['content'])
                        elif 'message' in item:
                            text_parts.append(item['message'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                
                if text_parts:
                    return ' '.join(text_parts)
                else:
                    # Si no hay texto, convertir toda la lista a string
                    return str(response)
            
            # Si es un diccionario, buscar campos de texto
            elif isinstance(response, dict):
                if 'text' in response:
                    return response['text']
                elif 'content' in response:
                    return response['content']
                elif 'message' in response:
                    return response['message']
                else:
                    return str(response)
            
            # Para cualquier otro tipo, convertir a string
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"❌ Error extrayendo texto de respuesta: {str(e)}")
            return str(response)
    
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
            # Siempre usar el agent executor si está disponible
            # Dejar que el LLM decida si usar herramientas o no
            if not self.agent_executor:
                logger.warning("⚠️ Agent executor no disponible, usando método base")
                return await super().process(input_text, context)
            
            # Usar agent executor - el LLM decidirá si usar herramientas
            logger.info("🤖 Procesando con agent executor - LLM decidirá si usar herramientas")
            
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
            
            # Asegurar que la respuesta es un string limpio
            if not isinstance(response, str):
                logger.warning(f"⚠️ Agent executor devolvió tipo {type(response)}: {repr(response)}")
                response = self._extract_text_from_response(response)
            
            # Limpiar la respuesta
            response = response.strip()
            
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

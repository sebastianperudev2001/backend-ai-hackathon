"""
Agente Coordinador - Orquesta el sistema multi-agente con LangGraph
"""
import logging
from typing import Dict, Any, Optional, List, TypedDict, Annotated, Literal
from enum import Enum
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from .fitness_agent import FitnessAgent
from .nutrition_agent_simple import NutritionAgent
from config.settings import get_settings
from domain.models import User

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Estado del grafo de agentes - simplificado para arquitectura supervisor"""
    messages: Annotated[list, add_messages]
    next_agent: Optional[str]
    context: Optional[Dict[str, Any]]


class CoordinatorAgent:
    """
    Agente coordinador que orquesta el sistema multi-agente usando LangGraph
    siguiendo la arquitectura de supervisor
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        # Inicializar modelo de Claude para el supervisor
        try:
            self.supervisor_llm = ChatAnthropic(
                api_key=self.settings.ANTHROPIC_API_KEY,
                model=self.settings.CLAUDE_MODEL,
                temperature=0,
                max_tokens=1024
            )
            logger.info(f"✅ Modelo Claude supervisor inicializado: {self.settings.CLAUDE_MODEL}")
        except Exception as e:
            logger.error(f"❌ Error inicializando modelo Claude: {str(e)}")
            logger.warning("⚠️ Continuando sin Claude - usando detección simple de agentes")
            self.supervisor_llm = None
        
        # Los agentes se inicializarán dinámicamente con el user_id
        self.agents = {}
        self.fitness_agent = None
        self.nutrition_agent = None
        
        logger.info("✅ Coordinador inicializado - agentes se crearán dinámicamente")
        
        # Construir el grafo de flujo
        try:
            self.graph = self._build_graph()
            logger.info("✅ Grafo de flujo construido correctamente")
        except Exception as e:
            logger.error(f"❌ Error construyendo grafo: {str(e)}")
            raise RuntimeError(f"No se pudo construir el grafo: {str(e)}")
        
        logger.info("✅ Coordinador multi-agente inicializado con LangGraph")
    
    def _get_user_id_from_phone(self, phone_number: str) -> Optional[str]:
        """
        Obtener user_id desde el número de teléfono
        
        Args:
            phone_number: Número de teléfono del usuario
            
        Returns:
            User ID si se encuentra, None si no
        """
        try:
            from repository.supabase_client import get_supabase_direct_client
            client = get_supabase_direct_client()
            
            if not client:
                logger.warning("⚠️ Cliente de Supabase no inicializado")
                return None
            
            result = client.table("users").select("id").eq("phone_number", phone_number).single().execute()
            
            if result.data:
                logger.info(f"✅ Usuario encontrado para teléfono: {phone_number}")
                return result.data["id"]
            else:
                logger.warning(f"⚠️ Usuario no encontrado para teléfono: {phone_number}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo user_id: {str(e)}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _get_or_create_fitness_agent(self, user_id: Optional[str] = None) -> 'FitnessAgent':
        """
        Obtener o crear agente de fitness con memoria persistente
        
        Args:
            user_id: ID del usuario para memoria persistente
            
        Returns:
            Instancia del agente de fitness
        """
        try:
            if not self.fitness_agent or (user_id and getattr(self.fitness_agent, 'user_id', None) != user_id):
                self.fitness_agent = FitnessAgent(user_id=user_id)
                logger.info(f"✅ Agente de Fitness creado con user_id: {user_id}")
            return self.fitness_agent
        except Exception as e:
            logger.error(f"❌ Error creando agente de fitness: {str(e)}")
            # Fallback sin memoria persistente
            if not self.fitness_agent:
                self.fitness_agent = FitnessAgent()
            return self.fitness_agent
    
    def _get_or_create_nutrition_agent(self, user_id: Optional[str] = None) -> 'NutritionAgent':
        """
        Obtener o crear agente de nutrición con memoria persistente
        
        Args:
            user_id: ID del usuario para memoria persistente
            
        Returns:
            Instancia del agente de nutrición
        """
        try:
            if not self.nutrition_agent or (user_id and getattr(self.nutrition_agent, 'user_id', None) != user_id):
                self.nutrition_agent = NutritionAgent(user_id=user_id)
                logger.info(f"✅ Agente de Nutrición creado con user_id: {user_id}")
            return self.nutrition_agent
        except Exception as e:
            logger.error(f"❌ Error creando agente de nutrición: {str(e)}")
            # Fallback sin memoria persistente
            if not self.nutrition_agent:
                self.nutrition_agent = NutritionAgent()
            return self.nutrition_agent
    
    def _extract_text_from_response(self, response) -> str:
        """
        Extraer texto limpio de respuestas complejas de los agentes
        
        Args:
            response: Respuesta compleja de un agente
            
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
    
    def _build_graph(self) -> StateGraph:
        """
        Construir el grafo de flujo de trabajo con LangGraph siguiendo la arquitectura de supervisor
        
        Returns:
            Grafo compilado listo para ejecución
        """
        # Crear el grafo de estado
        workflow = StateGraph(GraphState)
        
        # Agregar nodos - cada agente es un nodo
        workflow.add_node("supervisor", self._supervisor)
        workflow.add_node("fitness_agent", self._fitness_agent_node)
        workflow.add_node("nutrition_agent", self._nutrition_agent_node)
        workflow.add_node("welcome", self._welcome_node)
        
        # Definir el flujo - supervisor como punto de entrada
        workflow.add_edge(START, "supervisor")
        
        # Agregar edges condicionales desde el supervisor
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next_agent"],
            {
                "fitness_agent": "fitness_agent",
                "nutrition_agent": "nutrition_agent",
                "welcome": "welcome",
                "FINISH": END
            }
        )
        
        # Los agentes retornan al supervisor
        workflow.add_edge("fitness_agent", END)
        workflow.add_edge("nutrition_agent", END)
        workflow.add_edge("welcome", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def _supervisor(self, state: GraphState) -> GraphState:
        """
        Nodo supervisor que decide qué agente debe manejar la consulta
        
        Args:
            state: Estado actual del grafo
            
        Returns:
            Estado actualizado con el siguiente agente a ejecutar
        """
        messages = state["messages"]
        
        # Si no hay mensajes o ya se han procesado suficientes iteraciones, terminar
        if not messages or len(messages) > 10:  # Límite de seguridad
            state["next_agent"] = "FINISH"
            return state
            
        # Obtener el último mensaje del usuario
        last_message = messages[-1]
        
        # Prompt para el supervisor
        supervisor_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un supervisor que enruta consultas a agentes especializados.
            Tienes disponibles estos agentes:
            - welcome: Para saludos, primeras interacciones y mensajes de bienvenida  
            - fitness_agent: Experto en ejercicio, rutinas, técnicas de entrenamiento y fitness
            - nutrition_agent: Experto en nutrición, dietas, calorías y alimentación saludable

            Analiza la consulta del usuario y decide:
            1. Si es un saludo o mensaje de bienvenida (hola, buenos días, ayuda, qué puedes hacer, etc.) → welcome
            2. Si es sobre ejercicio, fitness o entrenamiento → fitness_agent
            3. Si es sobre nutrición, dietas o comidas → nutrition_agent  
            4. Si ya se ha respondido completamente → FINISH

            Responde SOLO con uno de estos valores: welcome, fitness_agent, nutrition_agent, o FINISH
            """),
            ("human", "{input}")
        ])
        
        # Invocar al supervisor para decidir el siguiente agente
        try:
            # Si Claude está disponible, usarlo
            if self.supervisor_llm:
                chain = supervisor_prompt | self.supervisor_llm 
                result = chain.invoke({"input": last_message.content})
                next_agent = result.content.strip()
            else:
                # Fallback: usar detección simple sin Claude
                next_agent = self._simple_agent_detection(last_message.content)
            
            # Validar la respuesta
            valid_agents = ["fitness_agent", "nutrition_agent", "welcome", "FINISH"]
            if next_agent not in valid_agents:
                # Si hay palabras clave, intentar inferir
                next_agent = self._simple_agent_detection(last_message.content)
            
            logger.info(f"🎯 Supervisor decidió: {next_agent}")
            
            state["next_agent"] = next_agent
            return state
        
        except Exception as e:
            logger.error(f"❌ Error en supervisor: {str(e)}")
            # Fallback: usar detección simple
            next_agent = self._simple_agent_detection(last_message.content)
            state["next_agent"] = next_agent
            return state
    
    def _simple_agent_detection(self, message_content: str) -> str:
        """
        Detección simple de agente sin Claude API
        
        Args:
            message_content: Contenido del mensaje del usuario
            
        Returns:
            Nombre del agente a usar o "welcome" para mensajes de bienvenida
        """
        content_lower = message_content.lower()
        
        # Detectar mensajes de bienvenida/primera interacción
        welcome_keywords = [
            'hola', 'buenas', 'buenos días', 'buenas tardes', 'buenas noches',
            'inicio', 'empezar', 'comenzar', 'ayuda', 'start', 'help', 'hello',
            'qué puedes hacer', 'que puedes hacer', 'quién eres', 'quien eres',
            'presentate', 'preséntate', 'información', 'info', 'opciones',
            'cómo funciona', 'como funciona', 'qué es faitracker', 'que es faitracker'
        ]
        
        # Verificar si es mensaje de saludo/bienvenida
        if any(keyword in content_lower for keyword in welcome_keywords) and len(message_content) < 50:
            return "welcome"
        
        # Palabras clave para nutrición
        nutrition_keywords = [
            'comida', 'comidas', 'desayuno', 'almuerzo', 'cena', 'dieta', 'nutrición',
            'calorias', 'calorías', 'macros', 'proteinas', 'proteínas', 'alimentación',
            'siguiente comida', 'que como', 'qué como', 'plan de hoy', 'deficit',
            'alimento', 'alimentos', 'buscar', 'ingrediente', 'registrar',
            'plan de dieta', 'plan activo', 'dieta activa', 'mi plan', 'plan que tengo',
            'dieta que tengo', 'mi dieta', 'plan actual', 'dieta actual'
        ]
        
        # Palabras clave para fitness
        fitness_keywords = [
            'ejercicio', 'ejercicios', 'rutina', 'entrenar', 'entrenamiento', 'fitness',
            'gym', 'gimnasio', 'músculo', 'fuerza', 'cardio', 'flexiones', 'sentadillas',
            'peso', 'series', 'repeticiones', 'workout', 'plan de entrenamiento'
        ]
        
        # Contar coincidencias
        nutrition_matches = sum(1 for keyword in nutrition_keywords if keyword in content_lower)
        fitness_matches = sum(1 for keyword in fitness_keywords if keyword in content_lower)
        
        # Decidir basado en coincidencias
        if nutrition_matches > fitness_matches:
            return "nutrition_agent"
        elif fitness_matches > nutrition_matches:
            return "fitness_agent"
        else:
            # En caso de empate, usar longitud de coincidencias más específicas
            if any(phrase in content_lower for phrase in ["que como", "qué como", "comidas de hoy", "siguiente comida"]):
                return "nutrition_agent"
            elif any(phrase in content_lower for phrase in ["rutina", "entrenar", "ejercicio"]):
                return "fitness_agent"
            else:
                # Default: fitness (comportamiento original)
                return "fitness_agent"
        
    
    async def _fitness_agent_node(self, state: GraphState) -> GraphState:
        """
        Nodo del agente de fitness
        
        Args:
            state: Estado actual del grafo
            
        Returns:
            Estado actualizado con la respuesta del agente
        """
        try:
            messages = state["messages"]
            
            # Obtener el último mensaje del usuario
            if messages:
                last_message = messages[-1]
                user_query = last_message.content
                
                logger.info(f"🏋️ Procesando consulta con agente de fitness: '{user_query[:50]}...'")
                
                # Extraer phone_number del contexto si está disponible
                phone_number = "+51998555878"  # Default demo user
                context = state.get('context', None)
                if context and 'sender' in context:
                    phone_number = context['sender']
                
                # Asegurar que el número tiene el prefijo + 
                if not phone_number.startswith('+'):
                    phone_number = '+' + phone_number
                
                # Obtener user_id para memoria persistente
                user_id = self._get_user_id_from_phone(phone_number)
                
                # Obtener agente de fitness con memoria persistente
                fitness_agent = self._get_or_create_fitness_agent(user_id)
                
                # Llamar al agente de fitness con herramientas
                response = await fitness_agent.process_with_tools(
                    input_text=user_query,
                    phone_number=phone_number,
                    context=context
                )
                
                # Asegurar que la respuesta es un string limpio
                if not isinstance(response, str):
                    logger.warning(f"⚠️ Respuesta del fitness agent no es string: {type(response)}")
                    response = self._extract_text_from_response(response)
                
                # Limpiar la respuesta final
                response = response.strip()
                
                # Agregar la respuesta a los mensajes
                state["messages"].append(AIMessage(content=response))
                
                logger.info("✅ Respuesta del agente de fitness generada")
                
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en agente de fitness: {str(e)}")
            state["messages"].append(
                AIMessage(content="Lo siento, ocurrió un error al procesar tu consulta de fitness.")
            )
            return state
    
    async def _nutrition_agent_node(self, state: GraphState) -> GraphState:
        """
        Nodo del agente de nutrición
        
        Args:
            state: Estado actual del grafo
            
        Returns:
            Estado actualizado con la respuesta del agente
        """
        try:
            messages = state["messages"]
            
            # Obtener el último mensaje del usuario
            if messages:
                last_message = messages[-1]
                user_query = last_message.content
                
                logger.info(f"🥗 Procesando consulta con agente de nutrición: '{user_query[:50]}...'")
                
                # Extraer phone_number del contexto si está disponible
                phone_number = "+51998555878"  # Default demo user
                context = state.get('context', None)
                if context and 'sender' in context:
                    phone_number = context['sender']
                
                # Asegurar que el número tiene el prefijo + 
                if not phone_number.startswith('+'):
                    phone_number = '+' + phone_number
                
                # Obtener user_id para memoria persistente
                user_id = self._get_user_id_from_phone(phone_number)
                
                # Obtener agente de nutrición con memoria persistente
                nutrition_agent = self._get_or_create_nutrition_agent(user_id)
                
                # Crear un objeto User mock para la interfaz del nutrition agent
                user = User(
                    id=user_id,
                    phone_number=phone_number,
                    name="Demo User",  # Placeholder
                    created_at=None,
                    updated_at=None
                )
                
                # Llamar al agente de nutrición usando process_message
                response = await nutrition_agent.process_message(user_query, user, context)
                
                # Asegurar que la respuesta es un string limpio
                if not isinstance(response, str):
                    logger.warning(f"⚠️ Respuesta del nutrition agent no es string: {type(response)}")
                    response = self._extract_text_from_response(response)
                
                # Limpiar la respuesta final
                response = response.strip()
                
                # Agregar la respuesta a los mensajes
                state["messages"].append(AIMessage(content=response))
                
                logger.info("✅ Respuesta del agente de nutrición generada")
                
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en agente de nutrición: {str(e)}")
            state["messages"].append(
                AIMessage(content="Lo siento, ocurrió un error al procesar tu consulta de nutrición.")
            )
            return state
    
    async def _welcome_node(self, state: GraphState) -> GraphState:
        """
        Nodo de bienvenida para nuevos usuarios o mensajes de saludo
        
        Args:
            state: Estado actual del grafo
            
        Returns:
            Estado actualizado con mensaje de bienvenida
        """
        try:
            logger.info("👋 Procesando mensaje de bienvenida")
            
            welcome_message = """¡Hola! Bienvenido a FaiTracker 🌟

🎯 **Tu plataforma de fitness y nutrición inteligente**

Tienes acceso a nuestros expertos:

💪 **Sebastián** - Tu entrenador personal de fitness
• Rutinas personalizadas y seguimiento de entrenamientos
• Registro en tiempo real de ejercicios y progreso
• Técnicas correctas y prevención de lesiones
• Más de 98 ejercicios en nuestra base de datos

🌙 **Luna** - Tu coach de nutrición
• Registro inteligente de comidas con análisis de macros
• Planes de dieta personalizados y seguimiento nutricional  
• Recomendaciones basadas en tus objetivos
• Base de datos nutricional completa

✨ **¿Qué quieres hacer hoy?**

Puedes preguntarme sobre:
🏋️ Fitness: "quiero entrenar", "rutina de pecho", "registrar mi workout"
🥗 Nutrición: "qué comidas tengo hoy", "registrar mi desayuno", "análisis nutricional"

¡Estamos aquí para ayudarte a alcanzar tus objetivos! 💪🌟"""
            
            # Agregar mensaje de bienvenida a los mensajes
            state["messages"].append(AIMessage(content=welcome_message))
            
            logger.info("✅ Mensaje de bienvenida enviado")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error en nodo de bienvenida: {str(e)}")
            state["messages"].append(
                AIMessage(content="¡Hola! Bienvenido a FaiTracker. ¿En qué puedo ayudarte hoy?")
            )
            return state

    
    async def process_message(
        self, 
        user_input: str, 
        image_data: Optional[bytes] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Procesar mensaje del usuario a través del sistema multi-agente
        
        Args:
            user_input: Mensaje del usuario
            image_data: Datos de imagen si existe
            context: Contexto adicional
            
        Returns:
            Respuesta generada por el sistema
        """
        try:
            # Preparar estado inicial simplificado
            initial_state = GraphState(
                messages=[HumanMessage(content=user_input)],
                next_agent=None,
                context=context
            )
            
            # Log de inicio de procesamiento
            logger.info(f"🚀 Iniciando procesamiento de mensaje: '{user_input[:50]}...'")
            
            # Ejecutar el grafo
            try:
                # Ejecutar el grafo con el estado inicial
                final_state = await self.graph.ainvoke(initial_state)
                
                # Extraer la última respuesta de los mensajes
                if final_state["messages"]:
                    # Buscar la última respuesta de un agente (AIMessage)
                    for message in reversed(final_state["messages"]):
                        if isinstance(message, AIMessage) and message.content:
                            logger.info("✅ Mensaje procesado exitosamente por el sistema multi-agente")
                            return message.content
                
                # Si no hay respuesta, devolver mensaje por defecto
                logger.warning("⚠️ No se encontró respuesta en el estado final")
                return "Lo siento, no pude procesar tu mensaje. Por favor, intenta reformular tu pregunta."
                
            except Exception as ge:
                # Error general en el grafo
                logger.error(f"❌ Error en ejecución del grafo: {str(ge)}")
                import traceback
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                return "Ocurrió un error al procesar tu mensaje. Por favor, intenta más tarde."
            
        except Exception as e:
            # Error general en la preparación
            logger.error(f"❌ Error general en el coordinador: {str(e)}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return "Ocurrió un error al procesar tu mensaje. Por favor, intenta más tarde."
    
    def visualize_graph(self) -> str:
        """
        Obtener representación visual del grafo (para debugging)
        
        Returns:
            Representación en string del grafo
        """
        try:
            # LangGraph puede generar una representación del grafo
            return self.graph.get_graph().draw_mermaid()
        except:
            return "Grafo de flujo: START -> supervisor -> [fitness_agent|nutrition_agent|FINISH] -> supervisor -> END"
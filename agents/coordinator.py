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
from .nutrition_agent import NutritionAgent
from config.settings import get_settings

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
            raise RuntimeError(f"No se pudo inicializar el modelo Claude: {str(e)}")
        
        # Inicializar agentes especializados
        self.agents = {}
        try:
            # Solo necesitamos fitness y nutrition según el requerimiento
            self.fitness_agent = FitnessAgent()
            logger.info("✅ Agente de Fitness inicializado")
            
            self.nutrition_agent = NutritionAgent()
            logger.info("✅ Agente de Nutrición inicializado")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando agentes: {str(e)}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            raise
        
        # Construir el grafo de flujo
        try:
            self.graph = self._build_graph()
            logger.info("✅ Grafo de flujo construido correctamente")
        except Exception as e:
            logger.error(f"❌ Error construyendo grafo: {str(e)}")
            raise RuntimeError(f"No se pudo construir el grafo: {str(e)}")
        
        logger.info("✅ Coordinador multi-agente inicializado con LangGraph")
    
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
        
        # Definir el flujo - supervisor como punto de entrada
        workflow.add_edge(START, "supervisor")
        
        # Agregar edges condicionales desde el supervisor
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next_agent"],
            {
                "fitness_agent": "fitness_agent",
                "nutrition_agent": "nutrition_agent",
                "FINISH": END
            }
        )
        
        # Los agentes retornan al supervisor
        workflow.add_edge("fitness_agent", END)
        workflow.add_edge("nutrition_agent", END)
        
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
            - fitness_agent: Experto en ejercicio, rutinas, técnicas de entrenamiento y fitness
            - nutrition_agent: Experto en nutrición, dietas, calorías y alimentación saludable

            Analiza la consulta del usuario y decide:
            1. Si debe ir al fitness_agent
            2. Si debe ir al nutrition_agent  
            3. Si ya se ha respondido completamente, responde FINISH

            Responde SOLO con uno de estos valores: fitness_agent, nutrition_agent, o FINISH
            """),
            ("human", "{input}")
        ])
        
        # Invocar al supervisor para decidir el siguiente agente
        try:
            chain = supervisor_prompt | self.supervisor_llm 
            result = chain.invoke({"input": last_message.content})
            # Extraer la decisión
            next_agent = result.content.strip()
            # Validar la respuesta
            valid_agents = ["fitness_agent", "nutrition_agent", "FINISH"]
            if next_agent not in valid_agents:
                # Si hay palabras clave, intentar inferir
                content_lower = last_message.content.lower()
                if any(word in content_lower for word in ["ejercicio", "rutina", "entrenar", "fitness", "gym"]):
                    next_agent = "fitness_agent"
                elif any(word in content_lower for word in ["comida", "dieta", "nutrición", "calorías", "alimentación"]):
                    next_agent = "nutrition_agent"
                else:
                    next_agent = "fitness_agent"  # Default
            
            logger.info(f"🎯 Supervisor decidió: {next_agent}")
            
            state["next_agent"] = next_agent
            return state
        
        except Exception as e:
            logger.error(f"❌ Error en supervisor: {str(e)}")
            state["next_agent"] = "FINISH"
            return state
        
    
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
                
                # Llamar al agente de fitness con herramientas
                response = await self.fitness_agent.process_with_tools(
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
                
                # Llamar al agente de nutrición
                response = await self.nutrition_agent.process(user_query)
                
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
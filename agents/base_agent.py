"""
Agente base con funcionalidad común para todos los agentes
"""
import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from config.settings import get_settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Clase base para todos los agentes del sistema
    """
    
    def __init__(self, name: str, system_prompt: str):
        """
        Inicializar agente base
        
        Args:
            name: Nombre del agente
            system_prompt: Prompt del sistema para este agente
        """
        self.name = name
        self.settings = get_settings()
        self.system_prompt = system_prompt
        
        # Inicializar modelo de Claude
        try:
            self.llm = ChatAnthropic(
                api_key=self.settings.ANTHROPIC_API_KEY,
                model=self.settings.CLAUDE_MODEL,
                temperature=0,
                max_tokens=1024,
            )
        except Exception as e:
            logger.error(f"❌ Error inicializando ChatAnthropic: {str(e)}")
            # Crear un LLM mock para pruebas
            self.llm = None
        
        # Memoria del agente
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info(f"✅ Agente {name} inicializado con modelo {self.settings.CLAUDE_MODEL}")
    
    async def process(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Procesar entrada y generar respuesta
        
        Args:
            input_text: Texto de entrada del usuario
            context: Contexto adicional opcional
            
        Returns:
            Respuesta generada por el agente
        """
        try:
            if self.llm is None:
                return f"Hola! Soy tu asistente de {self.name.lower()}. He recibido tu mensaje: '{input_text}'. En este momento estoy en modo limitado, pero puedo ayudarte con información básica."
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=input_text)
            ]
            
            # Agregar contexto si existe
            if context:
                context_str = self._format_context(context)
                messages.insert(1, SystemMessage(content=f"Contexto adicional: {context_str}"))
            
            # Generar respuesta
            response = await self.llm.ainvoke(messages)
            
            # Guardar en memoria
            self.memory.save_context(
                {"input": input_text},
                {"output": response.content}
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Error en agente {self.name}: {str(e)}")
            return "Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente o reformula tu pregunta."
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Formatear contexto para incluir en el prompt
        
        Args:
            context: Diccionario con contexto
            
        Returns:
            String formateado con el contexto
        """
        formatted_parts = []
        for key, value in context.items():
            formatted_parts.append(f"{key}: {value}")
        return "\n".join(formatted_parts)
    
    def clear_memory(self):
        """
        Limpiar memoria del agente
        """
        self.memory.clear()
        logger.info(f"🧹 Memoria del agente {self.name} limpiada")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """
        Obtener historial de conversación
        
        Returns:
            Lista de mensajes en la memoria
        """
        return self.memory.chat_memory.messages

"""
Agente base con funcionalidad común para todos los agentes
"""
import logging
from typing import Dict, Any, Optional, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from config.settings import get_settings
from config.memory_config import create_optimized_memory, MemoryConfig
from agents.basic_memory import BasicPersistentMemory
from agents.optimized_memory import OptimizedMemory, UltraCompactMemory

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Clase base para todos los agentes del sistema
    """
    
    def __init__(self, name: str, system_prompt: str, user_id: Optional[str] = None):
        """
        Inicializar agente base
        
        Args:
            name: Nombre del agente
            system_prompt: Prompt del sistema para este agente
            user_id: ID del usuario para memoria persistente (opcional)
        """
        self.name = name
        self.settings = get_settings()
        self.system_prompt = system_prompt
        self.user_id = user_id
        
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
        
        # Memoria del agente - usar memoria optimizada configurada para ahorrar tokens
        if user_id:
            try:
                # Crear memoria optimizada según configuración de entorno
                self.memory = create_optimized_memory(
                    user_id=user_id,
                    memory_key="chat_history"
                )
                
                mode = MemoryConfig.get_memory_mode()
                settings = MemoryConfig.get_memory_settings(mode)
                logger.info(f"✅ Memoria optimizada inicializada para usuario: {user_id}")
                logger.info(f"🎛️ Modo: {mode.value} - {settings['description']}")
                
            except Exception as e:
                logger.error(f"❌ Error inicializando memoria optimizada: {str(e)}")
                # Fallback a memoria básica
                try:
                    self.memory = BasicPersistentMemory(
                        user_id=user_id,
                        memory_key="chat_history",
                        return_messages=True
                    )
                    logger.info("⚠️ Usando memoria básica como fallback")
                except Exception as e2:
                    logger.error(f"❌ Error con memoria básica: {str(e2)}")
                    # Último fallback a memoria en memoria
                    self.memory = ConversationBufferMemory(
                        memory_key="chat_history",
                        return_messages=True
                    )
                    logger.info("⚠️ Usando memoria en memoria como último fallback")
        else:
            # Memoria en memoria por defecto
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            logger.info("📝 Usando memoria en memoria (sin persistencia)")
        
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
            
            # Cargar memoria optimizada
            memory_variables = self.memory.load_memory_variables({})
            chat_history = memory_variables.get("chat_history", "")
            
            messages = [
                SystemMessage(content=self.system_prompt),
            ]
            
            # Agregar historial compacto si existe
            if chat_history:
                messages.append(SystemMessage(content=f"Contexto: {chat_history}"))
            
            # Agregar contexto adicional si existe (también compacto)
            if context:
                context_str = self._format_context(context)
                # Limitar contexto adicional también
                if len(context_str) > 300:
                    context_str = context_str[:300] + "..."
                messages.append(SystemMessage(content=f"Info: {context_str}"))
            
            # Mensaje del usuario
            messages.append(HumanMessage(content=input_text))
            
            # Log del tamaño total del prompt para monitoreo
            total_chars = sum(len(msg.content) for msg in messages)
            logger.info(f"📊 Prompt total: {total_chars} caracteres, {len(messages)} mensajes")
            
            # Generar respuesta
            response = await self.llm.ainvoke(messages)
            
            # Guardar en memoria optimizada
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
        if hasattr(self.memory, 'chat_memory'):
            return self.memory.chat_memory.messages
        else:
            # Para memoria persistente, cargar desde BD
            memory_vars = self.memory.load_memory_variables({})
            return memory_vars.get("chat_history", [])
    
    async def get_conversation_summary(self) -> str:
        """
        Obtener resumen de la conversación actual
        
        Returns:
            Resumen de la conversación
        """
        if isinstance(self.memory, BasicPersistentMemory):
            return await self.memory.get_conversation_summary()
        else:
            # Para memoria en memoria, crear resumen básico
            messages = self.get_conversation_history()
            human_count = len([m for m in messages if isinstance(m, HumanMessage)])
            ai_count = len([m for m in messages if isinstance(m, AIMessage)])
            return f"Conversación en memoria: {len(messages)} mensajes ({human_count} del usuario, {ai_count} del asistente)"
    
    async def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Agregar un mensaje del sistema a la conversación
        
        Args:
            content: Contenido del mensaje del sistema
            metadata: Metadatos adicionales
        """
        if isinstance(self.memory, BasicPersistentMemory):
            # Para memoria persistente básica, agregar directamente
            system_message = SystemMessage(content=content)
            self.memory.add_message(system_message)
        else:
            # Para memoria en memoria, agregar directamente
            system_message = SystemMessage(content=content)
            if hasattr(self.memory, 'chat_memory'):
                self.memory.chat_memory.add_message(system_message)

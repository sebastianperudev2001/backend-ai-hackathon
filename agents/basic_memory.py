"""
Memoria básica que funciona sin problemas de Pydantic
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from domain.models import (
    ConversationMessageType, AddMessageRequest, ConversationMessage
)
from repository.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class BasicPersistentMemory:
    """
    Memoria persistente básica que no depende de herencia de Pydantic
    """
    
    def __init__(self, user_id: str, memory_key: str = "chat_history", return_messages: bool = True):
        """
        Inicializar memoria persistente básica
        
        Args:
            user_id: ID del usuario
            memory_key: Clave para la memoria en el contexto
            return_messages: Si retornar mensajes como objetos o como string
        """
        self.user_id = user_id
        self.memory_key = memory_key
        self.return_messages = return_messages
        self.session_id = None
        self.conversation_repo = ConversationRepository()
        self.local_messages = []  # Backup local
        
        logger.info(f"✅ Memoria persistente básica inicializada para usuario: {user_id}")
    
    async def ensure_session(self) -> str:
        """
        Asegurar que existe una sesión activa
        
        Returns:
            ID de la sesión
        """
        if not self.session_id:
            try:
                # Obtener o crear sesión activa
                response = await self.conversation_repo.get_or_create_active_session(self.user_id)
                if response.success and response.session:
                    self.session_id = response.session.id
                    logger.info(f"✅ Sesión establecida: {self.session_id}")
                else:
                    logger.error(f"❌ Error estableciendo sesión: {response.error}")
                    raise RuntimeError(f"No se pudo establecer sesión: {response.error}")
            except Exception as e:
                logger.error(f"❌ Error obteniendo sesión: {str(e)}")
                # Usar una sesión temporal
                self.session_id = f"temp_session_{self.user_id}"
                logger.warning(f"⚠️ Usando sesión temporal: {self.session_id}")
        
        return self.session_id
    
    @property
    def memory_variables(self) -> List[str]:
        """Variables que esta memoria proporciona"""
        return [self.memory_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cargar variables de memoria
        
        Args:
            inputs: Inputs del usuario
            
        Returns:
            Diccionario con las variables de memoria
        """
        try:
            # Intentar cargar desde BD, pero usar local como fallback
            messages = self._load_messages_sync()
            
            if self.return_messages:
                return {self.memory_key: messages}
            else:
                buffer = self._messages_to_string(messages)
                return {self.memory_key: buffer}
                
        except Exception as e:
            logger.error(f"❌ Error cargando memoria: {str(e)}")
            # Retornar memoria local
            if self.return_messages:
                return {self.memory_key: self.local_messages}
            else:
                buffer = self._messages_to_string(self.local_messages)
                return {self.memory_key: buffer}
    
    def _load_messages_sync(self) -> List[BaseMessage]:
        """
        Cargar mensajes de forma síncrona (usando local como fallback)
        
        Returns:
            Lista de mensajes
        """
        try:
            # Por ahora, retornar mensajes locales para evitar problemas de async
            # En producción se podría implementar carga desde BD
            return self.local_messages.copy()
            
        except Exception as e:
            logger.error(f"❌ Error cargando mensajes: {str(e)}")
            return []
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de la conversación
        
        Args:
            inputs: Inputs del usuario
            outputs: Outputs del agente
        """
        try:
            # Guardar en memoria local inmediatamente
            input_key = "input"
            output_key = "output"
            
            if input_key in inputs:
                human_msg = HumanMessage(content=inputs[input_key])
                self.local_messages.append(human_msg)
            
            if output_key in outputs:
                ai_msg = AIMessage(content=outputs[output_key])
                self.local_messages.append(ai_msg)
            
            # Intentar guardar en BD de forma asíncrona (sin bloquear)
            try:
                import asyncio
                asyncio.create_task(self._save_context_async(inputs, outputs))
            except Exception as async_error:
                logger.warning(f"⚠️ No se pudo guardar en BD async: {async_error}")
            
            logger.info("✅ Contexto guardado en memoria local")
            
        except Exception as e:
            logger.error(f"❌ Error guardando contexto: {str(e)}")
    
    async def _save_context_async(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de forma asíncrona en BD
        """
        try:
            session_id = await self.ensure_session()
            
            if session_id.startswith("temp_"):
                # No guardar sesiones temporales
                return
            
            # Guardar mensaje del usuario
            if "input" in inputs:
                user_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.HUMAN,
                    content=inputs["input"],
                    metadata={"source": "user_input"}
                )
                await self.conversation_repo.add_message(user_message)
            
            # Guardar respuesta del agente
            if "output" in outputs:
                ai_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.AI,
                    content=outputs["output"],
                    metadata={"source": "agent_response"}
                )
                await self.conversation_repo.add_message(ai_message)
            
            logger.info("✅ Contexto guardado en BD")
            
        except Exception as e:
            logger.error(f"❌ Error guardando contexto async: {str(e)}")
    
    def clear(self) -> None:
        """
        Limpiar memoria
        """
        self.local_messages.clear()
        logger.info("🧹 Memoria local limpiada")
    
    def _messages_to_string(self, messages: List[BaseMessage]) -> str:
        """
        Convertir lista de mensajes a string
        
        Args:
            messages: Lista de mensajes
            
        Returns:
            String con los mensajes formateados
        """
        string_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                string_messages.append(f"Usuario: {message.content}")
            elif isinstance(message, AIMessage):
                string_messages.append(f"Asistente: {message.content}")
            elif isinstance(message, SystemMessage):
                string_messages.append(f"Sistema: {message.content}")
        
        return "\n".join(string_messages)
    
    async def get_conversation_summary(self) -> str:
        """
        Obtener un resumen de la conversación actual
        
        Returns:
            Resumen de la conversación
        """
        try:
            # Usar mensajes locales para el resumen
            total_messages = len(self.local_messages)
            human_messages = len([m for m in self.local_messages if isinstance(m, HumanMessage)])
            ai_messages = len([m for m in self.local_messages if isinstance(m, AIMessage)])
            
            return f"Conversación activa: {total_messages} mensajes ({human_messages} del usuario, {ai_messages} del asistente)"
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen: {str(e)}")
            return "Error obteniendo resumen de conversación"
    
    # Métodos para compatibilidad con LangChain
    @property
    def chat_memory(self):
        """Propiedad para compatibilidad con LangChain"""
        return self
    
    @property
    def messages(self):
        """Mensajes para compatibilidad con LangChain"""
        return self.local_messages
    
    def add_message(self, message: BaseMessage):
        """Agregar mensaje para compatibilidad con LangChain"""
        self.local_messages.append(message)

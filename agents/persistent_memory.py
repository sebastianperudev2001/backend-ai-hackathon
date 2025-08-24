"""
Memoria persistente personalizada para LangChain que se integra con Supabase
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import Field

from domain.models import (
    ConversationMessageType, AddMessageRequest, ConversationMessage
)
from repository.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class PersistentChatMemory(BaseChatMemory):
    """
    Memoria de chat persistente que almacena conversaciones en Supabase
    y se integra con LangChain
    """
    
    conversation_repo: ConversationRepository = Field(default_factory=ConversationRepository)
    session_id: Optional[str] = Field(default=None)
    user_id: str = Field(...)
    max_token_limit: int = Field(default=4000)
    return_messages: bool = Field(default=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, user_id: str, session_id: Optional[str] = None, **kwargs):
        """
        Inicializar memoria persistente
        
        Args:
            user_id: ID del usuario
            session_id: ID de la sesión (opcional, se creará una si no se proporciona)
            **kwargs: Argumentos adicionales
        """
        # Establecer user_id antes de llamar a super().__init__
        self.user_id = user_id
        self.session_id = session_id
        self.conversation_repo = ConversationRepository()
        
        # Llamar a super().__init__ con los kwargs necesarios
        super().__init__(**kwargs)
        
        logger.info(f"✅ Memoria persistente inicializada para usuario: {user_id}")
    
    async def ensure_session(self) -> str:
        """
        Asegurar que existe una sesión activa
        
        Returns:
            ID de la sesión
        """
        if not self.session_id:
            # Obtener o crear sesión activa
            response = await self.conversation_repo.get_or_create_active_session(self.user_id)
            if response.success and response.session:
                self.session_id = response.session.id
                logger.info(f"✅ Sesión establecida: {self.session_id}")
            else:
                logger.error(f"❌ Error estableciendo sesión: {response.error}")
                raise RuntimeError(f"No se pudo establecer sesión: {response.error}")
        
        return self.session_id
    
    @property
    def memory_variables(self) -> List[str]:
        """Variables que esta memoria proporciona"""
        return [self.memory_key]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cargar variables de memoria desde la base de datos
        
        Args:
            inputs: Inputs del usuario
            
        Returns:
            Diccionario con las variables de memoria
        """
        try:
            # Cargar mensajes desde la base de datos de forma síncrona
            # Nota: En un entorno async real, esto debería ser manejado diferente
            import asyncio
            
            # Obtener el loop de eventos actual o crear uno nuevo
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si ya hay un loop corriendo, crear una tarea
                    messages = []
                    logger.warning("⚠️ Loop de eventos ya corriendo, usando memoria local")
                else:
                    messages = loop.run_until_complete(self._load_messages_async())
            except RuntimeError:
                # No hay loop de eventos, crear uno nuevo
                messages = asyncio.run(self._load_messages_async())
            
            if self.return_messages:
                return {self.memory_key: messages}
            else:
                # Convertir mensajes a string
                buffer = self._messages_to_string(messages)
                return {self.memory_key: buffer}
                
        except Exception as e:
            logger.error(f"❌ Error cargando memoria: {str(e)}")
            # Retornar memoria vacía en caso de error
            return {self.memory_key: [] if self.return_messages else ""}
    
    async def _load_messages_async(self) -> List[BaseMessage]:
        """
        Cargar mensajes de forma asíncrona
        
        Returns:
            Lista de mensajes de LangChain
        """
        try:
            session_id = await self.ensure_session()
            
            # Obtener mensajes recientes (últimos 30 mensajes o 60 minutos)
            recent_messages = await self.conversation_repo.get_recent_messages(
                session_id=session_id,
                minutes=60,
                limit=30
            )
            
            # Convertir a mensajes de LangChain
            langchain_messages = []
            for msg in recent_messages:
                if msg.message_type == ConversationMessageType.HUMAN:
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.message_type == ConversationMessageType.AI:
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.message_type == ConversationMessageType.SYSTEM:
                    langchain_messages.append(SystemMessage(content=msg.content))
            
            logger.info(f"✅ Mensajes cargados desde BD: {len(langchain_messages)}")
            return langchain_messages
            
        except Exception as e:
            logger.error(f"❌ Error cargando mensajes async: {str(e)}")
            return []
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de la conversación en la base de datos
        
        Args:
            inputs: Inputs del usuario
            outputs: Outputs del agente
        """
        try:
            import asyncio
            
            # Ejecutar guardado de forma asíncrona
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si ya hay un loop corriendo, crear una tarea en background
                    asyncio.create_task(self._save_context_async(inputs, outputs))
                else:
                    loop.run_until_complete(self._save_context_async(inputs, outputs))
            except RuntimeError:
                # No hay loop de eventos, crear uno nuevo
                asyncio.run(self._save_context_async(inputs, outputs))
                
        except Exception as e:
            logger.error(f"❌ Error guardando contexto: {str(e)}")
    
    async def _save_context_async(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de forma asíncrona
        
        Args:
            inputs: Inputs del usuario
            outputs: Outputs del agente
        """
        try:
            session_id = await self.ensure_session()
            
            # Guardar mensaje del usuario
            if self.input_key in inputs:
                user_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.HUMAN,
                    content=inputs[self.input_key],
                    metadata={"source": "user_input"}
                )
                await self.conversation_repo.add_message(user_message)
            
            # Guardar respuesta del agente
            if self.output_key in outputs:
                ai_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.AI,
                    content=outputs[self.output_key],
                    metadata={"source": "agent_response"}
                )
                await self.conversation_repo.add_message(ai_message)
            
            logger.info("✅ Contexto guardado en BD")
            
        except Exception as e:
            logger.error(f"❌ Error guardando contexto async: {str(e)}")
    
    def clear(self) -> None:
        """
        Limpiar memoria (crear nueva sesión)
        """
        try:
            import asyncio
            
            # Desactivar sesión actual y crear una nueva
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._clear_async())
                else:
                    loop.run_until_complete(self._clear_async())
            except RuntimeError:
                asyncio.run(self._clear_async())
                
        except Exception as e:
            logger.error(f"❌ Error limpiando memoria: {str(e)}")
    
    async def _clear_async(self) -> None:
        """
        Limpiar memoria de forma asíncrona
        """
        try:
            if self.session_id:
                # Marcar sesión actual como inactiva
                # (esto se podría implementar en el repositorio si es necesario)
                pass
            
            # Crear nueva sesión
            response = await self.conversation_repo.get_or_create_active_session(self.user_id)
            if response.success and response.session:
                self.session_id = response.session.id
                logger.info(f"✅ Nueva sesión creada: {self.session_id}")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando memoria async: {str(e)}")
    
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
    
    async def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Agregar un mensaje del sistema
        
        Args:
            content: Contenido del mensaje
            metadata: Metadatos adicionales
        """
        try:
            session_id = await self.ensure_session()
            
            system_message = AddMessageRequest(
                session_id=session_id,
                message_type=ConversationMessageType.SYSTEM,
                content=content,
                metadata=metadata or {"source": "system"}
            )
            
            await self.conversation_repo.add_message(system_message)
            logger.info("✅ Mensaje del sistema agregado")
            
        except Exception as e:
            logger.error(f"❌ Error agregando mensaje del sistema: {str(e)}")
    
    async def get_conversation_summary(self) -> str:
        """
        Obtener un resumen de la conversación actual
        
        Returns:
            Resumen de la conversación
        """
        try:
            if not self.session_id:
                return "No hay conversación activa"
            
            # Obtener historial completo
            history_response = await self.conversation_repo.get_conversation_history(
                session_id=self.session_id,
                limit=100
            )
            
            if not history_response.success:
                return "Error obteniendo historial"
            
            # Crear resumen básico
            total_messages = history_response.total_messages
            human_messages = len([m for m in history_response.messages if m.message_type == ConversationMessageType.HUMAN])
            ai_messages = len([m for m in history_response.messages if m.message_type == ConversationMessageType.AI])
            
            if history_response.session:
                session_duration = (datetime.now() - history_response.session.started_at).total_seconds() / 60
                return f"Conversación activa: {total_messages} mensajes ({human_messages} del usuario, {ai_messages} del asistente) en {session_duration:.1f} minutos"
            else:
                return f"Conversación: {total_messages} mensajes ({human_messages} del usuario, {ai_messages} del asistente)"
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen: {str(e)}")
            return "Error obteniendo resumen de conversación"

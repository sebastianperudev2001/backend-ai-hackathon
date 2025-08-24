"""
Memoria persistente simplificada que evita problemas de Pydantic
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from domain.models import (
    ConversationMessageType, AddMessageRequest, ConversationMessage
)
from repository.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class SimplePersistentMemory(BaseChatMemory):
    """
    Memoria persistente simplificada que almacena conversaciones en Supabase
    """
    
    def __init__(self, user_id: str, session_id: Optional[str] = None, **kwargs):
        """
        Inicializar memoria persistente simplificada
        
        Args:
            user_id: ID del usuario
            session_id: ID de la sesión (opcional)
            **kwargs: Argumentos para BaseChatMemory
        """
        # Establecer valores por defecto para kwargs
        if 'memory_key' not in kwargs:
            kwargs['memory_key'] = 'chat_history'
        if 'return_messages' not in kwargs:
            kwargs['return_messages'] = True
        
        # Inicializar clase padre
        super().__init__(**kwargs)
        
        # Establecer propiedades propias
        self.user_id = user_id
        self.session_id = session_id
        self.conversation_repo = ConversationRepository()
        self.max_token_limit = 4000
        
        logger.info(f"✅ Memoria persistente simple inicializada para usuario: {user_id}")
    
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
            import asyncio
            
            # Obtener el loop de eventos actual o crear uno nuevo
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si ya hay un loop corriendo, usar memoria local por ahora
                    messages = self._get_local_messages()
                    logger.warning("⚠️ Loop de eventos corriendo, usando memoria local")
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
            # Retornar memoria local como fallback
            local_messages = self._get_local_messages()
            if self.return_messages:
                return {self.memory_key: local_messages}
            else:
                buffer = self._messages_to_string(local_messages)
                return {self.memory_key: buffer}
    
    def _get_local_messages(self) -> List[BaseMessage]:
        """
        Obtener mensajes de la memoria local
        
        Returns:
            Lista de mensajes locales
        """
        if hasattr(self, 'chat_memory') and hasattr(self.chat_memory, 'messages'):
            return self.chat_memory.messages
        return []
    
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
            return self._get_local_messages()
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de la conversación
        
        Args:
            inputs: Inputs del usuario
            outputs: Outputs del agente
        """
        try:
            # Primero guardar en memoria local
            super().save_context(inputs, outputs)
            
            # Luego intentar guardar en BD de forma asíncrona
            import asyncio
            
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
            # Continuar con memoria local
    
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
        Limpiar memoria
        """
        super().clear()
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
            # Fallback a resumen local
            local_messages = self._get_local_messages()
            human_count = len([m for m in local_messages if isinstance(m, HumanMessage)])
            ai_count = len([m for m in local_messages if isinstance(m, AIMessage)])
            return f"Conversación local: {len(local_messages)} mensajes ({human_count} del usuario, {ai_count} del asistente)"

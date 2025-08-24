"""
Memoria optimizada para reducir el costo de tokens en prompts
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from domain.models import (
    ConversationMessageType, AddMessageRequest, ConversationMessage
)
from repository.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class OptimizedMemory:
    """
    Memoria optimizada que minimiza el volumen de datos enviados a Claude
    """
    
    def __init__(self, user_id: str, memory_key: str = "chat_history", 
                 max_context_messages: int = 6, max_chars_per_message: int = 200):
        """
        Inicializar memoria optimizada
        
        Args:
            user_id: ID del usuario
            memory_key: Clave para la memoria en el contexto
            max_context_messages: Número máximo de mensajes a incluir (default: 6)
            max_chars_per_message: Máximo de caracteres por mensaje (default: 200)
        """
        self.user_id = user_id
        self.memory_key = memory_key
        self.session_id = None
        self.conversation_repo = ConversationRepository()
        self.local_messages = []
        
        # Configuración para optimizar tokens
        self.max_context_messages = max_context_messages  # Solo los últimos 6 mensajes
        self.max_chars_per_message = max_chars_per_message  # Truncar mensajes largos
        
        logger.info(f"✅ Memoria optimizada inicializada para usuario: {user_id}")
        logger.info(f"📊 Configuración: max_messages={max_context_messages}, max_chars={max_chars_per_message}")
    
    async def ensure_session(self) -> str:
        """Asegurar que existe una sesión activa"""
        if not self.session_id:
            try:
                response = await self.conversation_repo.get_or_create_active_session(self.user_id)
                if response.success and response.session:
                    self.session_id = response.session.id
                    logger.info(f"✅ Sesión establecida: {self.session_id}")
                else:
                    logger.error(f"❌ Error estableciendo sesión: {response.error}")
                    self.session_id = f"temp_session_{self.user_id}"
                    logger.warning(f"⚠️ Usando sesión temporal: {self.session_id}")
            except Exception as e:
                logger.error(f"❌ Error obteniendo sesión: {str(e)}")
                self.session_id = f"temp_session_{self.user_id}"
        
        return self.session_id
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cargar variables de memoria optimizadas
        """
        try:
            # Usar mensajes locales optimizados
            optimized_messages = self._get_optimized_messages()
            
            # Convertir a string compacto
            context_string = self._messages_to_compact_string(optimized_messages)
            
            return {self.memory_key: context_string}
                
        except Exception as e:
            logger.error(f"❌ Error cargando memoria: {str(e)}")
            return {self.memory_key: ""}
    
    def _get_optimized_messages(self) -> List[BaseMessage]:
        """
        Obtener mensajes optimizados para el contexto
        
        Returns:
            Lista reducida y optimizada de mensajes
        """
        # Obtener solo los últimos N mensajes
        recent_messages = self.local_messages[-self.max_context_messages:] if self.local_messages else []
        
        # Truncar mensajes muy largos
        optimized_messages = []
        for msg in recent_messages:
            content = msg.content
            if self.max_chars_per_message and len(content) > self.max_chars_per_message:
                content = content[:self.max_chars_per_message] + "..."
            
            if isinstance(msg, HumanMessage):
                optimized_messages.append(HumanMessage(content=content))
            elif isinstance(msg, AIMessage):
                optimized_messages.append(AIMessage(content=content))
            elif isinstance(msg, SystemMessage):
                optimized_messages.append(SystemMessage(content=content))
        
        return optimized_messages
    
    def _messages_to_compact_string(self, messages: List[BaseMessage]) -> str:
        """
        Convertir mensajes a string compacto para ahorrar tokens
        """
        if not messages:
            return ""
        
        compact_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                compact_messages.append(f"U: {msg.content}")
            elif isinstance(msg, AIMessage):
                compact_messages.append(f"A: {msg.content}")
            elif isinstance(msg, SystemMessage):
                compact_messages.append(f"S: {msg.content}")
        
        # Unir con separador mínimo
        context = " | ".join(compact_messages)
        
        # Log del tamaño para monitoreo
        logger.info(f"📏 Contexto generado: {len(context)} caracteres, {len(messages)} mensajes")
        
        return context
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Guardar contexto de la conversación
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
            
            # Mantener solo los últimos mensajes en memoria local para ahorrar RAM
            max_local_messages = self.max_context_messages * 2  # Un poco más para buffer
            if len(self.local_messages) > max_local_messages:
                # Mantener solo los más recientes
                self.local_messages = self.local_messages[-max_local_messages:]
                logger.info(f"🧹 Memoria local limpiada, manteniendo {len(self.local_messages)} mensajes")
            
            # Intentar guardar en BD de forma asíncrona (sin bloquear)
            try:
                import asyncio
                asyncio.create_task(self._save_context_async(inputs, outputs))
            except Exception as async_error:
                logger.warning(f"⚠️ No se pudo guardar en BD async: {async_error}")
            
            logger.info("✅ Contexto guardado en memoria local optimizada")
            
        except Exception as e:
            logger.error(f"❌ Error guardando contexto: {str(e)}")
    
    async def _save_context_async(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Guardar contexto de forma asíncrona en BD (opcional)"""
        try:
            session_id = await self.ensure_session()
            
            if session_id.startswith("temp_"):
                return  # No guardar sesiones temporales
            
            # Guardar mensaje del usuario
            if "input" in inputs:
                user_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.HUMAN,
                    content=inputs["input"],
                    metadata={"source": "user_input", "optimized": True}
                )
                await self.conversation_repo.add_message(user_message)
            
            # Guardar respuesta del agente
            if "output" in outputs:
                ai_message = AddMessageRequest(
                    session_id=session_id,
                    message_type=ConversationMessageType.AI,
                    content=outputs["output"],
                    metadata={"source": "agent_response", "optimized": True}
                )
                await self.conversation_repo.add_message(ai_message)
            
            logger.info("✅ Contexto guardado en BD")
            
        except Exception as e:
            logger.error(f"❌ Error guardando contexto async: {str(e)}")
    
    def clear(self) -> None:
        """Limpiar memoria"""
        self.local_messages.clear()
        logger.info("🧹 Memoria optimizada limpiada")
    
    @property
    def memory_variables(self) -> List[str]:
        """Variables que esta memoria proporciona"""
        return [self.memory_key]
    
    async def get_conversation_summary(self) -> str:
        """
        Obtener un resumen ultra compacto de la conversación
        """
        try:
            total_messages = len(self.local_messages)
            human_messages = len([m for m in self.local_messages if isinstance(m, HumanMessage)])
            ai_messages = len([m for m in self.local_messages if isinstance(m, AIMessage)])
            
            return f"Conv: {total_messages}msg ({human_messages}U, {ai_messages}A)"
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen: {str(e)}")
            return "Error en resumen"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la memoria para monitoreo
        """
        try:
            optimized_messages = self._get_optimized_messages()
            context_string = self._messages_to_compact_string(optimized_messages)
            
            return {
                "total_local_messages": len(self.local_messages),
                "context_messages": len(optimized_messages),
                "context_size_chars": len(context_string),
                "estimated_tokens": len(context_string) // 4,  # Estimación aproximada
                "max_configured_messages": self.max_context_messages,
                "max_chars_per_message": self.max_chars_per_message
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats: {str(e)}")
            return {"error": str(e)}


class UltraCompactMemory(OptimizedMemory):
    """
    Versión ultra compacta para casos donde se necesita minimizar al máximo los tokens
    """
    
    def __init__(self, user_id: str, memory_key: str = "chat_history"):
        # Configuración ultra agresiva para ahorrar tokens
        super().__init__(
            user_id=user_id,
            memory_key=memory_key,
            max_context_messages=4,  # Solo 4 mensajes
            max_chars_per_message=100  # Solo 100 caracteres por mensaje
        )
        logger.info("🔥 Memoria ULTRA COMPACTA activada - ahorro máximo de tokens")
    
    def _messages_to_compact_string(self, messages: List[BaseMessage]) -> str:
        """Version ultra compacta del contexto"""
        if not messages:
            return ""
        
        # Format ultra compacto: U:mensaje|A:respuesta
        compact = []
        for msg in messages[-2:]:  # Solo los últimos 2 mensajes
            if isinstance(msg, HumanMessage):
                compact.append(f"U:{msg.content[:50]}")  # Solo 50 chars
            elif isinstance(msg, AIMessage):
                compact.append(f"A:{msg.content[:50]}")  # Solo 50 chars
        
        result = "|".join(compact)
        logger.info(f"🔥 Contexto ultra compacto: {len(result)} chars")
        return result

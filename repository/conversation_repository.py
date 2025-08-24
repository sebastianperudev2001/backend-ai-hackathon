"""
Repositorio para gestionar el historial de conversaciones y memoria del chatbot
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from supabase import Client

from domain.models import (
    ConversationSession, ConversationMessage, ConversationMessageType,
    CreateSessionRequest, AddMessageRequest, ConversationHistoryResponse,
    SessionResponse
)
from repository.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class ConversationRepository:
    """
    Repositorio para operaciones de conversación y memoria
    """
    
    def __init__(self):
        """Inicializar repositorio"""
        from repository.supabase_client import get_supabase_direct_client
        self.client: Client = get_supabase_direct_client()
        
        if not self.client:
            logger.error("❌ Cliente de Supabase no inicializado en ConversationRepository")
            raise RuntimeError("Cliente de Supabase no disponible")
        
        logger.info("✅ ConversationRepository inicializado")
    
    def _set_user_context(self, user_id: str):
        """
        Establecer contexto de usuario para RLS
        
        Args:
            user_id: ID del usuario
        """
        try:
            from repository.supabase_client import get_supabase_client
            wrapper = get_supabase_client()
            wrapper.set_user_context(user_id)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo establecer contexto de usuario: {str(e)}")
            # Continuar sin contexto - las operaciones pueden fallar pero no crashear
    
    async def create_session(self, request: CreateSessionRequest) -> SessionResponse:
        """
        Crear una nueva sesión de conversación
        
        Args:
            request: Datos para crear la sesión
            
        Returns:
            Respuesta con la sesión creada
        """
        try:
            # Establecer contexto de usuario para RLS
            self._set_user_context(request.user_id)
            
            # Preparar datos para insertar
            session_data = {
                "user_id": request.user_id,
                "session_name": request.session_name,
                "metadata": request.metadata or {}
            }
            
            # Insertar en la base de datos
            result = self.client.table("conversation_sessions").insert(session_data).execute()
            
            if result.data:
                session_dict = result.data[0]
                session = ConversationSession(
                    id=session_dict["id"],
                    user_id=session_dict["user_id"],
                    session_name=session_dict.get("session_name"),
                    started_at=datetime.fromisoformat(session_dict["started_at"].replace('Z', '+00:00')),
                    last_activity_at=datetime.fromisoformat(session_dict["last_activity_at"].replace('Z', '+00:00')),
                    is_active=session_dict["is_active"],
                    metadata=session_dict.get("metadata"),
                    created_at=datetime.fromisoformat(session_dict["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(session_dict["updated_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"✅ Sesión creada: {session.id}")
                return SessionResponse(
                    success=True,
                    session=session,
                    message="Sesión creada exitosamente"
                )
            else:
                logger.error("❌ No se pudo crear la sesión")
                return SessionResponse(
                    success=False,
                    message="Error al crear la sesión",
                    error="No se recibieron datos de la base de datos"
                )
                
        except Exception as e:
            logger.error(f"❌ Error creando sesión: {str(e)}")
            return SessionResponse(
                success=False,
                message="Error al crear la sesión",
                error=str(e)
            )
    
    async def get_or_create_active_session(self, user_id: str, session_name: Optional[str] = None) -> SessionResponse:
        """
        Obtener la sesión activa del usuario o crear una nueva si no existe
        
        Args:
            user_id: ID del usuario
            session_name: Nombre opcional para la sesión
            
        Returns:
            Respuesta con la sesión activa
        """
        try:
            # Establecer contexto de usuario para RLS
            self._set_user_context(user_id)
            
            # Buscar sesión activa existente
            result = self.client.table("conversation_sessions")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .order("last_activity_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                # Usar sesión existente
                session_dict = result.data[0]
                session = ConversationSession(
                    id=session_dict["id"],
                    user_id=session_dict["user_id"],
                    session_name=session_dict.get("session_name"),
                    started_at=datetime.fromisoformat(session_dict["started_at"].replace('Z', '+00:00')),
                    last_activity_at=datetime.fromisoformat(session_dict["last_activity_at"].replace('Z', '+00:00')),
                    is_active=session_dict["is_active"],
                    metadata=session_dict.get("metadata"),
                    created_at=datetime.fromisoformat(session_dict["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(session_dict["updated_at"].replace('Z', '+00:00'))
                )
                
                logger.info(f"✅ Sesión activa encontrada: {session.id}")
                return SessionResponse(
                    success=True,
                    session=session,
                    message="Sesión activa encontrada"
                )
            else:
                # Crear nueva sesión
                logger.info(f"🆕 Creando nueva sesión para usuario: {user_id}")
                create_request = CreateSessionRequest(
                    user_id=user_id,
                    session_name=session_name or f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                return await self.create_session(create_request)
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo/creando sesión: {str(e)}")
            return SessionResponse(
                success=False,
                message="Error al obtener la sesión",
                error=str(e)
            )
    
    async def add_message(self, request: AddMessageRequest) -> bool:
        """
        Agregar un mensaje a la conversación
        
        Args:
            request: Datos del mensaje a agregar
            
        Returns:
            True si se agregó exitosamente
        """
        try:
            # Obtener user_id de la sesión para establecer contexto
            session_result = self.client.table("conversation_sessions")\
                .select("user_id")\
                .eq("id", request.session_id)\
                .single()\
                .execute()
            
            if session_result.data:
                self._set_user_context(session_result.data["user_id"])
            
            # Preparar datos para insertar
            message_data = {
                "session_id": request.session_id,
                "message_type": request.message_type.value,
                "content": request.content,
                "metadata": request.metadata or {},
                "agent_name": request.agent_name,
                "token_count": request.token_count
            }
            
            # Insertar en la base de datos
            result = self.client.table("conversation_messages").insert(message_data).execute()
            
            if result.data:
                logger.info(f"✅ Mensaje agregado a sesión {request.session_id}")
                return True
            else:
                logger.error("❌ No se pudo agregar el mensaje")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error agregando mensaje: {str(e)}")
            return False
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> ConversationHistoryResponse:
        """
        Obtener historial de conversación de una sesión
        
        Args:
            session_id: ID de la sesión
            limit: Número máximo de mensajes a obtener
            offset: Número de mensajes a saltar
            
        Returns:
            Respuesta con el historial de conversación
        """
        try:
            # Obtener información de la sesión
            session_result = self.client.table("conversation_sessions")\
                .select("*")\
                .eq("id", session_id)\
                .single()\
                .execute()
            
            if not session_result.data:
                return ConversationHistoryResponse(
                    success=False,
                    message="Sesión no encontrada",
                    error="La sesión especificada no existe"
                )
            
            # Convertir datos de sesión
            session_dict = session_result.data
            session = ConversationSession(
                id=session_dict["id"],
                user_id=session_dict["user_id"],
                session_name=session_dict.get("session_name"),
                started_at=datetime.fromisoformat(session_dict["started_at"].replace('Z', '+00:00')),
                last_activity_at=datetime.fromisoformat(session_dict["last_activity_at"].replace('Z', '+00:00')),
                is_active=session_dict["is_active"],
                metadata=session_dict.get("metadata"),
                created_at=datetime.fromisoformat(session_dict["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(session_dict["updated_at"].replace('Z', '+00:00'))
            )
            
            # Obtener mensajes de la conversación
            messages_result = self.client.table("conversation_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            messages = []
            if messages_result.data:
                for msg_dict in messages_result.data:
                    message = ConversationMessage(
                        id=msg_dict["id"],
                        session_id=msg_dict["session_id"],
                        message_type=ConversationMessageType(msg_dict["message_type"]),
                        content=msg_dict["content"],
                        metadata=msg_dict.get("metadata"),
                        agent_name=msg_dict.get("agent_name"),
                        token_count=msg_dict.get("token_count"),
                        created_at=datetime.fromisoformat(msg_dict["created_at"].replace('Z', '+00:00'))
                    )
                    messages.append(message)
            
            # Contar total de mensajes
            count_result = self.client.table("conversation_messages")\
                .select("id", count="exact")\
                .eq("session_id", session_id)\
                .execute()
            
            total_messages = count_result.count if count_result.count else 0
            
            logger.info(f"✅ Historial obtenido: {len(messages)} mensajes de {total_messages} total")
            
            return ConversationHistoryResponse(
                success=True,
                session=session,
                messages=messages,
                total_messages=total_messages,
                message=f"Historial obtenido exitosamente: {len(messages)} mensajes"
            )
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {str(e)}")
            return ConversationHistoryResponse(
                success=False,
                message="Error al obtener el historial",
                error=str(e)
            )
    
    async def get_recent_messages(
        self, 
        session_id: str, 
        minutes: int = 60,
        limit: int = 20
    ) -> List[ConversationMessage]:
        """
        Obtener mensajes recientes de una sesión
        
        Args:
            session_id: ID de la sesión
            minutes: Minutos hacia atrás para buscar mensajes
            limit: Número máximo de mensajes
            
        Returns:
            Lista de mensajes recientes
        """
        try:
            # Calcular timestamp de hace X minutos
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            # Obtener mensajes recientes
            result = self.client.table("conversation_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .gte("created_at", cutoff_time.isoformat())\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            messages = []
            if result.data:
                for msg_dict in result.data:
                    message = ConversationMessage(
                        id=msg_dict["id"],
                        session_id=msg_dict["session_id"],
                        message_type=ConversationMessageType(msg_dict["message_type"]),
                        content=msg_dict["content"],
                        metadata=msg_dict.get("metadata"),
                        agent_name=msg_dict.get("agent_name"),
                        token_count=msg_dict.get("token_count"),
                        created_at=datetime.fromisoformat(msg_dict["created_at"].replace('Z', '+00:00'))
                    )
                    messages.append(message)
            
            logger.info(f"✅ Mensajes recientes obtenidos: {len(messages)}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo mensajes recientes: {str(e)}")
            return []
    
    async def deactivate_old_sessions(self, user_id: str, days: int = 7) -> int:
        """
        Desactivar sesiones antiguas del usuario
        
        Args:
            user_id: ID del usuario
            days: Días de inactividad para considerar una sesión como antigua
            
        Returns:
            Número de sesiones desactivadas
        """
        try:
            # Calcular timestamp de hace X días
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # Desactivar sesiones antiguas
            result = self.client.table("conversation_sessions")\
                .update({"is_active": False})\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .lt("last_activity_at", cutoff_time.isoformat())\
                .execute()
            
            count = len(result.data) if result.data else 0
            logger.info(f"✅ Sesiones desactivadas: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error desactivando sesiones: {str(e)}")
            return 0
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[ConversationSession]:
        """
        Obtener todas las sesiones de un usuario
        
        Args:
            user_id: ID del usuario
            active_only: Si solo obtener sesiones activas
            
        Returns:
            Lista de sesiones del usuario
        """
        try:
            query = self.client.table("conversation_sessions")\
                .select("*")\
                .eq("user_id", user_id)
            
            if active_only:
                query = query.eq("is_active", True)
            
            result = query.order("last_activity_at", desc=True).execute()
            
            sessions = []
            if result.data:
                for session_dict in result.data:
                    session = ConversationSession(
                        id=session_dict["id"],
                        user_id=session_dict["user_id"],
                        session_name=session_dict.get("session_name"),
                        started_at=datetime.fromisoformat(session_dict["started_at"].replace('Z', '+00:00')),
                        last_activity_at=datetime.fromisoformat(session_dict["last_activity_at"].replace('Z', '+00:00')),
                        is_active=session_dict["is_active"],
                        metadata=session_dict.get("metadata"),
                        created_at=datetime.fromisoformat(session_dict["created_at"].replace('Z', '+00:00')),
                        updated_at=datetime.fromisoformat(session_dict["updated_at"].replace('Z', '+00:00'))
                    )
                    sessions.append(session)
            
            logger.info(f"✅ Sesiones obtenidas: {len(sessions)}")
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo sesiones: {str(e)}")
            return []

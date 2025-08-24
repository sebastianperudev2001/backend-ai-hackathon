"""
Cliente de Supabase para operaciones de base de datos
"""
import logging
from typing import Optional
from supabase import create_client, Client
from config.settings import get_settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Cliente singleton para Supabase
    """
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente de Supabase"""
        try:
            settings = get_settings()
            
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.warning("⚠️ Credenciales de Supabase no configuradas")
                return
            
            # Inicializar cliente con parámetros básicos
            self._client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
            
            logger.info("✅ Cliente de Supabase inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente de Supabase: {str(e)}")
            logger.error(f"   URL: {settings.SUPABASE_URL[:20] if settings.SUPABASE_URL else 'No configurada'}...")
            logger.error(f"   Key: {'Configurada' if settings.SUPABASE_KEY else 'No configurada'}")
            self._client = None
    
    @property
    def client(self) -> Optional[Client]:
        """Obtener cliente de Supabase"""
        return self._client
    
    def is_connected(self) -> bool:
        """Verificar si el cliente está conectado"""
        return self._client is not None
    
    def set_user_context(self, user_id: str):
        """
        Establecer contexto de usuario para RLS (Row Level Security)
        """
        if not self._client:
            logger.warning("⚠️ Cliente de Supabase no inicializado, no se puede establecer contexto")
            return False
            
        try:
            # Establecer el user_id en el contexto de la sesión
            result = self._client.rpc('set_config', {
                'setting_name': 'app.current_user_id',
                'new_value': user_id,
                'is_local': True
            }).execute()
            
            logger.debug(f"🔐 Contexto de usuario establecido: {user_id}")
            return True
            
        except Exception as e:
            # Log detallado del error para debugging
            error_msg = str(e)
            if "Could not find the function" in error_msg and "set_config" in error_msg:
                logger.warning(f"⚠️ Función set_config no encontrada en la base de datos.")
                logger.warning(f"   Ejecuta el esquema actualizado en Supabase SQL Editor.")
                logger.warning(f"   Las políticas RLS pueden no funcionar correctamente sin contexto de usuario.")
            else:
                logger.warning(f"⚠️ Error estableciendo contexto de usuario: {error_msg}")
            
            return False


def get_supabase_client() -> SupabaseClient:
    """
    Obtener instancia del cliente de Supabase
    """
    return SupabaseClient()

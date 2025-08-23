"""
Configuración centralizada de la aplicación
Todas las variables de entorno y configuraciones se manejan aquí
"""
import os
from functools import lru_cache


class Settings:
    """Configuración de la aplicación"""
    
    # WhatsApp Business API
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "your_whatsapp_token")
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "your_phone_id")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "fitness_bot_verify_123")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v18.0")
    
    # URLs
    @property
    def WHATSAPP_API_URL(self) -> str:
        return f"https://graph.facebook.com/{self.WHATSAPP_API_VERSION}/{self.WHATSAPP_PHONE_ID}/messages"
    
    # Aplicación
    APP_NAME: str = "WhatsApp Fitness Bot"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Timeouts
    HTTP_TIMEOUT: float = 10.0
    
    # Feature flags (para el hackathon, fácil activar/desactivar features)
    ENABLE_IMAGE_PROCESSING: bool = os.getenv("ENABLE_IMAGE_PROCESSING", "false").lower() == "true"
    ENABLE_AI_RESPONSES: bool = os.getenv("ENABLE_AI_RESPONSES", "false").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    """Obtener instancia singleton de configuración"""
    return Settings()

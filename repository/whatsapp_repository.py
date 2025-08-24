"""
Repository Layer - Maneja todas las interacciones con APIs externas
En este caso, la API de WhatsApp Business
"""
import httpx
import logging
from typing import Optional, Dict, Any
from config.settings import get_settings

logger = logging.getLogger(__name__)


class WhatsAppRepository:
    """
    Repositorio para interactuar con la API de WhatsApp
    Toda la comunicación externa con WhatsApp pasa por aquí
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.WHATSAPP_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Enviar mensaje de texto a través de WhatsApp API
        
        Args:
            to: Número de teléfono del destinatario
            message: Texto del mensaje
            
        Returns:
            Dict con la respuesta de la API
            
        Raises:
            Exception: Si hay un error en la comunicación con la API
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            # Log del payload para debugging
            logger.info(f"📤 Enviando mensaje a {to}: {len(message)} caracteres")
            logger.debug(f"📋 Payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.settings.HTTP_TIMEOUT
                )
                
                # Intentar parsear respuesta
                try:
                    response_data = response.json()
                except Exception as json_error:
                    logger.error(f"❌ Error parseando respuesta JSON: {json_error}")
                    logger.error(f"📄 Respuesta cruda: {response.text}")
                    return {
                        "success": False,
                        "error": f"Error parseando respuesta: {response.text[:200]}",
                        "status_code": response.status_code
                    }
                
                if response.status_code == 200:
                    logger.info(f"✅ Mensaje enviado exitosamente a {to}")
                    return {
                        "success": True,
                        "message_id": response_data.get("messages", [{}])[0].get("id"),
                        "data": response_data
                    }
                else:
                    # Log detallado del error
                    error_details = response_data.get("error", {})
                    error_message = error_details.get("message", "Error desconocido")
                    error_code = error_details.get("code", "unknown")
                    
                    logger.error(f"❌ Error de API WhatsApp:")
                    logger.error(f"   Status: {response.status_code}")
                    logger.error(f"   Code: {error_code}")
                    logger.error(f"   Message: {error_message}")
                    logger.error(f"   Full response: {response_data}")
                    
                    return {
                        "success": False,
                        "error": f"WhatsApp API Error ({error_code}): {error_message}",
                        "status_code": response.status_code,
                        "data": response_data
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout enviando mensaje a {to}")
            raise Exception("Timeout al enviar mensaje")
            
        except httpx.RequestError as e:
            logger.error(f"❌ Error de red: {str(e)}")
            raise Exception(f"Error de red: {str(e)}")
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {str(e)}")
            raise
    
    async def send_template_message(self, to: str, template_name: str, parameters: list = None) -> Dict[str, Any]:
        """
        Enviar mensaje de plantilla (para futura implementación)
        
        Args:
            to: Número de destino
            template_name: Nombre de la plantilla
            parameters: Parámetros de la plantilla
        """
        # TODO: Implementar cuando se necesiten plantillas
        raise NotImplementedError("Templates aún no implementados")
    
    async def send_media_message(self, to: str, media_type: str, media_url: str, caption: str = None) -> Dict[str, Any]:
        """
        Enviar mensaje con media (imagen, video, documento)
        
        Args:
            to: Número de destino
            media_type: Tipo de media (image, video, document)
            media_url: URL del archivo media
            caption: Texto opcional
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }
        
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.settings.HTTP_TIMEOUT
                )
                
                return self._process_response(response, f"media {media_type}", to)
                
        except Exception as e:
            logger.error(f"❌ Error enviando media: {str(e)}")
            raise
    
    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marcar mensaje como leído
        
        Args:
            message_id: ID del mensaje a marcar como leído
        """
        # TODO: Implementar cuando se necesite
        pass
    
    def _process_response(self, response: httpx.Response, action: str, to: str) -> Dict[str, Any]:
        """
        Procesar respuesta de la API de WhatsApp
        
        Args:
            response: Respuesta HTTP
            action: Acción realizada (para logging)
            to: Destinatario (para logging)
        """
        try:
            response_data = response.json()
        except:
            response_data = {"error": "No se pudo parsear la respuesta"}
            
        if response.status_code == 200:
            logger.info(f"✅ {action} enviado exitosamente a {to}")
            return {
                "success": True,
                "data": response_data
            }
        else:
            logger.error(f"❌ Error en {action}: {response.status_code}")
            return {
                "success": False,
                "error": response_data,
                "status_code": response.status_code
            }


# Singleton para reutilizar en toda la aplicación
_whatsapp_repo_instance = None

def get_whatsapp_repository() -> WhatsAppRepository:
    """Obtener instancia singleton del repositorio"""
    global _whatsapp_repo_instance
    if _whatsapp_repo_instance is None:
        _whatsapp_repo_instance = WhatsAppRepository()
    return _whatsapp_repo_instance

"""
Controller Layer - Maneja y valida los requests entrantes
Procesa los datos de entrada y los prepara para el servicio
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from domain.models import (
    ApiResponse, 
    MessageResponse, 
    HealthCheckResponse,
    WebhookData
)
from service.whatsapp_service import get_whatsapp_service
from config.settings import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookController:
    """
    Controlador para manejar las peticiones del webhook
    Valida y prepara los datos antes de pasarlos al servicio
    """
    
    def __init__(self):
        self.whatsapp_service = get_whatsapp_service()
        self.settings = get_settings()
        
    async def verify_webhook(self, 
                           mode: Optional[str], 
                           token: Optional[str], 
                           challenge: Optional[str]) -> int:
        """
        Verificar el webhook de WhatsApp (GET request)
        
        Args:
            mode: hub.mode parameter
            token: hub.verify_token parameter  
            challenge: hub.challenge parameter
            
        Returns:
            Challenge as integer if verification succeeds
            
        Raises:
            HTTPException: Si la verificación falla
        """
        logger.info(f"🔍 Verificando webhook: mode={mode}, token={token}")
        
        # Validar parámetros requeridos
        if not all([mode, token, challenge]):
            logger.error("❌ Faltan parámetros de verificación")
            raise HTTPException(
                status_code=400, 
                detail="Parámetros de verificación incompletos"
            )
        
        # Verificar token y modo
        if mode == "subscribe" and token == self.settings.VERIFY_TOKEN:
            logger.info("✅ Webhook verificado correctamente")
            try:
                return int(challenge)
            except ValueError:
                logger.error("❌ Challenge no es un número válido")
                raise HTTPException(
                    status_code=400,
                    detail="Challenge inválido"
                )
        else:
            logger.error(f"❌ Verificación fallida: mode={mode}, token válido={token == self.settings.VERIFY_TOKEN}")
            raise HTTPException(
                status_code=403, 
                detail="Token de verificación inválido"
            )
    
    async def handle_webhook_event(self, request_body: Dict[str, Any]) -> ApiResponse:
        """
        Manejar evento del webhook (POST request)
        
        Args:
            request_body: Body del request en formato JSON
            
        Returns:
            ApiResponse indicando el resultado
        """
        try:
            # Log del evento recibido
            logger.info(f"📨 Webhook recibido: {request_body.get('object', 'unknown')}")
            
            # Validar estructura básica
            if not request_body:
                raise HTTPException(
                    status_code=400,
                    detail="Request body vacío"
                )
            
            # Procesar el webhook
            success = await self.whatsapp_service.process_webhook_data(request_body)
            
            if success:
                return ApiResponse(
                    status="success",
                    message="Webhook procesado correctamente"
                )
            else:
                return ApiResponse(
                    status="warning",
                    message="Webhook procesado con advertencias"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error procesando webhook: {str(e)}")
            # No lanzamos 500 para que WhatsApp no reintente
            return ApiResponse(
                status="error",
                message="Error interno procesando webhook",
                data={"error": str(e)}
            )
    
    async def send_test_message(self, 
                               phone_number: str, 
                               message: Optional[str] = None) -> ApiResponse:
        """
        Enviar mensaje de prueba
        
        Args:
            phone_number: Número de teléfono destino
            message: Mensaje opcional a enviar
            
        Returns:
            ApiResponse con el resultado
            
        Raises:
            HTTPException: Si hay error en el envío
        """
        # Validar número de teléfono
        if not phone_number:
            raise HTTPException(
                status_code=400,
                detail="Número de teléfono requerido"
            )
        
        # Validación básica del formato del número
        if not self._validate_phone_number(phone_number):
            raise HTTPException(
                status_code=400,
                detail="Formato de número inválido. Use formato internacional: +521234567890"
            )
        
        try:
            # Enviar mensaje a través del servicio
            result = await self.whatsapp_service.send_test_message(phone_number, message)
            
            if result.success:
                return ApiResponse(
                    status="success",
                    message="Mensaje enviado correctamente",
                    data={
                        "message_id": result.message_id,
                        "to": phone_number,
                        "text": result.response_text
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error enviando mensaje: {result.error}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de prueba: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error interno: {str(e)}"
            )
    
    def get_health_status(self) -> HealthCheckResponse:
        """
        Obtener estado de salud de la aplicación
        
        Returns:
            HealthCheckResponse con el estado actual
        """
        return HealthCheckResponse(
            status="healthy",
            service=self.settings.APP_NAME,
            timestamp=datetime.now(),
            environment=self.settings.APP_ENV
        )
    
    def get_root_info(self) -> ApiResponse:
        """
        Obtener información básica de la API
        
        Returns:
            ApiResponse con información del servicio
        """
        return ApiResponse(
            status="running",
            message=f"🏋️ {self.settings.APP_NAME} API",
            data={
                "version": self.settings.APP_VERSION,
                "environment": self.settings.APP_ENV,
                "features": {
                    "image_processing": self.settings.ENABLE_IMAGE_PROCESSING,
                    "ai_responses": self.settings.ENABLE_AI_RESPONSES
                }
            }
        )
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Validar formato básico del número de teléfono
        
        Args:
            phone_number: Número a validar
            
        Returns:
            True si el formato es válido
        """
        # Eliminar espacios y guiones
        cleaned = phone_number.replace(" ", "").replace("-", "")
        
        # Debe empezar con + o ser solo números
        if cleaned.startswith("+"):
            return cleaned[1:].isdigit() and len(cleaned) >= 10
        else:
            return cleaned.isdigit() and len(cleaned) >= 10


# Singleton del controlador
_webhook_controller_instance = None

def get_webhook_controller() -> WebhookController:
    """Obtener instancia singleton del controlador"""
    global _webhook_controller_instance
    if _webhook_controller_instance is None:
        _webhook_controller_instance = WebhookController()
    return _webhook_controller_instance

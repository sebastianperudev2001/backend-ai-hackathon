"""
Service Layer - Lógica de negocio del bot
Aquí procesamos los mensajes y decidimos qué responder
"""
import logging
from typing import Dict, Any, Optional
from domain.models import (
    MessageType, 
    WhatsAppIncomingMessage, 
    MessageResponse
)
from repository.whatsapp_repository import get_whatsapp_repository
from config.settings import get_settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Servicio principal para procesar mensajes de WhatsApp
    Contiene toda la lógica de negocio del bot
    """
    
    def __init__(self):
        self.whatsapp_repo = get_whatsapp_repository()
        self.settings = get_settings()
        
    async def process_webhook_data(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Procesar datos completos del webhook
        
        Args:
            webhook_data: Datos crudos del webhook
            
        Returns:
            True si se procesó correctamente
        """
        try:
            # Verificar estructura del webhook
            if "entry" not in webhook_data:
                logger.warning("⚠️ Webhook sin 'entry'")
                return False
                
            for entry in webhook_data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            await self._process_message_change(change["value"])
                            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando webhook: {str(e)}")
            return False
    
    async def _process_message_change(self, message_data: Dict[str, Any]) -> None:
        """
        Procesar cambios de mensajes del webhook
        
        Args:
            message_data: Datos del cambio de mensaje
        """
        if "messages" not in message_data:
            return
            
        messages = message_data.get("messages", [])
        
        for message in messages:
            try:
                # Crear modelo de mensaje entrante
                incoming_msg = WhatsAppIncomingMessage(
                    from_number=message["from"],
                    id=message["id"],
                    type=MessageType(message["type"]),
                    timestamp=message.get("timestamp")
                )
                
                # Procesar según el tipo de mensaje
                await self._handle_message_by_type(incoming_msg, message)
                
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje individual: {str(e)}")
    
    async def _handle_message_by_type(self, incoming_msg: WhatsAppIncomingMessage, raw_message: Dict) -> MessageResponse:
        """
        Manejar mensaje según su tipo
        
        Args:
            incoming_msg: Mensaje modelado
            raw_message: Datos crudos del mensaje
            
        Returns:
            MessageResponse con el resultado
        """
        sender = incoming_msg.from_number
        message_type = incoming_msg.type
        
        logger.info(f"📨 Procesando mensaje {message_type} de {sender}")
        
        # Procesamiento según tipo
        if message_type == MessageType.TEXT:
            text = raw_message["text"]["body"]
            return await self._handle_text_message(sender, text)
            
        elif message_type == MessageType.IMAGE:
            return await self._handle_image_message(sender, raw_message.get("image", {}))
            
        elif message_type == MessageType.LOCATION:
            return await self._handle_location_message(sender, raw_message.get("location", {}))
            
        else:
            # Mensaje genérico para tipos no soportados
            return await self._send_unsupported_type_message(sender, message_type)
    
    async def _handle_text_message(self, sender: str, text: str) -> MessageResponse:
        """
        Procesar mensaje de texto y generar respuesta
        
        Args:
            sender: Número del remitente
            text: Texto del mensaje
            
        Returns:
            MessageResponse con el resultado
        """
        logger.info(f"📝 Texto de {sender}: {text}")
        
        # Lógica de negocio: Analizar el texto y responder
        response_text = await self._generate_text_response(text)
        
        # Enviar respuesta
        result = await self.whatsapp_repo.send_text_message(sender, response_text)
        
        return MessageResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            response_text=response_text,
            error=result.get("error")
        )
    
    async def _generate_text_response(self, text: str) -> str:
        """
        Generar respuesta basada en el texto recibido
        AQUÍ ES DONDE AGREGARÁS TU LÓGICA DE IA/FITNESS
        
        Args:
            text: Texto del usuario
            
        Returns:
            Texto de respuesta
        """
        text_lower = text.lower()
        
        # Comandos básicos del bot
        if text_lower in ["hola", "hello", "hi", "hey"]:
            return (
                "¡Hola! 👋 Soy tu Fitness Bot personal 💪\n\n"
                "¿En qué puedo ayudarte hoy?\n"
                "• 🏋️ Rutinas de ejercicio\n"
                "• 🥗 Consejos de nutrición\n"
                "• 📊 Seguimiento de progreso\n"
                "• 💡 Motivación diaria\n\n"
                "Escribe 'ayuda' para ver todos los comandos disponibles."
            )
            
        elif text_lower in ["ayuda", "help", "comandos"]:
            return (
                "📚 **COMANDOS DISPONIBLES**\n\n"
                "🏋️ *Ejercicio:*\n"
                "• 'rutina' - Obtener rutina del día\n"
                "• 'ejercicio [músculo]' - Ejercicios específicos\n\n"
                "🥗 *Nutrición:*\n"
                "• 'dieta' - Plan alimenticio\n"
                "• 'calorias [comida]' - Info nutricional\n\n"
                "📊 *Progreso:*\n"
                "• 'peso [kg]' - Registrar peso\n"
                "• 'progreso' - Ver tu evolución\n\n"
                "💪 Envía una foto de tu comida y la analizaré!"
            )
            
        elif "rutina" in text_lower:
            return (
                "🏋️ **RUTINA DE HOY**\n\n"
                "🔥 Calentamiento (5 min):\n"
                "• Jumping jacks - 1 min\n"
                "• Estiramientos dinámicos\n\n"
                "💪 Ejercicios principales:\n"
                "• Sentadillas - 3x15\n"
                "• Flexiones - 3x12\n"
                "• Plancha - 3x30 seg\n"
                "• Burpees - 3x10\n\n"
                "🧘 Enfriamiento (5 min):\n"
                "• Estiramientos estáticos\n\n"
                "¡Tú puedes! 💪"
            )
            
        elif "peso" in text_lower:
            # TODO: Aquí conectarías con una base de datos para guardar el progreso
            return "✅ Peso registrado correctamente. ¡Sigue así! 📈"
            
        else:
            # Respuesta por defecto con el echo del mensaje
            return (
                f"🤖 Recibí tu mensaje: '{text}'\n\n"
                "💡 Tip del día: Mantente hidratado bebiendo al menos 2L de agua.\n\n"
                "Escribe 'ayuda' para ver qué puedo hacer por ti."
            )
    
    async def _handle_image_message(self, sender: str, image_data: Dict) -> MessageResponse:
        """
        Procesar mensaje de imagen
        
        Args:
            sender: Número del remitente
            image_data: Datos de la imagen
            
        Returns:
            MessageResponse con el resultado
        """
        logger.info(f"🖼️ Imagen recibida de {sender}")
        
        response_text = (
            "📸 ¡Imagen recibida!\n\n"
            "🔍 Analizando tu comida...\n\n"
            "🥗 Parece una comida saludable!\n"
            "Estimación: ~450 calorías\n\n"
            "💡 Consejo: Agrega más proteína para mejor recuperación muscular."
        )
        
        if not self.settings.ENABLE_IMAGE_PROCESSING:
            response_text = (
                "📸 ¡Imagen recibida!\n\n"
                "⚠️ El análisis de imágenes estará disponible pronto.\n"
                "Por ahora, puedes describirme tu comida y te daré información nutricional."
            )
        
        result = await self.whatsapp_repo.send_text_message(sender, response_text)
        
        return MessageResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            response_text=response_text
        )
    
    async def _handle_location_message(self, sender: str, location_data: Dict) -> MessageResponse:
        """
        Procesar mensaje de ubicación
        
        Args:
            sender: Número del remitente
            location_data: Datos de ubicación
            
        Returns:
            MessageResponse con el resultado
        """
        logger.info(f"📍 Ubicación recibida de {sender}")
        
        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        
        response_text = (
            f"📍 Ubicación recibida!\n"
            f"Coordenadas: {lat}, {lon}\n\n"
            "🏃 Pronto podré sugerirte rutas de running y gimnasios cercanos."
        )
        
        result = await self.whatsapp_repo.send_text_message(sender, response_text)
        
        return MessageResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            response_text=response_text
        )
    
    async def _send_unsupported_type_message(self, sender: str, message_type: str) -> MessageResponse:
        """
        Enviar mensaje para tipos no soportados
        
        Args:
            sender: Número del remitente
            message_type: Tipo de mensaje recibido
            
        Returns:
            MessageResponse con el resultado
        """
        response_text = (
            f"📱 Recibí tu mensaje tipo '{message_type}'.\n\n"
            "Por ahora puedo procesar:\n"
            "• 💬 Mensajes de texto\n"
            "• 📸 Imágenes\n"
            "• 📍 Ubicaciones\n\n"
            "¡Pronto agregaré más funciones!"
        )
        
        result = await self.whatsapp_repo.send_text_message(sender, response_text)
        
        return MessageResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            response_text=response_text
        )
    
    async def send_test_message(self, phone_number: str, message: str = None) -> MessageResponse:
        """
        Enviar mensaje de prueba
        
        Args:
            phone_number: Número de destino
            message: Mensaje opcional
            
        Returns:
            MessageResponse con el resultado
        """
        if not message:
            message = (
                "🧪 **MENSAJE DE PRUEBA**\n\n"
                "✅ El Fitness Bot está funcionando correctamente!\n"
                f"📱 Versión: {self.settings.APP_VERSION}\n"
                f"🌍 Ambiente: {self.settings.APP_ENV}\n\n"
                "¡Listo para ayudarte con tu fitness! 💪"
            )
        
        result = await self.whatsapp_repo.send_text_message(phone_number, message)
        
        return MessageResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            response_text=message,
            error=result.get("error")
        )


# Singleton del servicio
_whatsapp_service_instance = None

def get_whatsapp_service() -> WhatsAppService:
    """Obtener instancia singleton del servicio"""
    global _whatsapp_service_instance
    if _whatsapp_service_instance is None:
        _whatsapp_service_instance = WhatsAppService()
    return _whatsapp_service_instance

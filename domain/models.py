"""
Modelos de dominio para el Fitness Bot de WhatsApp
Contiene todas las estructuras de datos utilizadas en la aplicación
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class MessageType(str, Enum):
    """Tipos de mensajes soportados por WhatsApp"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    REACTION = "reaction"
    STICKER = "sticker"


class WhatsAppTextMessage(BaseModel):
    """Estructura para mensajes de texto de WhatsApp"""
    body: str


class WhatsAppOutgoingMessage(BaseModel):
    """Mensaje saliente para enviar por WhatsApp"""
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: Dict[str, str]


class WhatsAppIncomingMessage(BaseModel):
    """Mensaje entrante de WhatsApp"""
    from_number: str = Field(alias="from")
    id: str
    type: MessageType
    timestamp: Optional[str] = None
    text: Optional[WhatsAppTextMessage] = None
    
    class Config:
        populate_by_name = True  # Actualizado para Pydantic v2


class WebhookEntry(BaseModel):
    """Estructura de entrada del webhook"""
    id: str
    changes: List[Dict[str, Any]]


class WebhookData(BaseModel):
    """Datos completos del webhook"""
    object: str
    entry: List[WebhookEntry]


class MessageResponse(BaseModel):
    """Respuesta después de procesar un mensaje"""
    success: bool
    message_id: Optional[str] = None
    response_text: Optional[str] = None
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Respuesta del health check"""
    status: str
    service: str
    timestamp: datetime
    environment: Optional[str] = None


class ApiResponse(BaseModel):
    """Respuesta genérica de la API"""
    status: str
    message: str
    data: Optional[Any] = None

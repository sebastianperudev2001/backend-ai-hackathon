"""Módulo de dominio - Modelos y estructuras de datos"""
from .models import (
    MessageType,
    WhatsAppTextMessage,
    WhatsAppOutgoingMessage,
    WhatsAppIncomingMessage,
    WebhookEntry,
    WebhookData,
    MessageResponse,
    HealthCheckResponse,
    ApiResponse
)

__all__ = [
    "MessageType",
    "WhatsAppTextMessage",
    "WhatsAppOutgoingMessage",
    "WhatsAppIncomingMessage",
    "WebhookEntry",
    "WebhookData",
    "MessageResponse",
    "HealthCheckResponse",
    "ApiResponse"
]

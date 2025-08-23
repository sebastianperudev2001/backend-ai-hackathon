"""
Handler Layer - Define los endpoints de la API
Solo maneja el routing y delega al controller
"""
from fastapi import APIRouter, Request, Query, HTTPException
from typing import Optional
from domain.models import ApiResponse, HealthCheckResponse
from controller.webhook_controller import get_webhook_controller
import logging

logger = logging.getLogger(__name__)

# Crear router de FastAPI
router = APIRouter(
    prefix="",
    tags=["webhook"],
    responses={404: {"description": "Not found"}},
)

# Obtener instancia del controlador
webhook_controller = get_webhook_controller()


@router.get("/", response_model=ApiResponse)
async def root():
    """
    Endpoint raíz - Información básica de la API
    
    Returns:
        ApiResponse con información del servicio
    """
    return webhook_controller.get_root_info()


@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    """
    Verificar webhook de WhatsApp (requerido por Meta)
    
    Este endpoint es llamado por WhatsApp para verificar que el webhook
    es válido y está configurado correctamente.
    
    Args:
        hub_mode: Modo de verificación (debe ser "subscribe")
        hub_verify_token: Token de verificación configurado
        hub_challenge: Challenge a devolver si la verificación es exitosa
        
    Returns:
        Challenge como entero si la verificación es exitosa
        
    Raises:
        HTTPException: Si la verificación falla
    """
    logger.info(f"🔍 GET /webhook - Verificación solicitada")
    return await webhook_controller.verify_webhook(
        mode=hub_mode,
        token=hub_verify_token,
        challenge=hub_challenge
    )


@router.post("/webhook", response_model=ApiResponse)
async def handle_webhook(request: Request):
    """
    Manejar eventos del webhook de WhatsApp
    
    Este endpoint recibe todos los eventos de WhatsApp:
    - Mensajes entrantes
    - Estados de mensajes enviados
    - Otros eventos del sistema
    
    Args:
        request: Request con el body del webhook
        
    Returns:
        ApiResponse indicando el resultado del procesamiento
    """
    try:
        # Obtener el body del request
        body = await request.json()
        logger.info(f"📨 POST /webhook - Evento recibido")
        
        # Delegar al controlador
        return await webhook_controller.handle_webhook_event(body)
        
    except Exception as e:
        logger.error(f"❌ Error en handler: {str(e)}")
        # Retornar success para evitar reintentos de WhatsApp
        return ApiResponse(
            status="error",
            message="Error procesando webhook",
            data={"error": str(e)}
        )


@router.post("/send-test-message", response_model=ApiResponse)
async def send_test_message(
    phone_number: str,
    message: Optional[str] = None
):
    """
    Enviar mensaje de prueba a un número de WhatsApp
    
    Útil para verificar que la integración está funcionando correctamente.
    
    Args:
        phone_number: Número de teléfono en formato internacional (+521234567890)
        message: Mensaje opcional a enviar (si no se provee, se envía uno por defecto)
        
    Returns:
        ApiResponse con el resultado del envío
        
    Raises:
        HTTPException: Si hay error en el envío
    """
    logger.info(f"📤 POST /send-test-message - Enviando a {phone_number}")
    return await webhook_controller.send_test_message(phone_number, message)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    
    Verifica que el servicio está funcionando correctamente.
    Útil para monitoreo y balanceadores de carga.
    
    Returns:
        HealthCheckResponse con el estado del servicio
    """
    return webhook_controller.get_health_status()


# Handlers adicionales que podrías necesitar en el hackathon

@router.post("/send-menu", response_model=ApiResponse)
async def send_menu(phone_number: str):
    """
    Enviar menú principal del bot a un usuario
    
    Args:
        phone_number: Número de teléfono destino
        
    Returns:
        ApiResponse con el resultado
    """
    menu_message = (
        "📱 **MENÚ PRINCIPAL**\n\n"
        "Selecciona una opción:\n\n"
        "1️⃣ Ver rutina de hoy\n"
        "2️⃣ Registrar peso\n"
        "3️⃣ Analizar comida (envía foto)\n"
        "4️⃣ Ver progreso\n"
        "5️⃣ Consejos de nutrición\n"
        "6️⃣ Motivación del día\n\n"
        "Responde con el número de la opción que deseas."
    )
    
    return await webhook_controller.send_test_message(phone_number, menu_message)


@router.post("/broadcast", response_model=ApiResponse)
async def broadcast_message(
    message: str,
    phone_numbers: list[str]
):
    """
    Enviar mensaje masivo a múltiples usuarios (útil para notificaciones)
    
    Args:
        message: Mensaje a enviar
        phone_numbers: Lista de números destino
        
    Returns:
        ApiResponse con el resumen del envío
    """
    results = []
    for phone in phone_numbers:
        try:
            await webhook_controller.send_test_message(phone, message)
            results.append({"phone": phone, "status": "sent"})
        except Exception as e:
            results.append({"phone": phone, "status": "failed", "error": str(e)})
    
    successful = len([r for r in results if r["status"] == "sent"])
    failed = len(results) - successful
    
    return ApiResponse(
        status="completed",
        message=f"Broadcast completado: {successful} enviados, {failed} fallidos",
        data={"results": results}
    )

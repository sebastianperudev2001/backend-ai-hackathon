"""
WhatsApp Fitness Bot - Punto de entrada principal
Arquitectura por capas para hackathon
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

# Importar configuración y handlers
from config.settings import get_settings
from handler.webhook_handler import router as webhook_router

# Configurar logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # Opcional: agregar archivo de logs
        # logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    logger.info("="*50)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🌍 Ambiente: {settings.APP_ENV}")
    logger.info(f"📱 WhatsApp Phone ID: {settings.WHATSAPP_PHONE_ID}")
    logger.info(f"🔧 Features habilitadas:")
    logger.info(f"   - Procesamiento de imágenes: {settings.ENABLE_IMAGE_PROCESSING}")
    logger.info(f"   - Respuestas con IA: {settings.ENABLE_AI_RESPONSES}")
    logger.info("="*50)
    logger.info("✅ Aplicación iniciada correctamente")
    logger.info(f"📚 Documentación disponible en: http://localhost:{settings.PORT}/docs")
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="🏋️ Bot de WhatsApp para fitness y nutrición - Hackathon Edition",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan  # Usar lifespan en lugar de on_event
)

# Configurar CORS (importante para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(webhook_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # String import para Railway
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.APP_ENV == "development"  # Auto-reload en desarrollo
    )
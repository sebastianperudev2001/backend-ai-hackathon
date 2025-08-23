"""
Agente especializado en análisis de imágenes con Claude Vision
"""
import logging
import base64
import httpx
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class ImageAnalysisAgent(BaseAgent):
    """
    Agente experto en análisis de imágenes de comida y ejercicio
    """
    
    def __init__(self):
        system_prompt = """
        Eres un experto en análisis visual de imágenes relacionadas con fitness y nutrición.
        Tu objetivo es analizar imágenes y proporcionar:
        
        Para imágenes de COMIDA:
        1. Identificación de alimentos y platos
        2. Estimación de porciones
        3. Cálculo aproximado de calorías y macronutrientes
        4. Evaluación de la calidad nutricional
        5. Sugerencias de mejora
        
        Para imágenes de EJERCICIO/POSTURA:
        1. Identificación del ejercicio o postura
        2. Análisis de la técnica y forma
        3. Puntos de mejora en la ejecución
        4. Riesgos potenciales de lesión
        5. Ejercicios correctivos si es necesario
        
        Para imágenes de PROGRESO FÍSICO:
        1. Observaciones respetuosas sobre cambios visibles
        2. Motivación y reconocimiento del esfuerzo
        3. Sugerencias para continuar el progreso
        
        Características de tus respuestas:
        - Sé preciso pero comprensivo con las estimaciones
        - Mantén un tono positivo y motivador
        - Usa emojis relevantes (📸🔍💪🥗)
        - Si no puedes identificar algo con certeza, indícalo
        - Prioriza la salud y seguridad en tus recomendaciones
        
        Responde siempre en español y de forma clara y estructurada.
        """
        
        super().__init__(name="ImageAnalysisAgent", system_prompt=system_prompt)
        
        # Configurar modelo con capacidad de visión
        self.vision_llm = ChatAnthropic(
            api_key=self.settings.ANTHROPIC_API_KEY,
            model=self.settings.CLAUDE_MODEL,
            temperature=0,
            max_tokens=1024,
        )
    
    async def analyze_image(self, image_data: bytes, image_type: str = "auto") -> str:
        """
        Analizar una imagen y proporcionar información relevante
        
        Args:
            image_data: Datos de la imagen en bytes
            image_type: Tipo de imagen (food, exercise, progress, auto)
            
        Returns:
            Análisis detallado de la imagen
        """
        try:
            # Codificar imagen en base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Determinar el prompt según el tipo
            analysis_prompt = self._get_analysis_prompt(image_type)
            
            # Crear mensaje con imagen
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                )
            ]
            
            # Analizar con Claude Vision
            response = await self.vision_llm.ainvoke(messages)
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Error analizando imagen: {str(e)}")
            return f"No pude analizar la imagen correctamente. Error: {str(e)}"
    
    async def analyze_food_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Análisis especializado para imágenes de comida
        
        Args:
            image_data: Datos de la imagen
            
        Returns:
            Diccionario con análisis nutricional detallado
        """
        prompt = """
        Analiza esta imagen de comida y proporciona:
        
        1. **Identificación de alimentos** 🍽️
           - Lista todos los alimentos visibles
           - Estima las porciones (en gramos o unidades)
        
        2. **Información nutricional** 📊
           - Calorías totales estimadas
           - Proteínas (g)
           - Carbohidratos (g)
           - Grasas (g)
           - Fibra estimada (g)
        
        3. **Evaluación de calidad** ⭐
           - Puntuación del 1-10 en valor nutricional
           - Puntos positivos del plato
           - Áreas de mejora
        
        4. **Recomendaciones** 💡
           - Sugerencias para mejorar el balance nutricional
           - Alternativas más saludables si aplica
        
        Formatea la respuesta de manera clara y estructurada.
        """
        
        result = await self.analyze_image(image_data, "food")
        
        return {
            "type": "food_analysis",
            "analysis": result,
            "timestamp": self._get_timestamp()
        }
    
    async def analyze_exercise_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Análisis especializado para imágenes de ejercicio
        
        Args:
            image_data: Datos de la imagen
            
        Returns:
            Diccionario con análisis de técnica
        """
        prompt = """
        Analiza esta imagen de ejercicio/postura y proporciona:
        
        1. **Identificación del ejercicio** 🏋️
           - Nombre del ejercicio o postura
           - Músculos principales trabajados
        
        2. **Análisis de técnica** 🎯
           - Puntos correctos en la ejecución
           - Errores o áreas de mejora identificadas
           - Calificación de la técnica (1-10)
        
        3. **Correcciones sugeridas** ✅
           - Ajustes específicos de postura
           - Tips para mejorar la ejecución
           - Señales (cues) útiles
        
        4. **Prevención de lesiones** ⚠️
           - Riesgos identificados
           - Ejercicios preparatorios recomendados
           - Progresiones o regresiones sugeridas
        
        Sé específico y constructivo en tu feedback.
        """
        
        result = await self.analyze_image(image_data, "exercise")
        
        return {
            "type": "exercise_analysis",
            "analysis": result,
            "timestamp": self._get_timestamp()
        }
    
    async def analyze_progress_image(self, image_data: bytes, context: Optional[Dict] = None) -> str:
        """
        Análisis de imágenes de progreso físico
        
        Args:
            image_data: Datos de la imagen
            context: Contexto adicional (tiempo entrenando, objetivos, etc.)
            
        Returns:
            Análisis motivador del progreso
        """
        prompt = """
        Observa esta imagen de progreso físico y proporciona:
        
        1. **Reconocimiento del esfuerzo** 💪
           - Mensaje motivador y positivo
           - Reconocimiento del trabajo realizado
        
        2. **Observaciones constructivas** 📈
           - Cambios positivos observables (si los hay)
           - Áreas que muestran desarrollo
        
        3. **Recomendaciones futuras** 🎯
           - Sugerencias para continuar el progreso
           - Áreas en las que enfocarse
        
        4. **Motivación** ⭐
           - Mensaje inspirador personalizado
           - Recordatorio de que el progreso no siempre es visible
        
        IMPORTANTE: Sé respetuoso, positivo y evita comentarios sobre peso o 
        apariencia que puedan ser negativos. Enfócate en salud y bienestar.
        """
        
        return await self.analyze_image(image_data, "progress")
    
    def _get_analysis_prompt(self, image_type: str) -> str:
        """
        Obtener prompt específico según el tipo de imagen
        
        Args:
            image_type: Tipo de imagen a analizar
            
        Returns:
            Prompt apropiado para el análisis
        """
        prompts = {
            "food": "Analiza esta imagen de comida. Identifica los alimentos, estima las calorías y macronutrientes, y proporciona una evaluación nutricional completa.",
            "exercise": "Analiza esta imagen de ejercicio o postura. Evalúa la técnica, identifica posibles errores y proporciona correcciones específicas.",
            "progress": "Analiza esta imagen de progreso físico de manera respetuosa y motivadora. Enfócate en aspectos positivos y proporciona encouragement.",
            "auto": "Analiza esta imagen relacionada con fitness o nutrición. Identifica qué tipo de contenido es y proporciona un análisis apropiado."
        }
        
        return prompts.get(image_type, prompts["auto"])
    
    def _get_timestamp(self) -> str:
        """
        Obtener timestamp actual
        
        Returns:
            Timestamp en formato ISO
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def download_whatsapp_image(self, image_id: str, whatsapp_token: str) -> bytes:
        """
        Descargar imagen desde WhatsApp
        
        Args:
            image_id: ID de la imagen en WhatsApp
            whatsapp_token: Token de autenticación
            
        Returns:
            Datos de la imagen en bytes
        """
        try:
            # Primero obtener la URL de la imagen
            async with httpx.AsyncClient() as client:
                media_response = await client.get(
                    f"https://graph.facebook.com/v18.0/{image_id}",
                    headers={"Authorization": f"Bearer {whatsapp_token}"}
                )
                media_data = media_response.json()
                image_url = media_data.get("url")
                
                # Descargar la imagen
                image_response = await client.get(
                    image_url,
                    headers={"Authorization": f"Bearer {whatsapp_token}"}
                )
                
                return image_response.content
                
        except Exception as e:
            logger.error(f"❌ Error descargando imagen de WhatsApp: {str(e)}")
            raise

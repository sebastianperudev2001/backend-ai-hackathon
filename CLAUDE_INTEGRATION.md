# 🤖 Integración de Claude y LangGraph - Sistema Multi-Agente

## 📋 Descripción

Este sistema implementa un bot de WhatsApp inteligente para fitness y nutrición usando:

- **Claude 3.5 Sonnet** de Anthropic para procesamiento de lenguaje natural
- **LangGraph** para orquestación de agentes
- **Sistema Multi-Agente** con agentes especializados

## 🏗️ Arquitectura

```
┌─────────────────┐
│   WhatsApp API  │
└────────┬────────┘
         │
┌────────▼────────┐
│  WhatsApp       │
│  Service        │
└────────┬────────┘
         │
┌────────▼────────┐
│  Coordinator    │◄── LangGraph
│  Agent          │    Orchestration
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    │         │          │         │
┌───▼──┐ ┌───▼──┐ ┌─────▼──┐ ┌───▼──┐
│Fitness│ │Nutrition│ │Image │ │General│
│Agent  │ │Agent    │ │Agent │ │Agent  │
└───────┘ └─────────┘ └──────┘ └───────┘
```

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# REQUERIDO: Claude API
ANTHROPIC_API_KEY=tu_api_key_de_anthropic

# Configuración de WhatsApp (si usas WhatsApp)
WHATSAPP_TOKEN=tu_token_de_whatsapp
WHATSAPP_PHONE_ID=tu_phone_id
VERIFY_TOKEN=tu_verify_token

# Configuración del sistema
ENABLE_MULTI_AGENT=true
CLAUDE_MODEL=claude-3-5-sonnet-20241022
AGENT_MAX_ITERATIONS=10
AGENT_TIMEOUT=30.0
```

### 3. Obtener API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com)
2. Crea una cuenta o inicia sesión
3. Ve a API Keys
4. Crea una nueva API key
5. Copia la key en tu `.env`

## 🧪 Pruebas

### Ejecutar pruebas del sistema

```bash
python test_agents.py
```

Este script ofrece:

- Pruebas automáticas de todos los agentes
- Modo interactivo para chatear con el bot
- Pruebas individuales de cada agente

### Probar con WhatsApp

```bash
python main.py
```

Luego configura el webhook en Meta Business:

- URL: `https://tu-dominio.com/webhook`
- Verify Token: El que pusiste en `.env`

## 🤖 Agentes Disponibles

### 1. **Fitness Agent** 🏋️

- Rutinas de ejercicio personalizadas
- Análisis de técnica
- Prevención de lesiones
- Planes de entrenamiento progresivos

### 2. **Nutrition Agent** 🥗

- Planes de alimentación
- Cálculo de calorías y macros
- Análisis nutricional de comidas
- Recetas saludables

### 3. **Image Analysis Agent** 📸

- Análisis de imágenes de comida (calorías, macros)
- Evaluación de técnica en ejercicios
- Seguimiento de progreso físico
- Usa Claude Vision para análisis visual

### 4. **Coordinator Agent** 🎯

- Orquesta todos los agentes
- Enruta consultas al agente apropiado
- Combina respuestas de múltiples agentes
- Gestiona el flujo de conversación

## 📝 Ejemplos de Uso

### Consultas de Fitness

```
Usuario: "Dame una rutina para principiantes"
Bot: [Genera rutina personalizada con calentamiento, ejercicios y enfriamiento]

Usuario: "¿Cómo hago una sentadilla correctamente?"
Bot: [Explica técnica paso a paso con consejos de seguridad]
```

### Consultas de Nutrición

```
Usuario: "¿Cuántas calorías debo comer para perder peso?"
Bot: [Calcula TDEE y proporciona recomendaciones personalizadas]

Usuario: "Dame recetas saludables para el desayuno"
Bot: [Sugiere 3 recetas con información nutricional]
```

### Análisis de Imágenes

```
Usuario: [Envía foto de un plato de comida]
Bot: [Analiza la imagen y estima calorías, proteínas, carbohidratos y grasas]

Usuario: [Envía foto haciendo ejercicio]
Bot: [Analiza la postura y proporciona correcciones de técnica]
```

### Consultas Mixtas

```
Usuario: "Quiero perder peso, ¿qué ejercicios y dieta me recomiendas?"
Bot: [Combina respuestas del agente de fitness y nutrición]
```

## 🔧 Configuración Avanzada

### Personalizar Agentes

Puedes modificar los prompts de sistema en cada agente:

```python
# agents/fitness_agent.py
system_prompt = """
Tu prompt personalizado aquí...
"""
```

### Agregar Nuevos Agentes

1. Crea una nueva clase heredando de `BaseAgent`
2. Agrégala al coordinador en `agents/coordinator.py`
3. Actualiza el routing en `_classify_intent`

### Modificar el Flujo de LangGraph

El flujo está definido en `coordinator.py` método `_build_graph()`:

```python
workflow.add_node("tu_nuevo_nodo", self._tu_metodo)
workflow.add_edge("origen", "destino")
```

## 📊 Monitoreo y Logs

El sistema incluye logs detallados:

```python
# Ver todos los logs
LOG_LEVEL=DEBUG python main.py

# Logs por defecto (INFO)
LOG_LEVEL=INFO python main.py
```

## 🐛 Solución de Problemas

### Error: "ANTHROPIC_API_KEY no configurada"

- Verifica que tu archivo `.env` existe
- Confirma que la API key es válida

### Error: "Rate limit exceeded"

- Espera unos minutos
- Considera actualizar tu plan en Anthropic

### Las respuestas son muy lentas

- Ajusta `AGENT_TIMEOUT` en `.env`
- Verifica tu conexión a internet

### El bot no responde en WhatsApp

- Verifica que el webhook está configurado
- Revisa los logs para errores
- Confirma que `WHATSAPP_TOKEN` es correcto

## 🚢 Deploy

### Con Railway (Recomendado)

1. Conecta tu repo a Railway
2. Agrega las variables de entorno en Railway
3. Deploy automático al hacer push

### Con Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Manual en VPS

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar nginx para proxy reverso
# Usar PM2 o supervisor para mantener el proceso activo
pm2 start main.py --interpreter python3
```

## 📚 Recursos

- [Documentación de Claude](https://docs.anthropic.com)
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch
3. Commit tus cambios
4. Push a la branch
5. Abre un Pull Request

## 📄 Licencia

MIT License - Úsalo como quieras 🎉

## 💡 Tips para el Hackathon

- **Diferenciador clave**: Sistema multi-agente con especialización
- **Valor agregado**: Análisis de imágenes con Claude Vision
- **Escalabilidad**: Fácil agregar nuevos agentes
- **UX**: Respuestas contextuales y personalizadas
- **Demo**: Usa `test_agents.py` para demostración en vivo

¡Buena suerte en el hackathon! 💪🚀

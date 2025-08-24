# 🔧 Configuración de Variables de Entorno

## Archivo .env de Ejemplo

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# ==================== CONFIGURACIÓN DE EJEMPLO ====================
# Copia este contenido en tu archivo .env y configura tus credenciales reales

# WhatsApp Business API
WHATSAPP_TOKEN=tu_token_de_whatsapp_aqui
WHATSAPP_PHONE_ID=tu_phone_id_aqui
VERIFY_TOKEN=tu_verify_token_secreto

# Aplicación
APP_ENV=development
PORT=8000
LOG_LEVEL=INFO

# Features
ENABLE_IMAGE_PROCESSING=false
ENABLE_AI_RESPONSES=true
ENABLE_MULTI_AGENT=true

# Claude API Configuration (REQUERIDO para IA)
ANTHROPIC_API_KEY=tu_api_key_de_claude_aqui
CLAUDE_MODEL=claude-3-5-sonnet-latest

# LangGraph Configuration
AGENT_MAX_ITERATIONS=10
AGENT_TIMEOUT=30.0

# Supabase Configuration (REQUERIDO para fitness tracking)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui
```

## 📋 Instrucciones de Configuración

### 1. Claude API Key (REQUERIDO)

- Ve a [console.anthropic.com](https://console.anthropic.com)
- Crea una cuenta y obtén tu API key
- Pégala en `ANTHROPIC_API_KEY`

### 2. Supabase (REQUERIDO para fitness tracking)

- Ve a [supabase.com](https://supabase.com)
- Crea un nuevo proyecto
- Ve a Settings > API
- Copia la URL y anon key
- Ejecuta el archivo `database/schema.sql` en el SQL Editor de Supabase

### 3. WhatsApp (Opcional para desarrollo)

- Configura WhatsApp Business API
- Obtén token y phone ID de Meta for Developers

## 🧪 Testing

### Para probar sin configurar todo:

```bash
python3 test_fitness_basic.py
```

### Para pruebas completas con base de datos:

```bash
python3 test_fitness_integration.py
```

## ⚠️ Notas Importantes

- **Sin Claude API**: El agente funcionará en modo demo
- **Sin Supabase**: Las herramientas de fitness no podrán guardar datos
- **Sin WhatsApp**: Solo para desarrollo local, no afecta las funciones de fitness

## 🔒 Seguridad

- Nunca subas el archivo `.env` al repositorio
- Usa variables de entorno en producción
- El archivo `.env` ya está en `.gitignore`

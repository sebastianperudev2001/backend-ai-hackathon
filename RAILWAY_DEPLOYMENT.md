# 🚂 Guía de Despliegue en Railway

## ✅ Tu proyecto ya está listo para Railway

Este proyecto ha sido completamente configurado para desplegarse en Railway sin problemas.

## 📋 Pasos para desplegar

### 1. Subir código a GitHub

```bash
# Inicializar git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "Initial commit - WhatsApp Bot ready for Railway"

# Conectar con tu repositorio de GitHub
git remote add origin https://github.com/tu-usuario/tu-repo.git

# Push al repositorio
git push -u origin main
```

### 2. Crear proyecto en Railway

1. Ve a [railway.app](https://railway.app)
2. Haz click en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway para acceder a GitHub
5. Selecciona tu repositorio

### 3. Configurar Variables de Entorno

En el dashboard de Railway, ve a la pestaña **Variables** y agrega:

```bash
# REQUERIDAS - WhatsApp Business API
WHATSAPP_TOKEN=tu_token_de_whatsapp_business
WHATSAPP_PHONE_ID=tu_phone_number_id
VERIFY_TOKEN=tu_token_secreto_para_webhook

# OPCIONALES - Configuración
APP_ENV=production
LOG_LEVEL=INFO
WHATSAPP_API_VERSION=v18.0

# OPCIONALES - Feature Flags
ENABLE_IMAGE_PROCESSING=false
ENABLE_AI_RESPONSES=false
```

### 4. Obtener tu URL

Railway te asignará automáticamente una URL como:

```
https://tu-proyecto.up.railway.app
```

### 5. Configurar Webhook en WhatsApp

En tu panel de Meta/WhatsApp Business:

1. **Callback URL**: `https://tu-proyecto.up.railway.app/webhook`
2. **Verify Token**: El mismo valor que pusiste en `VERIFY_TOKEN`
3. **Webhook fields**: Selecciona `messages`

## 🔧 Archivos de configuración incluidos

- ✅ **Procfile** - Define cómo iniciar la aplicación
- ✅ **railway.json** - Configuración optimizada para Railway
- ✅ **runtime.txt** - Especifica versión de Python 3.11.6
- ✅ **requirements.txt** - Todas las dependencias con versiones fijas
- ✅ **main.py** - Configurado para producción
- ✅ **settings.py** - Adaptado para variables de Railway

## 📊 Monitoreo

### Ver logs en Railway

1. En tu dashboard de Railway
2. Click en tu proyecto
3. Ve a la pestaña **"Logs"**

### Endpoints de salud

- Health Check: `https://tu-url.railway.app/health`
- Documentación: `https://tu-url.railway.app/docs`

## 🚀 Comandos útiles

### Re-desplegar manualmente

```bash
git add .
git commit -m "Update: descripción del cambio"
git push origin main
```

Railway detectará el push y re-desplegará automáticamente.

### Ver logs localmente

```bash
railway logs
```

### Variables de entorno locales

```bash
railway run python main.py
```

## ⚠️ Troubleshooting

### Si el webhook no responde

1. Verifica que `VERIFY_TOKEN` sea el mismo en Railway y WhatsApp
2. Revisa los logs en Railway para ver errores
3. Prueba el endpoint manualmente:

```bash
curl "https://tu-url.railway.app/webhook?hub.mode=subscribe&hub.verify_token=tu_token&hub.challenge=123"
```

### Si hay errores de puerto

Railway setea automáticamente la variable `PORT`. No la hardcodees.

### Si hay errores de memoria

El plan gratuito de Railway tiene límites. Optimiza tu código o considera upgrading.

## 💰 Costos

- **Plan Gratuito**: $5 USD de créditos mensuales
- **Suficiente para**: ~500 horas de ejecución
- **Recomendación**: Suficiente para desarrollo y pruebas

## 🎉 ¡Listo!

Tu bot de WhatsApp está listo para desplegarse en Railway. La configuración está optimizada para:

- ✅ Auto-restart en caso de fallos
- ✅ Health checks automáticos
- ✅ Logs estructurados
- ✅ Variables de entorno seguras
- ✅ Despliegue automático con cada push

¿Necesitas ayuda? Revisa los logs en Railway o el endpoint `/health`.

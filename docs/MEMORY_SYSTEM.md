# 🧠 Sistema de Memoria Persistente - Chatbot IA

## 📋 Descripción

El sistema de memoria persistente permite al chatbot recordar conversaciones previas con cada usuario, optimizando las consultas a la base de datos y mejorando significativamente la experiencia del usuario.

## 🏗️ Arquitectura

```
┌─────────────────┐
│   WhatsApp      │
│   User          │
└────────┬────────┘
         │
┌────────▼────────┐
│  Coordinator    │
│  Agent          │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───▼──┐ ┌───▼──┐ ┌─────▼──┐
│Fitness│ │Nutrition│ │Memory │
│Agent  │ │Agent    │ │System │
└───┬───┘ └───┬────┘ └─────┬──┘
    │         │            │
    └─────────┼────────────┘
              │
    ┌─────────▼─────────┐
    │  Supabase DB      │
    │  ┌─────────────┐  │
    │  │conversation_│  │
    │  │sessions     │  │
    │  └─────────────┘  │
    │  ┌─────────────┐  │
    │  │conversation_│  │
    │  │messages     │  │
    │  └─────────────┘  │
    └───────────────────┘
```

## 🗄️ Esquema de Base de Datos

### Tabla `conversation_sessions`

Almacena sesiones de conversación por usuario:

```sql
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Tabla `conversation_messages`

Almacena mensajes individuales de cada conversación:

```sql
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES conversation_sessions(id),
    message_type VARCHAR(20) CHECK (message_type IN ('human', 'ai', 'system', 'function')),
    content TEXT NOT NULL,
    metadata JSONB,
    agent_name VARCHAR(100),
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
);
```

## 🔧 Componentes Principales

### 1. ConversationRepository

Gestiona todas las operaciones de base de datos relacionadas con conversaciones:

```python
from repository.conversation_repository import ConversationRepository

repo = ConversationRepository()

# Crear nueva sesión
session_response = await repo.create_session(CreateSessionRequest(
    user_id="user-uuid",
    session_name="Conversación sobre fitness"
))

# Agregar mensaje
await repo.add_message(AddMessageRequest(
    session_id=session_id,
    message_type=ConversationMessageType.HUMAN,
    content="Hola, quiero empezar a entrenar"
))

# Obtener historial
history = await repo.get_conversation_history(session_id)
```

### 2. PersistentChatMemory

Memoria personalizada de LangChain que se integra con Supabase:

```python
from agents.persistent_memory import PersistentChatMemory

# Crear memoria persistente
memory = PersistentChatMemory(user_id="user-uuid")

# La memoria se carga automáticamente desde la BD
memory_vars = memory.load_memory_variables({})

# Se guarda automáticamente cuando se usa con agentes
memory.save_context(
    {"input": "¿Qué ejercicios me recomendaste?"},
    {"output": "Te recomendé flexiones, sentadillas y plancha"}
)
```

### 3. BaseAgent Actualizado

Todos los agentes ahora soportan memoria persistente:

```python
from agents.fitness_agent import FitnessAgent

# Crear agente con memoria persistente
agent = FitnessAgent(user_id="user-uuid")

# El agente recordará conversaciones previas automáticamente
response = await agent.process("¿Cuántas series me dijiste que hiciera?")
```

## 🚀 Uso del Sistema

### Inicialización Automática

El sistema se inicializa automáticamente cuando se proporciona un `user_id`:

1. **Coordinador** obtiene el `user_id` desde el número de teléfono
2. **Agentes** se crean dinámicamente con memoria persistente
3. **Memoria** carga automáticamente el historial reciente (últimos 60 minutos o 30 mensajes)

### Flujo de Conversación

```python
# 1. Usuario envía mensaje por WhatsApp
user_input = "Hola, quiero empezar una rutina"

# 2. Coordinador procesa con contexto
context = {"sender": "+51998555878"}
response = await coordinator.process_message(user_input, context=context)

# 3. Sistema automáticamente:
#    - Obtiene user_id desde phone_number
#    - Crea/obtiene sesión activa
#    - Carga historial reciente
#    - Procesa mensaje con contexto
#    - Guarda nueva interacción
```

### Gestión de Sesiones

- **Sesión Activa**: Una por usuario, se reutiliza automáticamente
- **Inactividad**: Sesiones se marcan como inactivas después de 7 días
- **Limpieza**: Método `clear()` crea nueva sesión si es necesario

## 📊 Optimizaciones

### Consultas Eficientes

- **Índices**: Optimizados para consultas por usuario y tiempo
- **Límites**: Solo carga mensajes recientes (configurable)
- **Caché**: Memoria en RAM para sesión actual

### Políticas de Seguridad

- **RLS (Row Level Security)**: Usuarios solo ven sus propias conversaciones
- **Políticas**: Automáticas basadas en `app.current_user_id`

## 🧪 Testing

### Ejecutar Tests

```bash
# Test completo del sistema de memoria
python tests/test_memory_functionality.py

# Migrar esquema de base de datos
python tests/migrate_memory_schema.py
```

### Tests Incluidos

1. **Repositorio**: Crear sesiones, agregar mensajes, obtener historial
2. **Memoria Persistente**: Integración con LangChain
3. **Agentes**: Funcionamiento con memoria
4. **Coordinador**: Flujo completo con contexto

## 🔧 Configuración

### Variables de Entorno

Las mismas que el sistema existente:

```env
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_key
ANTHROPIC_API_KEY=tu_anthropic_key
```

### Configuración de Memoria

```python
# En agents/persistent_memory.py
class PersistentChatMemory:
    max_token_limit: int = 4000  # Límite de tokens

# En repository/conversation_repository.py
async def get_recent_messages(
    self,
    session_id: str,
    minutes: int = 60,    # Ventana de tiempo
    limit: int = 20       # Máximo de mensajes
):
```

## 📈 Beneficios

### Para el Usuario

- **Continuidad**: El chatbot recuerda conversaciones previas
- **Contexto**: Respuestas más relevantes y personalizadas
- **Eficiencia**: No necesita repetir información

### Para el Sistema

- **Optimización**: Menos consultas redundantes a la BD
- **Escalabilidad**: Memoria distribuida por usuario
- **Mantenimiento**: Limpieza automática de sesiones antiguas

## 🔍 Monitoreo

### Logs Importantes

```python
# Creación de sesiones
"✅ Sesión creada: {session_id}"

# Carga de memoria
"✅ Mensajes cargados desde BD: {count}"

# Guardado de contexto
"✅ Contexto guardado en BD"

# Errores
"❌ Error en memoria persistente: {error}"
```

### Métricas Sugeridas

- Número de sesiones activas por usuario
- Promedio de mensajes por sesión
- Tiempo de respuesta con/sin memoria
- Tasa de errores de memoria

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error de conexión a BD**

   - Verificar variables de entorno
   - Comprobar conectividad a Supabase

2. **Memoria no se carga**

   - Verificar que las tablas existan
   - Revisar políticas RLS

3. **Sesiones duplicadas**
   - Verificar lógica de `get_or_create_active_session`

### Comandos de Diagnóstico

```python
# Verificar sesiones de usuario
sessions = await repo.get_user_sessions(user_id)

# Obtener resumen de conversación
summary = await memory.get_conversation_summary()

# Limpiar memoria si es necesario
memory.clear()
```

## 🔮 Futuras Mejoras

1. **Compresión de Memoria**: Resumir conversaciones largas
2. **Memoria Semántica**: Búsqueda por similitud de contenido
3. **Análisis de Patrones**: Insights sobre comportamiento del usuario
4. **Memoria Compartida**: Entre diferentes tipos de agentes
5. **Backup/Restore**: Exportar/importar conversaciones

## 📋 Instalación y Configuración

Para activar el sistema de memoria:

### Paso 1: Aplicar Migración de Base de Datos

**Opción A: Manual (Recomendado)**

1. Ve a tu dashboard de Supabase
2. Abre el **SQL Editor**
3. Ejecuta el contenido completo de `database/memory_migration.sql`

**Opción B: Verificación Automática**

```bash
python tests/setup_memory_tables.py
```

### Paso 2: Verificar Instalación

```bash
# Verificar conexión y tablas
python tests/test_supabase_connection.py

# Test simplificado (recomendado)
python tests/test_memory_simple.py

# Test completo (requiere configuración RLS)
python tests/test_memory_functionality.py
```

#### Para Testing Completo (Opcional)

Si quieres probar la funcionalidad completa incluyendo persistencia:

1. **Deshabilitar RLS temporalmente**:

   ```sql
   -- En Supabase SQL Editor, ejecutar:
   -- database/disable_rls_for_testing.sql
   ```

2. **Ejecutar tests completos**:

   ```bash
   python tests/test_memory_functionality.py
   ```

3. **Rehabilitar RLS**:
   ```sql
   -- En Supabase SQL Editor, ejecutar:
   -- database/enable_rls_after_testing.sql
   ```

### Paso 3: Desplegar Cambios

El sistema está listo para usar automáticamente una vez que las tablas estén creadas.

## 📚 Referencias

- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)

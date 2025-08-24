# 🔧 Solución de Problemas - FitnessAgent

## 🚨 Problemas Comunes y Soluciones

### 1. Error: "new row violates row-level security policy"

**Problema:** Las políticas RLS impiden insertar datos en las tablas.

**Causa:** El contexto de usuario no se está estableciendo correctamente.

**Soluciones:**

#### Opción A: Deshabilitar RLS temporalmente (DESARROLLO)

```sql
-- Ejecutar en Supabase SQL Editor
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE workouts DISABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sets DISABLE ROW LEVEL SECURITY;
```

#### Opción B: Verificar función set_config

```sql
-- Verificar que la función existe
SELECT proname FROM pg_proc WHERE proname = 'set_config';

-- Si no existe, ejecutar el schema.sql completo
```

#### Opción C: Usar Service Key

En lugar de la anon key, usar la service key en `.env`:

```env
SUPABASE_KEY=tu_service_role_key_aqui
```

### 2. Error: "Client.**init**() got an unexpected keyword argument 'proxies'"

**Problema:** Incompatibilidad de versiones de librerías.

**Solución:**

```bash
pip install --upgrade anthropic langchain-anthropic
```

### 3. Agent executor no disponible

**Problema:** El LLM no se inicializa correctamente.

**Verificaciones:**

- ✅ `ANTHROPIC_API_KEY` configurada en `.env`
- ✅ Créditos disponibles en cuenta de Anthropic
- ✅ Conexión a internet estable

### 4. Herramientas no se ejecutan

**Problema:** El agente no usa las herramientas cuando debería.

**Verificaciones:**

- ✅ Usar frases específicas: "empezar rutina", "registrar serie"
- ✅ Evitar consultas generales: "¿cómo hacer flexiones?"
- ✅ Agent executor debe estar disponible

## 🧪 Scripts de Prueba

### Prueba Básica (Sin DB)

```bash
python3 test_simple_workout.py
```

### Prueba con Usuario Demo

```bash
# Primero configurar .env con credenciales
python3 test_demo_user.py
```

## 📋 Checklist de Configuración

### Variables de Entorno (.env)

```env
# Mínimo requerido
ANTHROPIC_API_KEY=tu_claude_key

# Para funcionalidad completa
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_o_service_key
```

### Base de Datos Supabase

- [ ] Proyecto creado en supabase.com
- [ ] Schema ejecutado (`database/schema.sql`)
- [ ] Usuario demo insertado
- [ ] RLS configurado o deshabilitado

### Dependencias Python

```bash
pip install -r requirements.txt
```

## 🔍 Debugging

### Logs Importantes

```bash
# Buscar estos mensajes en los logs:
✅ Cliente de Supabase inicializado correctamente
✅ Agente FitnessAgent inicializado
🔐 Contexto de usuario establecido
🔧 Procesando con herramientas disponibles
```

### Verificar Conexión a Supabase

```python
from repository.supabase_client import get_supabase_client

client = get_supabase_client()
print(f"Conectado: {client.is_connected()}")
```

### Verificar Usuario Demo

```sql
-- En Supabase SQL Editor
SELECT * FROM users WHERE phone_number = '+51998555878';
```

## 🚀 Flujo de Solución Rápida

1. **Ejecutar prueba básica**

   ```bash
   python3 test_simple_workout.py
   ```

2. **Si hay errores de RLS**

   ```sql
   -- En Supabase SQL Editor
   \i database/disable_rls_temp.sql
   ```

3. **Si no hay respuestas de IA**

   - Verificar `ANTHROPIC_API_KEY` en `.env`
   - Verificar créditos en console.anthropic.com

4. **Si hay errores de conexión DB**
   - Verificar `SUPABASE_URL` y `SUPABASE_KEY`
   - Verificar que el proyecto Supabase esté activo

## 📞 Soporte Adicional

### Logs Detallados

```bash
export LOG_LEVEL=DEBUG
python3 test_simple_workout.py
```

### Verificar Configuración

```python
from config.settings import get_settings
settings = get_settings()
print(f"Supabase URL: {settings.SUPABASE_URL}")
print(f"Claude Key: {'Configurada' if settings.ANTHROPIC_API_KEY else 'No configurada'}")
```

---

**Nota:** Para desarrollo, es recomendable deshabilitar RLS temporalmente hasta que la configuración esté completamente funcional.

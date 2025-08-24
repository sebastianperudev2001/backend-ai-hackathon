# 🧪 Guía de Testing del Sistema de Nutrición

## 📋 Preparación (Solo una vez)

### 1. **Configurar Base de Datos en Supabase**

Ejecuta estos scripts en el **SQL Editor de Supabase** en este orden:

```sql
-- 1. Esquema principal (si no lo tienes ya)
-- Ejecutar: database/schema.sql

-- 2. Esquema de dietas (NUEVO)
-- Ejecutar: database/diet_schema.sql

-- 3. Deshabilitar RLS para testing
-- Ejecutar: database/disable_rls_diet_tables.sql

-- 4. Insertar alimentos básicos
-- Ejecutar en Python: python3 scripts/insert_common_foods.py
```

### 2. **Variables de Entorno**

Asegúrate de tener configurado:

```bash
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
ANTHROPIC_API_KEY=tu_clave_de_claude
```

## 🚀 **Opciones de Testing**

### **OPCIÓN 1: Pruebas Automatizadas** (Recomendado)

```bash
# Ejecutar desde /backend
python3 test_nutrition_system.py
```

**¿Qué prueba?**

- ✅ Detección de mensajes del agente
- 🔍 Búsqueda de alimentos
- 📅 Consulta de comidas del día
- ⏰ Siguiente comida programada
- 📊 Análisis nutricional
- 🤖 Procesamiento de mensajes

### **OPCIÓN 2: Testing Manual por WhatsApp**

Una vez configurada la DB, puedes probar enviando mensajes:

**Consultas de Comidas:**

- "¿Qué comidas tengo hoy?"
- "¿Cuál es mi siguiente comida?"
- "¿Cuándo como?"

**Análisis Nutricional:**

- "¿Cómo voy con mi dieta?"
- "Mi progreso nutricional"
- "¿Estoy cumpliendo mis objetivos?"

**Búsqueda de Alimentos:**

- "Buscar pollo"
- "Alimentos ricos en proteína"
- "Opciones vegetarianas"

### **OPCIÓN 3: Testing Directo de Componentes**

```python
# Probar solo el agente
from agents.nutrition_agent_simple import NutritionAgent
agent = NutritionAgent()
result = agent.can_handle("¿Qué comidas tengo hoy?", {})
print(f"Puede manejar: {result}")
```

```python
# Probar búsqueda de alimentos
from agents.nutrition_tools import NutritionTools
tools = NutritionTools()
result = await tools.search_foods("pollo", limit=3)
print(result)
```

## 📊 **Resultados Esperados**

### ✅ **Detección de Mensajes**

```
✅ '¿Qué comidas tengo hoy?' -> True
✅ '¿Cuál es mi siguiente comida?' -> True
✅ '¿Cómo voy con mi dieta?' -> True
✅ 'Buscar alimentos ricos en proteína' -> True
❌ '¿Cómo hacer ejercicio?' -> False (correcto)
```

### 🔍 **Búsqueda de Alimentos**

```
Resultado búsqueda 'pollo': success=True
- Pechuga de pollo: 165 cal/100g
- Proteína: 31.0g | Carbos: 0.0g
```

### 📅 **Consulta de Comidas**

```
Comidas planificadas: X
Comidas consumidas: Y
Objetivo calórico: 2000 cal
Estado: on_track/under/over
```

### 📊 **Análisis Nutricional**

```
Estado calórico: on_track
Balance macros: 0.85/1.0
Adherencia: 85.5%
Recomendaciones: [lista]
```

## 🐛 **Troubleshooting**

### **Error: 'SupabaseClient' object has no attribute 'table'**

- **Causa:** Base de datos no configurada o credenciales incorrectas
- **Solución:** Verificar variables de entorno y ejecutar esquemas SQL

### **Error: ChatAnthropic initialization**

- **Causa:** Problema con Claude API key
- **Solución:** Verificar ANTHROPIC_API_KEY o comentar esa línea para testing

### **Error: No foods found**

- **Causa:** Tabla foods vacía
- **Solución:** Ejecutar `python3 scripts/insert_common_foods.py`

### **Error: No diet plan active**

- **Causa:** Usuario no tiene plan de dieta
- **Solución:** Normal en testing inicial, crear plan via API o SQL

## 🎯 **Escenarios de Prueba Manuales**

### **Escenario 1: Usuario Nuevo**

1. Usuario pregunta: "¿Qué comidas tengo hoy?"
2. **Esperado:** "No tienes plan de dieta activo" o comidas vacías
3. **Siguiente:** Crear plan de dieta para el usuario

### **Escenario 2: Usuario con Plan**

1. Crear plan de dieta en DB
2. Usuario pregunta: "¿Qué comidas tengo hoy?"
3. **Esperado:** Lista de comidas planificadas

### **Escenario 3: Búsqueda de Alimentos**

1. Usuario: "Buscar pollo"
2. **Esperado:** Lista de alimentos con "pollo" en el nombre
3. **Verificar:** Información nutricional correcta

### **Escenario 4: Análisis sin Datos**

1. Usuario: "¿Cómo voy con mi dieta?"
2. **Esperado:** Resumen con 0 calorías consumidas
3. **Verificar:** Recomendaciones apropiadas

## 📈 **Métricas de Éxito**

- ✅ **Detección de mensajes > 80%** de precisión
- ✅ **Búsqueda de alimentos** funciona con DB poblada
- ✅ **Consultas de comidas** retornan datos estructurados
- ✅ **Análisis nutricional** calcula métricas correctamente
- ✅ **Respuestas en español** bien formateadas
- ✅ **Manejo de errores** sin crashes del sistema

## 🚨 **Testing en Producción**

Antes de ir a producción:

1. **Habilitar RLS:** `database/enable_rls_diet_tables.sql`
2. **Crear usuarios de prueba** con planes completos
3. **Testear flujo completo** usuario → webhook → agente → respuesta
4. **Verificar rendimiento** con múltiples usuarios simultáneos

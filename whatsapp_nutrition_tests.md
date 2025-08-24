# 📱 Testing del Sistema de Nutrición via WhatsApp

## 🧪 Casos de Prueba para WhatsApp

### **Nivel 1: Detección Básica** ✅

Verificar que el agente de nutrición responde a estos mensajes:

```
✅ "¿Qué comidas tengo hoy?"
✅ "¿Cuál es mi siguiente comida?"
✅ "¿Cómo voy con mi dieta?"
✅ "Mi progreso nutricional"
✅ "Buscar alimentos ricos en proteína"
✅ "¿Cuántas calorías he consumido?"
```

### **Nivel 2: Funcionalidad Completa** 🔄

Con base de datos configurada:

#### **Consultas de Comidas** 📅

```
Usuario: "¿Qué comidas tengo hoy?"
Esperado: Lista de comidas programadas + resumen nutricional

Usuario: "¿Cuál es mi siguiente comida?"
Esperado: Próxima comida con horario y detalles
```

#### **Búsqueda de Alimentos** 🔍

```
Usuario: "Buscar pollo"
Esperado: Lista de alimentos con "pollo" + info nutricional

Usuario: "Alimentos vegetarianos"
Esperado: Lista filtrada de alimentos vegetarianos
```

#### **Análisis Nutricional** 📊

```
Usuario: "¿Cómo voy con mi dieta?"
Esperado: Estado calórico + balance macros + recomendaciones

Usuario: "Mi déficit calórico"
Esperado: Análisis de déficit/superávit del día
```

## 🎯 **Mensajes de Prueba Completos**

### **Set 1: Consultas Básicas**

```
1. "Hola, ¿qué comidas tengo programadas para hoy?"
2. "¿Cuándo es mi siguiente comida?"
3. "¿Cómo voy con mi plan nutricional?"
4. "Buscar alimentos con proteína"
5. "¿Cuántas calorías he consumido hoy?"
```

### **Set 2: Variaciones de Lenguaje**

```
1. "que como hoy"
2. "siguiente comida"
3. "como voy con la dieta"
4. "buscar pollo"
5. "mis calorias de hoy"
```

### **Set 3: Casos Edge**

```
1. "¿Tengo comidas?" (respuesta mínima)
2. "buscar" (sin término específico)
3. "dieta" (palabra clave sola)
4. "Mi análisis" (término incompleto)
```

## 📋 **Checklist de Resultados**

### ✅ **Debe Funcionar:**

- [ ] Respuestas en español
- [ ] Formato con emojis y estructura clara
- [ ] Detección correcta de intención
- [ ] Manejo de errores sin crashes
- [ ] Información nutricional precisa

### ❌ **No Debe Manejar:**

- [ ] "¿Cómo hacer ejercicio?" → Fitness Agent
- [ ] "Rutina de pecho" → Fitness Agent
- [ ] "¿Qué tal el clima?" → Fuera de scope
- [ ] "Configurar algo" → Fuera de scope

## 🐛 **Debugging Tips**

### **Si no responde a consultas nutricionales:**

1. Verificar que el agente esté registrado en coordinator.py
2. Revisar logs del webhook para ver qué agente se selecciona
3. Probar con `quick_nutrition_test.py` la detección

### **Si responde pero con errores de DB:**

1. Verificar conexión a Supabase
2. Ejecutar `disable_rls_diet_tables.sql`
3. Verificar que las tablas existen con `\dt` en psql

### **Si los datos están vacíos:**

1. Ejecutar `insert_common_foods.py`
2. Crear plan de dieta manual en Supabase
3. Verificar user_id en las consultas

## 📊 **Métricas de Éxito**

### **Funcionalidad Core (Nivel Mínimo)**

- ✅ Detección de mensajes nutricionales > 80%
- ✅ Respuestas formateadas correctamente
- ✅ Sin crashes del sistema
- ✅ Manejo básico de errores

### **Funcionalidad Completa (Objetivo)**

- ✅ Búsqueda de alimentos funcional
- ✅ Consultas de comidas con datos reales
- ✅ Análisis nutricional con cálculos
- ✅ Recomendaciones personalizadas

## 🚀 **Script de Testing Automático via WhatsApp**

Para testing masivo, puedes usar:

```python
# test_whatsapp_nutrition.py
import requests
import time

def send_test_message(message):
    """Enviar mensaje de prueba via webhook simulado"""
    # Tu lógica de envío aquí
    pass

test_messages = [
    "¿Qué comidas tengo hoy?",
    "¿Cuál es mi siguiente comida?",
    "¿Cómo voy con mi dieta?",
    "Buscar pollo",
    "Mi progreso nutricional"
]

for msg in test_messages:
    print(f"Enviando: {msg}")
    response = send_test_message(msg)
    print(f"Respuesta: {response}")
    time.sleep(2)  # Evitar rate limiting
```

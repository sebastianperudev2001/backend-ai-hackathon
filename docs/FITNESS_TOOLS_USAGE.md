# 🏋️ Guía de Uso de Herramientas de Fitness

## 📋 Resumen de Problemas Resueltos

### ✅ **Problema Principal Solucionado**

El agente estaba usando parámetros incorrectos en las herramientas de fitness. Ahora todas las herramientas aceptan `phone_number` como parámetro principal.

### 🔧 **Herramientas Disponibles**

#### 1. **get_active_workout**

**Uso correcto:**

```python
get_active_workout(phone_number="+51998555878")
```

- ✅ Verifica si hay rutinas activas
- ✅ Muestra detalles completos (ID, nombre, duración, series)
- ✅ **USAR SIEMPRE** antes de agregar series

#### 2. **start_workout**

**Uso correcto:**

```python
start_workout(
    phone_number="+51998555878",
    name="Rutina de Piernas",
    description="Entrenamiento enfocado en piernas"
)
```

- ✅ Inicia nueva rutina cuando no hay activas
- ✅ Registra timestamp de inicio
- ✅ Crea contexto para agregar series

#### 3. **add_set_simple** (NUEVA - MÁS FÁCIL)

**Uso correcto:**

```python
add_set_simple(
    phone_number="+51998555878",
    exercise="Sentadillas",
    reps=10,
    weight=100,
    sets=1,
    notes="Primera serie"
)
```

- ✅ **Herramienta recomendada** para agregar series
- ✅ Encuentra automáticamente la rutina activa
- ✅ Parámetros simples y claros

#### 4. **end_active_workout**

**Uso correcto:**

```python
end_active_workout(
    phone_number="+51998555878",
    notes="Rutina completada"
)
```

- ✅ Finaliza automáticamente la rutina activa
- ✅ No necesita workout_id específico
- ✅ Genera resumen completo

### 🔀 **Flujo Correcto para el Agente**

#### **Escenario 1: Usuario quiere agregar series**

```
1. get_active_workout(phone_number="+51998555878")
   ↓
   Si hay rutina activa:
   2. add_set_simple(phone_number="+51998555878", exercise="Sentadillas", reps=10, weight=100)

   Si NO hay rutina activa:
   2. start_workout(phone_number="+51998555878", name="Nueva Rutina")
   3. add_set_simple(phone_number="+51998555878", exercise="Sentadillas", reps=10, weight=100)
```

#### **Escenario 2: Usuario quiere finalizar rutina**

```
1. get_active_workout(phone_number="+51998555878")
   ↓
   Si hay rutina activa:
   2. end_active_workout(phone_number="+51998555878", notes="Rutina completada")

   Si NO hay rutina activa:
   2. "No hay rutinas activas para finalizar"
```

### ⚠️ **Errores Comunes del Agente CORREGIDOS**

#### ❌ **ANTES (Incorrecto):**

```python
# El agente hacía esto mal:
get_active_workout(phone_number="+51998555878")  # ✅ Esto estaba bien
start_workout(phone_number="+51998555878")       # ✅ Esto estaba bien
add_set(phone_number="+51998555878", exercise="Sentadillas", reps=10)  # ❌ Tool no existía así
```

#### ✅ **AHORA (Correcto):**

```python
# El agente debe hacer esto:
get_active_workout(phone_number="+51998555878")
start_workout(phone_number="+51998555878", name="Rutina Nueva")
add_set_simple(phone_number="+51998555878", exercise="Sentadillas", reps=10, weight=100)
end_active_workout(phone_number="+51998555878")
```

### 🎯 **Mensajes de Respuesta Mejorados**

Las herramientas ahora devuelven respuestas más claras:

#### **get_active_workout:**

```
🏋️ **Rutina activa encontrada:**

📝 **Nombre:** Rutina de Piernas
🆔 **ID:** 08dc20af-27a6-4abe-88b2-a76f35834ce6
⏰ **Iniciada:** 14:35:22 del 24/08/2025
📊 **Series registradas:** 3
📋 **Descripción:** Entrenamiento enfocado en piernas
```

#### **add_set_simple:**

```
✅ ¡Serie registrada exitosamente!

🏋️ **Ejercicio:** Sentadillas
📊 **Serie:** #1
⚖️ **Peso:** 100 kg
🔢 **Repeticiones:** 10
🆔 **Rutina:** Rutina de Piernas

¡Sigue así! 💪 ¿Vas a hacer otra serie?
```

### 📊 **Verificación de Funcionamiento**

Las herramientas han sido probadas exitosamente:

```
✅ get_active_workout: Encuentra rutinas activas
✅ start_workout: Crea nuevas rutinas
✅ add_set_simple: Registra series automáticamente
✅ end_active_workout: Finaliza rutinas exitosamente
```

### 🚀 **Para el Agente:**

**Usa siempre este patrón:**

1. Verificar rutina activa con `get_active_workout(phone_number="...")`
2. Si no hay rutina, usar `start_workout(phone_number="...", name="...")`
3. Para agregar series, usar `add_set_simple(phone_number="...", exercise="...", reps=..., weight=...)`
4. Para finalizar, usar `end_active_workout(phone_number="...", notes="...")`

### 💡 **Consejos para el Agente:**

1. **Siempre usar phone_number**: Todas las herramientas lo requieren
2. **Verificar primero**: Usar `get_active_workout` antes de agregar series
3. **Nombres claros**: Para rutinas usar nombres descriptivos como "Rutina de Piernas"
4. **add_set_simple**: Es más fácil que `add_set` - usar preferentemente
5. **Manejo de errores**: Las herramientas dan mensajes claros si algo falla

¡El sistema está listo para un uso fluido y sin errores! 🎉

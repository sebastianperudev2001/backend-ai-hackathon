# Progressive Overload Tool Documentation

## Resumen

Se ha agregado una nueva herramienta al FitnessAgent llamada `GetProgressiveOverloadTool` que analiza el historial de ejercicios de un usuario y proporciona recomendaciones específicas sobre sobrecarga progresiva.

## Características

### ✅ Funcionalidades Implementadas

- **Análisis histórico**: Examina las últimas 4 semanas (configurable) de datos de un ejercicio específico
- **Detección de tendencias**: Identifica si el peso/repeticiones están aumentando, disminuyendo o estables
- **Recomendaciones inteligentes**: Sugiere si incrementar peso o repeticiones basándose en el progreso actual
- **Diferenciación de ejercicios**: Distingue entre ejercicios de fuerza (con peso) y cardio/calistenia
- **Consejos específicos**: Proporciona incrementos de peso y repeticiones apropiados
- **Manejo de casos edge**: Respuesta apropiada cuando no hay suficiente historial

### 🛠️ Implementación Técnica

#### Nuevos Archivos/Modificaciones

1. **`agents/fitness_tools.py`**:

   - `GetProgressiveOverloadSchema`: Schema para parámetros del tool
   - `GetProgressiveOverloadTool`: Implementación principal del tool
   - Agregado a `get_fitness_tools()`

2. **`repository/fitness_repository.py`**:

   - `get_exercise_history()`: Nuevo método para obtener historial de ejercicios

3. **`agents/fitness_agent.py`**:
   - Actualización del prompt para incluir el nuevo tool
   - Palabras clave para detección de intención de sobrecarga progresiva

#### Schema del Tool

```python
class GetProgressiveOverloadSchema(BaseModel):
    phone_number: str  # Número de WhatsApp del usuario
    exercise_name: str  # Nombre del ejercicio a analizar
    weeks_to_analyze: Optional[int] = 4  # Semanas hacia atrás (por defecto 4)
```

## Uso

### Activación del Tool

El tool se activa automáticamente cuando el usuario hace preguntas relacionadas con:

- Sobrecarga progresiva
- Cómo progresar en un ejercicio
- Aumentar peso o repeticiones
- Cuánto peso subir
- Progresión en ejercicios específicos

#### Ejemplos de activación:

- "¿Cómo puedo progresar en sentadillas?"
- "¿Debo aumentar peso o repeticiones en press de banca?"
- "¿Cuánto peso debo subir en deadlift?"
- "¿Cómo aplicar sobrecarga progresiva en flexiones?"

### Lógica de Recomendaciones

#### Para Ejercicios con Peso:

1. **Si está en peso máximo histórico**:

   - Recomienda incrementar peso (2.5kg si <50kg, 5kg si ≥50kg)
   - Mantener repeticiones actuales
   - Puede reducir reps temporalmente si es necesario

2. **Si no está en peso máximo**:
   - Recomienda aumentar repeticiones primero
   - Una vez que domine las reps, subir peso

#### Para Ejercicios Sin Peso/Cardio:

1. **Si está en máximo de reps**:

   - Recomienda incrementar repeticiones (+3-5)
   - Sugiere progresiones más difíciles

2. **Si no está en máximo**:
   - Recomienda consolidar reps actuales primero
   - Después incrementar gradualmente

## Ejemplo de Respuesta

```
🎯 **Análisis de Sobrecarga Progresiva para Sentadillas**

📈 **Resumen del Progreso:**
• Total de series analizadas: 12
• Entrenamientos realizados: 4
• Período analizado: últimas 14 días únicos

**📊 Análisis de Peso:**
• Peso máximo: 100.0 kg
• Peso promedio: 95.0 kg
• Peso promedio reciente: 100.0 kg
• Tendencia: aumentando

**🔢 Análisis de Repeticiones:**
• Repeticiones máximas: 12
• Repeticiones promedio: 10.2
• Repeticiones promedio recientes: 11.0
• Tendencia: aumentando

🚀 **Recomendaciones de Sobrecarga Progresiva:**

✅ **Incrementar Peso (Recomendado)**
• Intenta aumentar 5 kg en tu próxima sesión
• Mantén las repeticiones en el rango actual (10-12)
• Si puedes completar todas las series con buena técnica, ¡es hora de subir el peso!

📋 **Plan sugerido:**
1. Aumenta a 105.0 kg
2. Reduce repeticiones a 8 si es necesario
3. Una vez que domines este peso, vuelve al rango de repeticiones anterior

💡 **Consejos Generales:**
• Incrementa la carga gradualmente (2.5-5kg o 1-2 reps)
• Mantén la técnica correcta siempre
• Asegúrate de descansar adecuadamente entre entrenamientos
• Escucha a tu cuerpo y no fuerces el progreso
```

## Casos Edge Manejados

### Sin Historial Suficiente

```
❌ No se encontró historial para el ejercicio **Press Arnold** en las últimas 4 semanas.

💡 **Para obtener recomendaciones de sobrecarga progresiva:**
1. Primero registra algunas series de este ejercicio
2. Realiza el ejercicio consistentemente por al menos 2-3 semanas
3. Vuelve a consultar para obtener recomendaciones basadas en tu progreso

¿Te gustaría ver los ejercicios disponibles en la base de datos?
```

## Integración con el Sistema

### Palabras Clave de Activación

El sistema detecta automáticamente intención de sobrecarga progresiva con estas palabras:

- "sobrecarga progresiva"
- "cómo progresar"
- "aumentar peso", "subir peso", "incrementar peso"
- "aumentar repeticiones", "subir reps"
- "cómo mejorar", "progreso en ejercicio"
- "cuánto peso subir", "debo aumentar"
- "siguiente nivel", "progresión"

### Base de Datos

El tool consulta las tablas:

- `users`: Para identificar al usuario
- `workout_sets`: Para obtener series históricas
- `workouts`: Para contexto de entrenamientos
- `exercises`: Para validar nombres de ejercicios

## Consideraciones de Seguridad

- Siempre enfatiza la técnica correcta
- Recomienda incrementos graduales y seguros
- Incluye disclaimers sobre escuchar al cuerpo
- Sugiere consultar profesionales en caso de dudas

## Testing

El tool ha sido probado exitosamente con:

- ✅ Usuarios con historial existente
- ✅ Ejercicios sin historial
- ✅ Diferentes tipos de ejercicios (fuerza vs cardio)
- ✅ Conectividad con Supabase
- ✅ Integración con FitnessAgent

## Próximas Mejoras Posibles

1. **Análisis de volumen total** (peso × reps × series)
2. **Detección de plateaus** automática
3. **Recomendaciones de periodización**
4. **Análisis de patrones de recuperación**
5. **Integración con métricas de fatiga**

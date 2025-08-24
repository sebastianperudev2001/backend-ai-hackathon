# 🏋️ Integración de FitnessAgent con Supabase

## 📋 Descripción

El `FitnessAgent` ahora cuenta con herramientas integradas para registrar y hacer seguimiento de rutinas de ejercicio en tiempo real usando Supabase como base de datos.

## 🚀 Características Implementadas

### 🛠️ Herramientas Disponibles

1. **`start_workout`** - Iniciar una nueva rutina de ejercicio
2. **`end_workout`** - Finalizar una rutina activa
3. **`add_set`** - Registrar una serie completada
4. **`get_active_workout`** - Verificar rutinas activas
5. **`get_exercises`** - Consultar ejercicios disponibles

### 📊 Datos Registrados

Por cada **rutina**:

- Nombre y descripción
- Hora de inicio y fin
- Duración total
- Número total de series
- Notas del usuario

Por cada **serie**:

- Ejercicio realizado
- Peso utilizado y unidad (kg/lbs)
- Número de repeticiones
- Duración (para ejercicios de tiempo)
- Distancia (para ejercicios de cardio)
- Tiempo de descanso
- Dificultad percibida (1-10)
- Notas específicas

## ⚙️ Configuración

### 1. Variables de Entorno

Agrega estas variables a tu archivo `.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui  # Opcional, para operaciones admin

# Claude API (ya existente)
ANTHROPIC_API_KEY=tu_api_key_de_claude
```

### 2. Base de Datos

1. Crea un nuevo proyecto en [Supabase](https://supabase.com)
2. Ve al SQL Editor en tu dashboard
3. Ejecuta el contenido del archivo `database/schema.sql`

### 3. Verificar Instalación

Ejecuta el script de prueba:

```bash
python test_fitness_integration.py
```

## 🔄 Flujo de Uso

### Flujo Típico de Entrenamiento

1. **Usuario**: "Quiero empezar a entrenar"

   - **Agente**: Verifica rutinas activas y sugiere iniciar nueva

2. **Usuario**: "Inicia una rutina de fuerza"

   - **Agente**: Usa `start_workout` para crear registro
   - **Base de datos**: Guarda rutina con timestamp de inicio

3. **Usuario**: "Hice 3 series de 10 flexiones con 15kg"

   - **Agente**: Usa `add_set` para cada serie
   - **Base de datos**: Registra cada serie con detalles

4. **Usuario**: "Terminé mi rutina"
   - **Agente**: Usa `end_workout` para finalizar
   - **Base de datos**: Calcula duración y genera resumen

### Comandos de Ejemplo

```
# Iniciar rutina
"Empezar rutina de fuerza para principiantes"

# Registrar series
"Hice 10 flexiones"
"3 series de sentadillas con 20kg"
"Plancha por 30 segundos"

# Consultar ejercicios
"¿Qué ejercicios de cardio tienes?"
"Muéstrame ejercicios para principiantes"

# Finalizar
"Terminar rutina"
"Finalizar entrenamiento"
```

## 🏗️ Arquitectura

```
WhatsApp User
     ↓
FitnessAgent (con herramientas)
     ↓
FitnessRepository
     ↓
SupabaseClient
     ↓
Supabase Database
```

### Componentes Principales

- **`agents/fitness_agent.py`** - Agente principal con herramientas integradas
- **`agents/fitness_tools.py`** - Definición de herramientas LangChain
- **`repository/fitness_repository.py`** - Lógica de acceso a datos
- **`repository/supabase_client.py`** - Cliente singleton de Supabase
- **`domain/models.py`** - Modelos de datos Pydantic
- **`database/schema.sql`** - Esquema de base de datos

## 📈 Esquema de Base de Datos

### Tablas Principales

1. **`workouts`** - Rutinas de ejercicio

   - `id`, `user_id`, `name`, `description`
   - `started_at`, `ended_at`, `duration_minutes`
   - `total_sets`, `notes`

2. **`exercises`** - Catálogo de ejercicios

   - `id`, `name`, `category`, `muscle_groups`
   - `equipment`, `instructions`, `difficulty_level`

3. **`workout_sets`** - Series individuales
   - `id`, `workout_id`, `exercise_id`, `set_number`
   - `weight`, `weight_unit`, `repetitions`
   - `duration_seconds`, `distance_meters`
   - `rest_seconds`, `difficulty_rating`, `notes`

### Características Avanzadas

- **Triggers automáticos** para calcular duración y total de series
- **Row Level Security (RLS)** para seguridad por usuario
- **Índices optimizados** para consultas rápidas
- **Validaciones de datos** a nivel de base de datos

## 🧪 Testing

### Script de Prueba

```bash
python test_fitness_integration.py
```

### Casos de Prueba Incluidos

1. Consultar rutina activa
2. Iniciar nueva rutina
3. Consultar ejercicios disponibles
4. Registrar series
5. Flujo completo simulado

## 🔧 Personalización

### Agregar Nuevos Ejercicios

```sql
INSERT INTO exercises (name, category, muscle_groups, equipment, instructions, difficulty_level)
VALUES ('Nuevo Ejercicio', 'fuerza', ARRAY['pecho', 'triceps'], 'mancuernas', 'Instrucciones...', 'intermedio');
```

### Modificar Herramientas

Las herramientas están en `agents/fitness_tools.py` y pueden ser extendidas o modificadas según necesidades específicas.

### Personalizar Prompts

El prompt del agente está en `agents/fitness_agent.py` y puede ser ajustado para cambiar el comportamiento del agente.

## 🚨 Consideraciones de Seguridad

- **RLS habilitado** - Los usuarios solo pueden ver sus propios datos
- **Validación de entrada** - Todos los inputs son validados con Pydantic
- **Manejo de errores** - Fallbacks implementados para casos de error
- **Logging completo** - Todas las operaciones son registradas

## 📞 Soporte

Para problemas o preguntas:

1. Revisa los logs de la aplicación
2. Ejecuta el script de prueba
3. Verifica la configuración de Supabase
4. Consulta la documentación de LangChain para herramientas personalizadas

## 🔮 Próximas Mejoras

- [ ] Análisis de progreso histórico
- [ ] Recomendaciones personalizadas basadas en historial
- [ ] Integración con dispositivos wearables
- [ ] Exportación de datos de entrenamiento
- [ ] Gamificación y logros
- [ ] Planes de entrenamiento predefinidos

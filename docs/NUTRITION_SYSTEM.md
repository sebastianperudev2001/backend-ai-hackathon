# Sistema de Nutrición y Dietas

## Resumen

El sistema de nutrición y dietas es el segundo componente principal de la aplicación fitness, diseñado para ayudar a los usuarios a seguir sus planes alimentarios, monitorear su progreso nutricional y mantener el déficit calórico establecido para alcanzar sus objetivos de salud.

## Arquitectura

### Componentes Principales

1. **Nutrition Agent** - Agente especializado en nutrición
2. **Nutrition Tools** - Herramientas para operaciones nutricionales
3. **Diet Repository** - Capa de acceso a datos de dietas
4. **Base de Datos** - 8 tablas principales para manejo completo de dietas

### Flujo de Datos

```
Usuario WhatsApp → Webhook → Coordinator → Nutrition Agent → Tools → Repository → Supabase
```

## Funcionalidades Principales

### 1. Consulta de Comidas del Día 📅

**¿Qué comidas tienes programadas para hoy?**

- Lista todas las comidas planificadas con horarios
- Muestra comidas ya consumidas vs. pendientes
- Resumen nutricional del día (calorías, macros)
- Estado de adherencia al plan

**Ejemplo de uso:**

```
Usuario: "¿Qué comidas tengo hoy?"
Bot: "🗓️ Comidas para 2024-01-15
📅 Programadas:
🌅 Avena con frutas (07:00) - 350 cal
🍽️ Pollo con arroz (13:00) - 450 cal
✅ Consumidas:
🌅 Avena con frutas - 340 cal ⭐⭐⭐⭐
📊 Resumen: 340/2000 cal (déficit: 1660 cal) ✅"
```

### 2. Siguiente Comida ⏰

**¿Cuál es tu siguiente comida y cuándo comerla?**

- Calcula la próxima comida basada en la hora actual
- Tiempo restante hasta la siguiente comida
- Detalles nutricionales y de preparación
- Instrucciones de cocina si están disponibles

**Ejemplo de uso:**

```
Usuario: "¿Cuál es mi siguiente comida?"
Bot: "🍽️ Tu Siguiente Comida: Pollo a la plancha
🕐 Horario: 13:00 en 2h 30min
🔥 Calorías: 450 cal
🥩 Macros: 35g proteína | 40g carbos | 15g grasas
📝 Preparación: Sazonar el pollo y cocinar a fuego medio..."
```

### 3. Análisis Nutricional 📊

**¿Cómo vas con tu dieta y objetivos nutricionales?**

- Estado del déficit/superávit calórico
- Balance de macronutrientes (proteínas, carbohidratos, grasas)
- Porcentaje de adherencia al plan
- Recomendaciones personalizadas

**Métricas incluidas:**

- Calorías consumidas vs. objetivo
- Distribución de macronutrientes
- Puntuación de balance nutricional (0.0 - 1.0)
- Fibra y micronutrientes

### 4. Búsqueda de Alimentos 🔍

**Encuentra alimentos y su información nutricional**

- Búsqueda por nombre en español e inglés
- Filtros por categoría (proteínas, carbohidratos, etc.)
- Restricciones dietéticas (vegetariano, vegano, sin gluten)
- Información nutricional completa por 100g

**Base de datos incluye:**

- +20 alimentos comunes con datos precisos
- Macronutrientes y micronutrientes
- Tamaños de porción típicos
- Índice glucémico cuando relevante

### 5. Registro de Comidas 📝

**Registra lo que has comido para tracking automático**

- Cálculo automático de calorías y macros
- Actualización del resumen nutricional diario
- Sistema de calificación de satisfacción (1-5 estrellas)
- Detección de adherencia al plan

### 6. Ajustes de Dieta ⚖️

**Modifica comidas manteniendo objetivos nutricionales**

- Sustituciones de alimentos equivalentes
- Mantenimiento del déficit calórico objetivo
- Adaptación a restricciones dietéticas
- Sugerencias inteligentes de ingredientes

## Esquema de Base de Datos

### Tablas Principales

1. **`foods`** - Catálogo de alimentos

   - Información nutricional por 100g
   - Macronutrientes (calorías, proteína, carbos, grasas)
   - Micronutrientes (sodio, calcio, hierro, vitaminas)
   - Marcadores dietéticos (vegetariano, vegano, sin gluten)

2. **`diet_plans`** - Planes de dieta personalizados

   - Objetivos nutricionales diarios
   - Distribución de comidas (5 comidas por defecto)
   - Horarios de comidas
   - Restricciones alimentarias

3. **`planned_meals`** - Comidas planificadas

   - Template de comidas por tipo y horario
   - Objetivos nutricionales por comida
   - Instrucciones de preparación

4. **`planned_meal_ingredients`** - Ingredientes de comidas planificadas

   - Cantidades específicas en gramos
   - Cálculo automático de valores nutricionales

5. **`consumed_meals`** - Registro de comidas consumidas

   - Tracking real de lo que come el usuario
   - Cálculo automático de totales nutricionales
   - Sistema de calificación y notas

6. **`consumed_meal_ingredients`** - Ingredientes consumidos

   - Registro detallado de cada ingrediente
   - Marcadores de adherencia al plan

7. **`daily_nutrition_summary`** - Resúmenes nutricionales diarios

   - Objetivos vs. consumo real
   - Cálculo de déficit/superávit calórico
   - Métricas de adherencia

8. **`food_substitutions`** - Sustituciones de alimentos
   - Equivalencias nutricionales
   - Factores de conversión
   - Tipos de sustitución

### Triggers Automáticos

- **Cálculo nutricional automático** - Al agregar ingredientes
- **Actualización de totales** - En comidas planificadas/consumidas
- **Resúmenes diarios** - Actualización en tiempo real
- **Timestamps** - Control automático de fechas

## Inteligencia del Sistema

### Detección de Intenciones

El agente de nutrición detecta automáticamente consultas relacionadas con:

**Palabras clave principales:**

- Comidas: desayuno, almuerzo, cena, colación
- Nutrición: calorías, macros, proteínas, carbohidratos
- Seguimiento: déficit, progreso, adherencia, cumplimiento
- Alimentos: buscar, ingredientes, sustitutos
- Registro: comí, consumí, registrar, anotar

**Patrones de consulta:**

- "¿Qué como hoy?" → Comidas del día
- "¿Cuándo como?" → Siguiente comida
- "¿Cómo voy?" → Análisis nutricional
- "Buscar [alimento]" → Búsqueda de alimentos

### Recomendaciones Inteligentes

El sistema genera recomendaciones personalizadas basadas en:

1. **Estado calórico:**

   - Déficit > 300 cal: "Agregar colación saludable"
   - Exceso > 300 cal: "Reducir porciones próxima comida"
   - Objetivo cumplido: "¡Excelente! Mantén el rumbo"

2. **Balance de macronutrientes:**

   - Déficit de proteína > 20g: Sugerir fuentes proteicas
   - Exceso de grasas: Recomendar ajustes
   - Baja fibra < 20g: Sugerir verduras y frutas

3. **Adherencia al plan:**
   - < 70%: Sugerir preparación anticipada
   - > 90%: Felicitar y motivar continuidad

## API y Herramientas

### Nutrition Tools

```python
class NutritionTools:
    async def get_today_meals(user_id: str) -> Dict
    async def get_next_meal(user_id: str) -> Dict
    async def analyze_nutrition_status(user_id: str) -> Dict
    async def search_foods(query: str, filters: Dict) -> Dict
    async def log_meal(meal_request: LogMealRequest) -> Dict
    async def suggest_meal_adjustments(adjust_request: AdjustDietRequest) -> Dict
```

### Diet Repository

```python
class DietRepository:
    # Alimentos
    async def get_food_by_id(food_id: str) -> Food
    async def search_foods(query: str, category: FoodCategory) -> List[Food]

    # Planes de dieta
    async def create_diet_plan(plan_request: CreateDietPlanRequest) -> DietPlan
    async def get_active_diet_plan(user_id: str) -> DietPlan

    # Comidas planificadas
    async def get_today_planned_meals(user_id: str) -> List[PlannedMeal]
    async def get_next_planned_meal(user_id: str) -> Tuple[PlannedMeal, int]

    # Comidas consumidas
    async def log_consumed_meal(meal_request: LogMealRequest) -> ConsumedMeal

    # Análisis
    async def get_daily_nutrition_summary(user_id: str) -> DailyNutritionSummary
    async def calculate_macro_balance_score(user_id: str) -> float
```

## Casos de Uso Principales

### 1. Consulta Matutina

```
Usuario: "Buenos días, ¿qué debo desayunar?"
→ Agente muestra desayuno planificado con horario y calorías
→ Incluye instrucciones de preparación
→ Informa tiempo hasta la siguiente comida
```

### 2. Seguimiento de Progreso

```
Usuario: "¿Cómo voy con mi dieta?"
→ Análisis completo del día actual
→ Estado del déficit calórico
→ Recomendaciones específicas para mejorar
```

### 3. Búsqueda y Sustitución

```
Usuario: "No tengo pollo, ¿qué puedo comer en su lugar?"
→ Buscar alternativas proteicas
→ Calcular equivalencias nutricionales
→ Mantener objetivos calóricos
```

### 4. Registro Post-Comida

```
Usuario: "Comí una ensalada con atún"
→ Solicitar detalles específicos de ingredientes
→ Calcular automáticamente nutrición
→ Actualizar progreso del día
```

## Configuración e Implementación

### Variables de Entorno

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Inicialización de Base de Datos

```bash
# 1. Ejecutar esquema principal
psql -f database/schema.sql

# 2. Ejecutar esquema de dietas
psql -f database/diet_schema.sql

# 3. Insertar alimentos comunes
python scripts/insert_common_foods.py
```

### Pruebas del Sistema

```bash
# Ejecutar pruebas completas
python test_nutrition_system.py

# Verificar detección de mensajes
python -c "from test_nutrition_system import test_can_handle; test_can_handle()"
```

## Próximas Mejoras

1. **Planificación Semanal** - Planes de 7 días con variedad
2. **Recetas Completas** - Base de datos de recetas con pasos detallados
3. **Lista de Compras** - Generación automática basada en plan semanal
4. **Análisis de Tendencias** - Progreso semanal y mensual
5. **Integración con Fotos** - Reconocimiento de alimentos por imagen
6. **Notificaciones Proactivas** - Recordatorios de comidas y agua

## Soporte Técnico

- **Logs detallados** en todas las operaciones
- **Manejo de errores** con mensajes informativos al usuario
- **Validación de datos** en todos los endpoints
- **Backup automático** de datos nutricionales
- **Monitoreo de performance** en consultas complejas

El sistema de nutrición está diseñado para ser escalable, preciso y fácil de usar, proporcionando a los usuarios todas las herramientas necesarias para el éxito en sus objetivos de salud y nutrición.

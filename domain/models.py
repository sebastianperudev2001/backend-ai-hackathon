"""
Modelos de dominio para el Fitness Bot de WhatsApp
Contiene todas las estructuras de datos utilizadas en la aplicación
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
from decimal import Decimal
import uuid


class MessageType(str, Enum):
    """Tipos de mensajes soportados por WhatsApp"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    REACTION = "reaction"
    STICKER = "sticker"


class WhatsAppTextMessage(BaseModel):
    """Estructura para mensajes de texto de WhatsApp"""
    body: str


class WhatsAppOutgoingMessage(BaseModel):
    """Mensaje saliente para enviar por WhatsApp"""
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: Dict[str, str]


class WhatsAppIncomingMessage(BaseModel):
    """Mensaje entrante de WhatsApp"""
    from_number: str = Field(alias="from")
    id: str
    type: MessageType
    timestamp: Optional[str] = None
    text: Optional[WhatsAppTextMessage] = None
    
    class Config:
        populate_by_name = True  # Actualizado para Pydantic v2


class WebhookEntry(BaseModel):
    """Estructura de entrada del webhook"""
    id: str
    changes: List[Dict[str, Any]]


class WebhookData(BaseModel):
    """Datos completos del webhook"""
    object: str
    entry: List[WebhookEntry]


class MessageResponse(BaseModel):
    """Respuesta después de procesar un mensaje"""
    success: bool
    message_id: Optional[str] = None
    response_text: Optional[str] = None
    error: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Respuesta del health check"""
    status: str
    service: str
    timestamp: datetime
    environment: Optional[str] = None


class ApiResponse(BaseModel):
    """Respuesta genérica de la API"""
    status: str
    message: str
    data: Optional[Any] = None


# ==================== MODELOS DE FITNESS ====================

class ExerciseCategory(str, Enum):
    """Categorías de ejercicios"""
    FUERZA = "fuerza"
    CARDIO = "cardio"
    FLEXIBILIDAD = "flexibilidad"


class DifficultyLevel(str, Enum):
    """Niveles de dificultad"""
    PRINCIPIANTE = "principiante"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"


class WeightUnit(str, Enum):
    """Unidades de peso"""
    KG = "kg"
    LBS = "lbs"


class Gender(str, Enum):
    """Géneros"""
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"


class FitnessGoal(str, Enum):
    """Objetivos de fitness"""
    PERDER_PESO = "perder_peso"
    GANAR_MUSCULO = "ganar_musculo"
    MEJORAR_RESISTENCIA = "mejorar_resistencia"
    TONIFICAR = "tonificar"
    MANTENER_FORMA = "mantener_forma"
    REHABILITACION = "rehabilitacion"


class User(BaseModel):
    """Modelo para usuarios"""
    id: Optional[str] = None
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    fitness_level: DifficultyLevel = DifficultyLevel.PRINCIPIANTE
    goals: List[FitnessGoal] = []
    medical_conditions: List[str] = []
    preferences: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None


class Exercise(BaseModel):
    """Modelo para ejercicios"""
    id: Optional[str] = None
    name: str
    category: ExerciseCategory
    muscle_groups: List[str]
    equipment: Optional[str] = None
    instructions: Optional[str] = None
    difficulty_level: DifficultyLevel
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Workout(BaseModel):
    """Modelo para rutinas de ejercicio"""
    id: Optional[str] = None
    user_id: str  # UUID del usuario
    name: str
    description: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    total_sets: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkoutSet(BaseModel):
    """Modelo para series de ejercicios"""
    id: Optional[str] = None
    workout_id: str
    exercise_id: str
    set_number: int
    weight: Optional[Decimal] = None
    weight_unit: WeightUnit = WeightUnit.KG
    repetitions: Optional[int] = None
    duration_seconds: Optional[int] = None
    distance_meters: Optional[Decimal] = None
    rest_seconds: Optional[int] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ==================== DTOs PARA REQUESTS ====================

class CreateUserRequest(BaseModel):
    """Request para crear un usuario"""
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    fitness_level: DifficultyLevel = DifficultyLevel.PRINCIPIANTE
    goals: List[FitnessGoal] = []
    medical_conditions: List[str] = []
    preferences: Optional[Dict[str, Any]] = None


class UpdateUserRequest(BaseModel):
    """Request para actualizar un usuario"""
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    fitness_level: Optional[DifficultyLevel] = None
    goals: Optional[List[FitnessGoal]] = None
    medical_conditions: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None


class StartWorkoutRequest(BaseModel):
    """Request para iniciar una rutina"""
    user_id: str  # UUID del usuario
    name: str
    description: Optional[str] = None


class EndWorkoutRequest(BaseModel):
    """Request para finalizar una rutina"""
    workout_id: str
    notes: Optional[str] = None


class AddSetRequest(BaseModel):
    """Request para agregar una serie"""
    workout_id: str
    exercise_name: str  # Nombre del ejercicio (se buscará en la BD)
    set_number: int
    weight: Optional[float] = None
    weight_unit: WeightUnit = WeightUnit.KG
    repetitions: Optional[int] = None
    duration_seconds: Optional[int] = None
    distance_meters: Optional[float] = None
    rest_seconds: Optional[int] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


# ==================== RESPONSES ====================

class UserResponse(BaseModel):
    """Respuesta con información de usuario"""
    success: bool
    user: Optional[User] = None
    message: str
    error: Optional[str] = None


class WorkoutResponse(BaseModel):
    """Respuesta con información de rutina"""
    success: bool
    workout: Optional[Workout] = None
    message: str
    error: Optional[str] = None


class SetResponse(BaseModel):
    """Respuesta al agregar una serie"""
    success: bool
    workout_set: Optional[WorkoutSet] = None
    message: str
    error: Optional[str] = None


class WorkoutSummaryResponse(BaseModel):
    """Resumen de una rutina completada"""
    workout: Workout
    total_sets: int
    exercises_performed: List[str]
    duration_minutes: Optional[int]
    average_difficulty: Optional[float]


# ==================== MODELOS DE NUTRICIÓN Y DIETAS ====================

class FoodCategory(str, Enum):
    """Categorías de alimentos"""
    PROTEINAS = "proteinas"
    CARBOHIDRATOS = "carbohidratos"
    GRASAS = "grasas"
    VERDURAS = "verduras"
    FRUTAS = "frutas"
    LACTEOS = "lacteos"
    LEGUMBRES = "legumbres"
    GRANOS = "granos"
    CONDIMENTOS = "condimentos"


class DietPlanType(str, Enum):
    """Tipos de planes de dieta"""
    PERDIDA_PESO = "perdida_peso"
    GANANCIA_MUSCULO = "ganancia_musculo"
    MANTENIMIENTO = "mantenimiento"
    DEFINICION = "definicion"


class MealType(str, Enum):
    """Tipos de comidas"""
    DESAYUNO = "desayuno"
    COLACION_1 = "colacion_1"
    ALMUERZO = "almuerzo"
    COLACION_2 = "colacion_2"
    CENA = "cena"


class Food(BaseModel):
    """Modelo para alimentos"""
    id: Optional[str] = None
    name: str
    name_es: str
    category: FoodCategory
    
    # Macronutrientes por 100g
    calories_per_100g: Decimal
    protein_per_100g: Decimal = Decimal('0')
    carbs_per_100g: Decimal = Decimal('0')
    fat_per_100g: Decimal = Decimal('0')
    fiber_per_100g: Decimal = Decimal('0')
    sugar_per_100g: Decimal = Decimal('0')
    
    # Micronutrientes por 100g (opcionales)
    sodium_mg_per_100g: Optional[Decimal] = Decimal('0')
    potassium_mg_per_100g: Optional[Decimal] = Decimal('0')
    calcium_mg_per_100g: Optional[Decimal] = Decimal('0')
    iron_mg_per_100g: Optional[Decimal] = Decimal('0')
    vitamin_c_mg_per_100g: Optional[Decimal] = Decimal('0')
    
    # Información adicional
    glycemic_index: Optional[int] = None
    common_serving_size_g: Optional[Decimal] = None
    serving_description: Optional[str] = None
    
    # Flags dietéticos
    is_vegetarian: bool = True
    is_vegan: bool = False
    is_gluten_free: bool = True
    is_dairy_free: bool = True
    is_low_carb: bool = False
    is_high_protein: bool = False
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DietPlan(BaseModel):
    """Modelo para planes de dieta"""
    id: Optional[str] = None
    user_id: str
    name: str
    description: Optional[str] = None
    plan_type: DietPlanType
    
    # Objetivos nutricionales diarios
    target_calories: int
    target_protein_g: Decimal
    target_carbs_g: Decimal
    target_fat_g: Decimal
    target_fiber_g: Decimal = Decimal('25')
    
    # Configuración de comidas
    meals_per_day: int = 5
    breakfast_calories_percent: Decimal = Decimal('25.00')
    lunch_calories_percent: Decimal = Decimal('30.00')
    dinner_calories_percent: Decimal = Decimal('25.00')
    snack1_calories_percent: Decimal = Decimal('10.00')
    snack2_calories_percent: Decimal = Decimal('10.00')
    
    # Configuración de horarios
    breakfast_time: str = "07:00"  # Formato HH:MM
    snack1_time: str = "10:00"
    lunch_time: str = "13:00"
    snack2_time: str = "16:00"
    dinner_time: str = "19:00"
    
    # Restricciones alimentarias
    dietary_restrictions: List[str] = []
    food_allergies: List[str] = []
    disliked_foods: List[str] = []
    
    # Control de estado
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_agent: str = "nutrition_agent"


class PlannedMeal(BaseModel):
    """Modelo para comidas planificadas"""
    id: Optional[str] = None
    diet_plan_id: str
    meal_type: MealType
    meal_name: str
    meal_time: str  # Formato HH:MM
    
    # Objetivos nutricionales de la comida
    target_calories: int
    target_protein_g: Decimal
    target_carbs_g: Decimal
    target_fat_g: Decimal
    
    # Receta/instrucciones
    preparation_instructions: Optional[str] = None
    cooking_time_minutes: Optional[int] = None
    difficulty_level: str = "facil"  # 'facil', 'medio', 'dificil'
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlannedMealIngredient(BaseModel):
    """Modelo para ingredientes de comidas planificadas"""
    id: Optional[str] = None
    planned_meal_id: str
    food_id: str
    
    # Cantidad del ingrediente
    quantity_grams: Decimal
    
    # Valores nutricionales calculados para esta cantidad
    calories: Decimal
    protein_g: Decimal
    carbs_g: Decimal
    fat_g: Decimal
    
    # Notas sobre el ingrediente
    notes: Optional[str] = None
    is_optional: bool = False
    
    created_at: Optional[datetime] = None


class ConsumedMeal(BaseModel):
    """Modelo para comidas consumidas"""
    id: Optional[str] = None
    user_id: str
    diet_plan_id: Optional[str] = None
    planned_meal_id: Optional[str] = None
    
    # Información de la comida consumida
    meal_type: MealType
    meal_name: str
    consumed_at: datetime
    consumption_date: datetime
    
    # Valores nutricionales totales consumidos
    total_calories: Decimal = Decimal('0')
    total_protein_g: Decimal = Decimal('0')
    total_carbs_g: Decimal = Decimal('0')
    total_fat_g: Decimal = Decimal('0')
    total_fiber_g: Decimal = Decimal('0')
    
    # Estado y notas
    adherence_score: Decimal = Decimal('1.0')  # 0.0 - 1.0
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 estrellas
    notes: Optional[str] = None
    
    created_at: Optional[datetime] = None


class ConsumedMealIngredient(BaseModel):
    """Modelo para ingredientes consumidos"""
    id: Optional[str] = None
    consumed_meal_id: str
    food_id: str
    
    # Cantidad consumida
    quantity_grams: Decimal
    
    # Valores nutricionales para esta cantidad
    calories: Decimal
    protein_g: Decimal
    carbs_g: Decimal
    fat_g: Decimal
    
    # Información adicional
    was_planned: bool = False
    substitution_for_food_id: Optional[str] = None
    notes: Optional[str] = None
    
    created_at: Optional[datetime] = None


class DailyNutritionSummary(BaseModel):
    """Modelo para resumen nutricional diario"""
    id: Optional[str] = None
    user_id: str
    diet_plan_id: Optional[str] = None
    summary_date: datetime
    
    # Objetivos del día
    target_calories: int
    target_protein_g: Decimal
    target_carbs_g: Decimal
    target_fat_g: Decimal
    
    # Consumo real del día
    consumed_calories: Decimal = Decimal('0')
    consumed_protein_g: Decimal = Decimal('0')
    consumed_carbs_g: Decimal = Decimal('0')
    consumed_fat_g: Decimal = Decimal('0')
    consumed_fiber_g: Decimal = Decimal('0')
    
    # Análisis
    calorie_deficit_surplus: Decimal = Decimal('0')  # Negativo = déficit, Positivo = superávit
    adherence_percentage: Decimal = Decimal('0')  # Porcentaje de adherencia al plan
    meals_completed: int = 0
    meals_planned: int = 0
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FoodSubstitution(BaseModel):
    """Modelo para sustituciones de alimentos"""
    id: Optional[str] = None
    original_food_id: str
    substitute_food_id: str
    conversion_factor: Decimal = Decimal('1.0000')
    substitution_type: str  # 'equivalent', 'similar_macros', 'similar_calories', 'dietary_restriction'
    notes: Optional[str] = None
    confidence_score: Decimal = Decimal('1.0')  # 0.0 - 1.0
    created_at: Optional[datetime] = None


# ==================== DTOs PARA REQUESTS DE DIETAS ====================

class CreateDietPlanRequest(BaseModel):
    """Request para crear un plan de dieta"""
    user_id: str
    name: str
    description: Optional[str] = None
    plan_type: DietPlanType
    target_calories: int
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float
    dietary_restrictions: List[str] = []
    food_allergies: List[str] = []
    disliked_foods: List[str] = []


class LogMealRequest(BaseModel):
    """Request para registrar una comida consumida"""
    user_id: str
    meal_type: MealType
    meal_name: str
    ingredients: List[Dict[str, Any]]  # Lista de {food_id, quantity_grams}
    notes: Optional[str] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)


class GetTodayMealsRequest(BaseModel):
    """Request para obtener comidas del día"""
    user_id: str
    date: Optional[datetime] = None


class GetNextMealRequest(BaseModel):
    """Request para obtener la siguiente comida"""
    user_id: str


class AdjustDietRequest(BaseModel):
    """Request para ajustar la dieta"""
    user_id: str
    meal_type: MealType
    food_changes: List[Dict[str, Any]]  # Lista de cambios: {action: 'add'/'remove'/'substitute', food_id, quantity, substitute_food_id}
    maintain_calories: bool = True


# ==================== RESPONSES DE DIETAS ====================

class DietPlanResponse(BaseModel):
    """Respuesta con información de plan de dieta"""
    success: bool
    diet_plan: Optional[DietPlan] = None
    message: str
    error: Optional[str] = None


class TodayMealsResponse(BaseModel):
    """Respuesta con comidas del día"""
    success: bool
    planned_meals: List[PlannedMeal] = []
    consumed_meals: List[ConsumedMeal] = []
    nutrition_summary: Optional[DailyNutritionSummary] = None
    message: str
    error: Optional[str] = None


class NextMealResponse(BaseModel):
    """Respuesta con la siguiente comida"""
    success: bool
    next_meal: Optional[PlannedMeal] = None
    time_until_next_meal_minutes: Optional[int] = None
    message: str
    error: Optional[str] = None


class DietAdjustmentResponse(BaseModel):
    """Respuesta de ajuste de dieta"""
    success: bool
    adjusted_meal: Optional[PlannedMeal] = None
    nutrition_impact: Optional[Dict[str, Any]] = None
    suggested_changes: List[str] = []
    message: str
    error: Optional[str] = None


class NutritionAnalysisResponse(BaseModel):
    """Respuesta con análisis nutricional"""
    success: bool
    daily_summary: Optional[DailyNutritionSummary] = None
    recommendations: List[str] = []
    calorie_deficit_status: str  # 'on_track', 'over', 'under'
    macro_balance_score: Optional[float] = None  # 0.0 - 1.0
    message: str
    error: Optional[str] = None


# ==================== MODELOS DE MEMORIA/CONVERSACIÓN ====================

class ConversationMessageType(str, Enum):
    """Tipos de mensajes en la conversación"""
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    FUNCTION = "function"


class ConversationSession(BaseModel):
    """Modelo para sesiones de conversación"""
    id: Optional[str] = None
    user_id: str
    session_name: Optional[str] = None
    started_at: datetime
    last_activity_at: datetime
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationMessage(BaseModel):
    """Modelo para mensajes de conversación"""
    id: Optional[str] = None
    session_id: str
    message_type: ConversationMessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    agent_name: Optional[str] = None
    token_count: Optional[int] = None
    created_at: Optional[datetime] = None


class CreateSessionRequest(BaseModel):
    """Request para crear una sesión de conversación"""
    user_id: str
    session_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AddMessageRequest(BaseModel):
    """Request para agregar un mensaje a la conversación"""
    session_id: str
    message_type: ConversationMessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    agent_name: Optional[str] = None
    token_count: Optional[int] = None


class ConversationHistoryResponse(BaseModel):
    """Respuesta con historial de conversación"""
    success: bool
    session: Optional[ConversationSession] = None
    messages: List[ConversationMessage] = []
    total_messages: int = 0
    message: str
    error: Optional[str] = None


class SessionResponse(BaseModel):
    """Respuesta con información de sesión"""
    success: bool
    session: Optional[ConversationSession] = None
    message: str
    error: Optional[str] = None

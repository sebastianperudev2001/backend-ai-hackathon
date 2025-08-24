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

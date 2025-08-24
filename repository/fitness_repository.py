"""
Repositorio para operaciones de fitness con Supabase
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from domain.models import (
    User, Workout, Exercise, WorkoutSet, 
    ExerciseCategory, DifficultyLevel, WeightUnit,
    CreateUserRequest, UpdateUserRequest,
    StartWorkoutRequest, EndWorkoutRequest, AddSetRequest,
    UserResponse, WorkoutResponse, SetResponse, WorkoutSummaryResponse
)
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class FitnessRepository:
    """
    Repositorio para operaciones de fitness
    """
    
    def __init__(self):
        self.supabase_client = get_supabase_client()
    
    def _sanitize_user_data(self, user_data: dict) -> dict:
        """
        Sanitiza los datos del usuario para manejar campos None que deben ser listas
        """
        sanitized_data = user_data.copy()
        if sanitized_data.get('medical_conditions') is None:
            sanitized_data['medical_conditions'] = []
        if sanitized_data.get('goals') is None:
            sanitized_data['goals'] = []
        return sanitized_data
    
    # ==================== MÉTODOS DE USUARIOS ====================
    
    async def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """
        Obtener usuario por número de teléfono
        """
        try:
            if not self.supabase_client.is_connected():
                return None
            
            result = self.supabase_client.client.table("users").select("*").eq("phone_number", phone_number).single().execute()
            print('result', result)
            
            if result.data:
                # Sanitizar datos del usuario para manejar campos None
                user_data = self._sanitize_user_data(result.data)
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por teléfono: {str(e)}")
            return None
    
    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """
        Crear un nuevo usuario
        """
        try:
            if not self.supabase_client.is_connected():
                return UserResponse(
                    success=False,
                    message="Error de conexión con la base de datos",
                    error="Supabase no está conectado"
                )
            
            # Verificar si el usuario ya existe
            existing_user = await self.get_user_by_phone(request.phone_number)
            if existing_user:
                return UserResponse(
                    success=False,
                    message="El usuario ya existe",
                    error="Phone number already registered"
                )
            
            # Crear nuevo usuario
            user_data = {
                "phone_number": request.phone_number,
                "name": request.name,
                "email": request.email,
                "age": request.age,
                "gender": request.gender.value if request.gender else None,
                "height_cm": request.height_cm,
                "weight_kg": float(request.weight_kg) if request.weight_kg else None,
                "fitness_level": request.fitness_level.value,
                "goals": [goal.value for goal in request.goals],
                "medical_conditions": request.medical_conditions,
                "preferences": request.preferences
            }
            
            result = self.supabase_client.client.table("users").insert(user_data).execute()
            
            if result.data:
                # Sanitizar datos del usuario para manejar campos None
                user_data = self._sanitize_user_data(result.data[0])
                user = User(**user_data)
                logger.info(f"✅ Usuario creado: {user.id} - {user.phone_number}")
                return UserResponse(
                    success=True,
                    user=user,
                    message=f"Usuario '{user.name or user.phone_number}' creado correctamente 👤"
                )
            else:
                return UserResponse(
                    success=False,
                    message="Error al crear el usuario",
                    error="No se pudo insertar en la base de datos"
                )
                
        except Exception as e:
            logger.error(f"❌ Error creando usuario: {str(e)}")
            return UserResponse(
                success=False,
                message="Error interno al crear usuario",
                error=str(e)
            )
    
    async def get_or_create_user(self, phone_number: str, name: Optional[str] = None) -> Optional[User]:
        """
        Obtener usuario existente o crear uno nuevo si no existe
        """
        try:
            # Intentar obtener usuario existente
            user = await self.get_user_by_phone(phone_number)
            if user:
                logger.info(f"🔍 Usuario existente encontrado: {user.id} para teléfono {phone_number}")
                # Actualizar última actividad
                await self.update_user_activity(user.id)
                return user
            
            # Crear nuevo usuario si no existe
            create_request = CreateUserRequest(
                phone_number=phone_number,
                name=name or "Usuario"
            )
            
            response = await self.create_user(create_request)
            if response.success:
                logger.info(f"🔍 Nuevo usuario creado: {response.user.id} para teléfono {phone_number}")
                return response.user
            
            logger.warning(f"⚠️ No se pudo crear usuario para {phone_number}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en get_or_create_user: {str(e)}")
            return None
    
    async def update_user_activity(self, user_id: str) -> bool:
        """
        Actualizar la última actividad del usuario
        """
        try:
            if not self.supabase_client.is_connected():
                return False
            
            result = self.supabase_client.client.table("users").update({
                "last_activity_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"❌ Error actualizando actividad de usuario: {str(e)}")
            return False
    
    # ==================== MÉTODOS DE RUTINAS (ACTUALIZADOS) ====================
    
    async def start_workout(self, request: StartWorkoutRequest) -> WorkoutResponse:
        """
        Iniciar una nueva rutina de ejercicio
        """
        try:
            if not self.supabase_client.is_connected():
                return WorkoutResponse(
                    success=False,
                    message="Error de conexión con la base de datos",
                    error="Supabase no está conectado"
                )
            
            # Establecer contexto de usuario para RLS
            logger.info(f"🔍 Intentando establecer contexto para user_id: {request.user_id}")
            context_set = self.supabase_client.set_user_context(request.user_id)
            if not context_set:
                logger.warning(f"⚠️ No se pudo establecer contexto de usuario para {request.user_id}")
                return WorkoutResponse(
                    success=False,
                    message="Error de configuración de seguridad",
                    error="No se pudo establecer el contexto de usuario. Verifica la configuración de RLS en Supabase."
                )
            else:
                logger.info(f"✅ Contexto establecido correctamente para user_id: {request.user_id}")
            
            # Crear nuevo workout
            workout_data = {
                "user_id": request.user_id,
                "name": request.name,
                "description": request.description,
                "started_at": datetime.now().isoformat(),
                "total_sets": 0
            }
            
            try:
                result = self.supabase_client.client.table("workouts").insert(workout_data).execute()
            except Exception as db_error:
                error_msg = str(db_error)
                logger.error(f"❌ Error de base de datos al crear workout: {error_msg}")
                
                # Mensajes de error más amigables
                if "row-level security policy" in error_msg.lower():
                    return WorkoutResponse(
                        success=False,
                        message="Error de permisos al crear la rutina",
                        error="Las políticas de seguridad impidieron crear la rutina. Verifica la configuración de RLS."
                    )
                elif "violates foreign key constraint" in error_msg.lower():
                    return WorkoutResponse(
                        success=False,
                        message="Error: Usuario no válido",
                        error="El usuario especificado no existe en la base de datos."
                    )
                else:
                    return WorkoutResponse(
                        success=False,
                        message="Error técnico al crear la rutina",
                        error=f"Error de base de datos: {error_msg[:100]}..."
                    )
            
            if result.data:
                workout = Workout(**result.data[0])
                logger.info(f"✅ Rutina iniciada: {workout.id} para usuario {request.user_id}")
                return WorkoutResponse(
                    success=True,
                    workout=workout,
                    message=f"Rutina '{workout.name}' iniciada correctamente 💪"
                )
            else:
                return WorkoutResponse(
                    success=False,
                    message="Error al crear la rutina",
                    error="No se pudo insertar en la base de datos"
                )
                
        except Exception as e:
            logger.error(f"❌ Error iniciando rutina: {str(e)}")
            return WorkoutResponse(
                success=False,
                message="Error interno al iniciar rutina",
                error=str(e)
            )
    
    async def end_workout(self, request: EndWorkoutRequest) -> WorkoutResponse:
        """
        Finalizar una rutina de ejercicio
        """
        try:
            if not self.supabase_client.is_connected():
                return WorkoutResponse(
                    success=False,
                    message="Error de conexión con la base de datos",
                    error="Supabase no está conectado"
                )
            
            # Actualizar workout con tiempo de finalización
            update_data = {
                "ended_at": datetime.now().isoformat(),
                "notes": request.notes
            }
            
            result = self.supabase_client.client.table("workouts").update(update_data).eq("id", request.workout_id).execute()
            
            if result.data:
                workout = Workout(**result.data[0])
                logger.info(f"✅ Rutina finalizada: {workout.id}")
                return WorkoutResponse(
                    success=True,
                    workout=workout,
                    message=f"¡Rutina completada! 🎉 Duración: {workout.duration_minutes or 0} minutos"
                )
            else:
                return WorkoutResponse(
                    success=False,
                    message="Error al finalizar la rutina",
                    error="Rutina no encontrada"
                )
                
        except Exception as e:
            logger.error(f"❌ Error finalizando rutina: {str(e)}")
            return WorkoutResponse(
                success=False,
                message="Error interno al finalizar rutina",
                error=str(e)
            )
    
    async def add_set(self, request: AddSetRequest) -> SetResponse:
        """
        Agregar una serie a una rutina
        """
        try:
            if not self.supabase_client.is_connected():
                return SetResponse(
                    success=False,
                    message="Error de conexión con la base de datos",
                    error="Supabase no está conectado"
                )
            
            # Buscar el ejercicio por nombre
            exercise = await self.get_exercise_by_name(request.exercise_name)
            if not exercise:
                return SetResponse(
                    success=False,
                    message=f"Ejercicio '{request.exercise_name}' no encontrado",
                    error="Ejercicio no existe en la base de datos"
                )
            
            # Crear la serie
            set_data = {
                "workout_id": request.workout_id,
                "exercise_id": exercise.id,
                "set_number": request.set_number,
                "weight": float(request.weight) if request.weight else None,
                "weight_unit": request.weight_unit.value,
                "repetitions": request.repetitions,
                "duration_seconds": request.duration_seconds,
                "distance_meters": float(request.distance_meters) if request.distance_meters else None,
                "rest_seconds": request.rest_seconds,
                "difficulty_rating": request.difficulty_rating,
                "notes": request.notes,
                "completed_at": datetime.now().isoformat()
            }
            
            result = self.supabase_client.client.table("workout_sets").insert(set_data).execute()
            
            if result.data:
                workout_set = WorkoutSet(**result.data[0])
                logger.info(f"✅ Serie agregada: {workout_set.id} - {exercise.name}")
                
                # Formatear mensaje de respuesta
                message_parts = [f"Serie {request.set_number} de {exercise.name} registrada 📝"]
                if request.weight and request.repetitions:
                    message_parts.append(f"💪 {request.weight}{request.weight_unit.value} x {request.repetitions} reps")
                elif request.repetitions:
                    message_parts.append(f"💪 {request.repetitions} repeticiones")
                elif request.duration_seconds:
                    message_parts.append(f"⏱️ {request.duration_seconds} segundos")
                
                return SetResponse(
                    success=True,
                    workout_set=workout_set,
                    message=" - ".join(message_parts)
                )
            else:
                return SetResponse(
                    success=False,
                    message="Error al registrar la serie",
                    error="No se pudo insertar en la base de datos"
                )
                
        except Exception as e:
            logger.error(f"❌ Error agregando serie: {str(e)}")
            return SetResponse(
                success=False,
                message="Error interno al registrar serie",
                error=str(e)
            )
    
    async def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """
        Buscar ejercicio por nombre (case-insensitive)
        """
        try:
            if not self.supabase_client.is_connected():
                return None
            
            result = self.supabase_client.client.table("exercises").select("*").ilike("name", f"%{name}%").limit(1).execute()
            
            if result.data:
                return Exercise(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ Error buscando ejercicio: {str(e)}")
            return None
    
    async def get_active_workout(self, phone_number: str) -> Optional[Workout]:
        """
        Obtener la rutina activa (sin finalizar) de un usuario por teléfono
        """
        try:
            if not self.supabase_client.is_connected():
                return None
            
            # Obtener usuario por teléfono
            user = await self.get_user_by_phone(phone_number)
            if not user:
                return None
            
            # Establecer contexto de usuario para RLS
            context_set = self.supabase_client.set_user_context(user.id)
            if not context_set:
                logger.warning(f"⚠️ No se pudo establecer contexto de usuario para {user.id}")
                logger.warning("   Las políticas RLS pueden fallar. Verifica que la función set_config exista.")
            
            result = self.supabase_client.client.table("workouts").select("*").eq("user_id", user.id).is_("ended_at", "null").order("started_at", desc=True).limit(1).execute()
            
            if result.data:
                return Workout(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo rutina activa: {str(e)}")
            return None
    
    async def get_workout_summary(self, workout_id: str) -> Optional[WorkoutSummaryResponse]:
        """
        Obtener resumen completo de una rutina
        """
        try:
            if not self.supabase_client.is_connected():
                return None
            
            # Obtener workout
            workout_result = self.supabase_client.client.table("workouts").select("*").eq("id", workout_id).single().execute()
            
            if not workout_result.data:
                return None
            
            workout = Workout(**workout_result.data)
            
            # Obtener series con información de ejercicios
            sets_result = self.supabase_client.client.table("workout_sets").select("""
                *,
                exercises (
                    name
                )
            """).eq("workout_id", workout_id).execute()
            
            exercises_performed = []
            total_sets = len(sets_result.data) if sets_result.data else 0
            difficulties = []
            
            if sets_result.data:
                for set_data in sets_result.data:
                    exercise_name = set_data.get("exercises", {}).get("name", "Desconocido")
                    if exercise_name not in exercises_performed:
                        exercises_performed.append(exercise_name)
                    
                    if set_data.get("difficulty_rating"):
                        difficulties.append(set_data["difficulty_rating"])
            
            average_difficulty = sum(difficulties) / len(difficulties) if difficulties else None
            
            return WorkoutSummaryResponse(
                workout=workout,
                total_sets=total_sets,
                exercises_performed=exercises_performed,
                duration_minutes=workout.duration_minutes,
                average_difficulty=average_difficulty
            )
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen de rutina: {str(e)}")
            return None
    
    async def get_available_exercises(self, category: Optional[ExerciseCategory] = None, difficulty: Optional[DifficultyLevel] = None) -> List[Exercise]:
        """
        Obtener lista de ejercicios disponibles
        """
        try:
            if not self.supabase_client.is_connected():
                return []
            
            query = self.supabase_client.client.table("exercises").select("*")
            
            if category:
                query = query.eq("category", category.value)
            
            if difficulty:
                query = query.eq("difficulty_level", difficulty.value)
            
            result = query.order("name").execute()
            
            if result.data:
                return [Exercise(**exercise_data) for exercise_data in result.data]
            return []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo ejercicios: {str(e)}")
            return []

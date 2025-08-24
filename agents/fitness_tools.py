"""
Herramientas (tools) para el FitnessAgent
Integración con Supabase para registrar rutinas y series
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from domain.models import (
    StartWorkoutRequest, EndWorkoutRequest, AddSetRequest,
    WeightUnit, ExerciseCategory, DifficultyLevel
)
from repository.fitness_repository import FitnessRepository

logger = logging.getLogger(__name__)


# ==================== SCHEMAS PARA TOOLS ====================

class StartWorkoutSchema(BaseModel):
    """Schema para iniciar rutina"""
    phone_number: str = Field(description="Número de teléfono del usuario")
    name: str = Field(description="Nombre de la rutina")
    description: Optional[str] = Field(default=None, description="Descripción opcional de la rutina")


class EndWorkoutSchema(BaseModel):
    """Schema para finalizar rutina"""
    workout_id: Optional[str] = Field(default=None, description="ID de la rutina a finalizar (opcional si se proporciona phone_number)")
    phone_number: Optional[str] = Field(default=None, description="Número de teléfono del usuario para finalizar rutina activa")
    notes: Optional[str] = Field(default=None, description="Notas finales de la rutina")


class AddSetSchema(BaseModel):
    """Schema para agregar serie"""
    workout_id: Optional[str] = Field(default=None, description="ID de la rutina (opcional si se proporciona phone_number)")
    phone_number: Optional[str] = Field(default=None, description="Número de teléfono del usuario para obtener rutina activa")
    exercise_name: str = Field(description="Nombre del ejercicio")
    set_number: int = Field(description="Número de serie")
    weight: Optional[float] = Field(default=None, description="Peso utilizado")
    weight_unit: str = Field(default="kg", description="Unidad de peso (kg o lbs)")
    repetitions: Optional[int] = Field(default=None, description="Número de repeticiones")
    duration_seconds: Optional[int] = Field(default=None, description="Duración en segundos")
    distance_meters: Optional[float] = Field(default=None, description="Distancia en metros")
    rest_seconds: Optional[int] = Field(default=None, description="Tiempo de descanso en segundos")
    difficulty_rating: Optional[int] = Field(default=None, description="Dificultad percibida (1-10)")
    notes: Optional[str] = Field(default=None, description="Notas de la serie")


class GetActiveWorkoutSchema(BaseModel):
    """Schema para obtener rutina activa"""
    phone_number: str = Field(description="Número de teléfono del usuario")


class GetExercisesSchema(BaseModel):
    """Schema para obtener ejercicios"""
    category: Optional[str] = Field(default=None, description="Categoría: fuerza, cardio, flexibilidad")
    difficulty: Optional[str] = Field(default=None, description="Dificultad: principiante, intermedio, avanzado")


class EndActiveWorkoutSchema(BaseModel):
    """Schema para finalizar rutina activa por teléfono"""
    phone_number: str = Field(description="Número de teléfono del usuario")
    notes: Optional[str] = Field(default=None, description="Notas finales de la rutina")


class AddSetSimpleSchema(BaseModel):
    """Schema simplificado para agregar serie usando phone_number"""
    phone_number: str = Field(description="Número de teléfono del usuario")
    exercise: str = Field(description="Nombre del ejercicio (ej: Sentadillas, Flexiones)")
    reps: Optional[int] = Field(default=None, description="Número de repeticiones")
    weight: Optional[float] = Field(default=None, description="Peso utilizado en kg")
    sets: Optional[int] = Field(default=1, description="Número de serie (por defecto 1)")
    notes: Optional[str] = Field(default=None, description="Notas adicionales")


# ==================== TOOLS ====================

class StartWorkoutTool(BaseTool):
    """Tool para iniciar una rutina de ejercicio"""
    name: str = "start_workout"
    description: str = """
    Inicia una nueva rutina de ejercicio para un usuario usando su número de teléfono.
    Registra el momento de inicio y crea un registro en la base de datos.
    Úsala cuando el usuario quiera comenzar una sesión de entrenamiento.
    Parámetros: phone_number, name (nombre de la rutina), description (opcional)
    """
    args_schema: type = StartWorkoutSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, phone_number: str, name: str, description: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(phone_number, name, description))
    
    async def _arun(self, phone_number: str, name: str, description: Optional[str] = None) -> str:
        """Iniciar rutina de ejercicio"""
        try:
            # Obtener o crear usuario
            user = await self.fitness_repo.get_or_create_user(phone_number)
            if not user:
                return "❌ Lo siento, no pude acceder a tu información de usuario en este momento. Por favor, intenta nuevamente."
            
            request = StartWorkoutRequest(
                user_id=user.id,
                name=name,
                description=description
            )
            
            response = await self.fitness_repo.start_workout(request)
            
            if response.success:
                workout_info = f"""
🏋️ ¡Rutina iniciada exitosamente!

📝 **Rutina:** {response.workout.name}
🆔 **ID:** {response.workout.id}
⏰ **Iniciada:** {response.workout.started_at.strftime('%H:%M:%S')}
📋 **Descripción:** {response.workout.description or 'Sin descripción'}

¡Ahora puedes empezar a registrar tus series! 💪
                """
                return workout_info.strip()
            else:
                # Mensaje de error más amigable para el usuario
                if "configuración de seguridad" in response.message:
                    return f"""
❌ Lo siento, parece que hubo un error técnico al intentar iniciar la rutina. 

Por favor, intenta nuevamente en unos momentos. 

💡 **Mientras tanto, te sugiero que realices un calentamiento adecuado:**
• 5-10 minutos de caminata o trote suave
• 10 rotaciones de tobillos (cada pie)  
• 10 rotaciones de rodillas
• 10 rotaciones de caderas
• 10 rotaciones de hombros

¿Te gustaría intentar iniciar la rutina nuevamente?
                    """.strip()
                else:
                    return "❌ Lo siento, no pude iniciar tu rutina en este momento. Por favor, verifica que no tengas una rutina activa y intenta nuevamente."
                
        except Exception as e:
            logger.error(f"❌ Error en StartWorkoutTool: {str(e)}")
            return "❌ Lo siento, no pude iniciar la rutina en este momento. Por favor, intenta nuevamente."


class EndWorkoutTool(BaseTool):
    """Tool para finalizar una rutina de ejercicio"""
    name: str = "end_workout"
    description: str = """
    Finaliza una rutina de ejercicio activa del usuario.
    Si no se proporciona workout_id, finaliza automáticamente la rutina activa.
    Registra el momento de finalización y calcula la duración total.
    Usa esta herramienta cuando el usuario termine su sesión de entrenamiento.
    """
    args_schema: type = EndWorkoutSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, workout_id: str = None, phone_number: str = None, notes: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(workout_id, phone_number, notes))
    
    async def _arun(self, workout_id: str = None, phone_number: str = None, notes: Optional[str] = None) -> str:
        """Finalizar rutina de ejercicio"""
        try:
            # Si no se proporciona workout_id, buscar la rutina activa
            if not workout_id and phone_number:
                active_workout = await self.fitness_repo.get_active_workout(phone_number)
                if active_workout:
                    workout_id = active_workout.id
                    logger.info(f"✅ Rutina activa encontrada para finalizar: {workout_id}")
                else:
                    return "ℹ️ No hay rutinas activas para finalizar."
            
            if not workout_id:
                return "❌ No se pudo identificar qué rutina finalizar. Proporciona el ID de la rutina o tu número de teléfono."
            
            request = EndWorkoutRequest(
                workout_id=workout_id,
                notes=notes
            )
            
            response = await self.fitness_repo.end_workout(request)
            
            if response.success:
                # Obtener resumen de la rutina
                summary = await self.fitness_repo.get_workout_summary(workout_id)
                
                if summary:
                    summary_info = f"""
🎉 ¡Rutina completada exitosamente!

📝 **Rutina:** {summary.workout.name}
⏱️ **Duración:** {summary.duration_minutes or 0} minutos
📊 **Total de series:** {summary.total_sets}
🏋️ **Ejercicios realizados:** {', '.join(summary.exercises_performed)}
{f"⭐ **Dificultad promedio:** {summary.average_difficulty:.1f}/10" if summary.average_difficulty else ""}
{f"📝 **Notas:** {summary.workout.notes}" if summary.workout.notes else ""}

¡Excelente trabajo! 💪🔥
                    """
                    return summary_info.strip()
                else:
                    return f"✅ Rutina finalizada: {response.message}"
            else:
                return "❌ Lo siento, no pude finalizar tu rutina en este momento. Por favor, intenta nuevamente."
                
        except Exception as e:
            logger.error(f"❌ Error en EndWorkoutTool: {str(e)}")
            return "❌ Lo siento, no pude finalizar la rutina en este momento. Por favor, intenta nuevamente."


class AddSetTool(BaseTool):
    """Tool para agregar una serie a la rutina activa"""
    name: str = "add_set"
    description: str = """
    Registra una serie de ejercicio en la rutina activa.
    Incluye información como peso, repeticiones, duración, etc.
    Usa esta herramienta cada vez que el usuario complete una serie de un ejercicio.
    """
    args_schema: type = AddSetSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, workout_id: Optional[str] = None, phone_number: Optional[str] = None,
             exercise_name: str = None, set_number: int = 1, 
             weight: Optional[float] = None, weight_unit: str = "kg",
             repetitions: Optional[int] = None, duration_seconds: Optional[int] = None,
             distance_meters: Optional[float] = None, rest_seconds: Optional[int] = None,
             difficulty_rating: Optional[int] = None, notes: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(
            workout_id, phone_number, exercise_name, set_number, weight, weight_unit,
            repetitions, duration_seconds, distance_meters, rest_seconds,
            difficulty_rating, notes
        ))
    
    async def _arun(self, workout_id: Optional[str] = None, phone_number: Optional[str] = None,
                    exercise_name: str = None, set_number: int = 1,
                    weight: Optional[float] = None, weight_unit: str = "kg",
                    repetitions: Optional[int] = None, duration_seconds: Optional[int] = None,
                    distance_meters: Optional[float] = None, rest_seconds: Optional[int] = None,
                    difficulty_rating: Optional[int] = None, notes: Optional[str] = None) -> str:
        """Agregar serie a la rutina"""
        try:
            # Si no se proporciona workout_id, buscar la rutina activa
            if not workout_id and phone_number:
                active_workout = await self.fitness_repo.get_active_workout(phone_number)
                if active_workout:
                    workout_id = active_workout.id
                    logger.info(f"✅ Rutina activa encontrada para agregar serie: {workout_id}")
                else:
                    return "❌ No hay rutinas activas. Por favor, inicia una rutina primero usando start_workout."
            
            if not workout_id:
                return "❌ No se pudo identificar la rutina. Proporciona el workout_id o phone_number."
            
            if not exercise_name:
                return "❌ Debes especificar el nombre del ejercicio."
            
            # Validar unidad de peso
            try:
                weight_unit_enum = WeightUnit(weight_unit.lower())
            except ValueError:
                weight_unit_enum = WeightUnit.KG
            
            request = AddSetRequest(
                workout_id=workout_id,
                exercise_name=exercise_name,
                set_number=set_number,
                weight=weight,
                weight_unit=weight_unit_enum,
                repetitions=repetitions,
                duration_seconds=duration_seconds,
                distance_meters=distance_meters,
                rest_seconds=rest_seconds,
                difficulty_rating=difficulty_rating,
                notes=notes
            )
            
            response = await self.fitness_repo.add_set(request)
            
            if response.success:
                return f"✅ {response.message}"
            else:
                # Mostrar el mensaje específico del error
                error_message = response.message if response.message else "No pude registrar tu serie en este momento."
                return f"❌ {error_message}"
                
        except Exception as e:
            logger.error(f"❌ Error en AddSetTool: {str(e)}")
            return "❌ Lo siento, no pude registrar la serie en este momento. Por favor, intenta nuevamente."


class GetActiveWorkoutTool(BaseTool):
    """Tool para obtener la rutina activa del usuario"""
    name: str = "get_active_workout"
    description: str = """
    Obtiene la rutina de ejercicio activa (no finalizada) del usuario usando su número de teléfono.
    ÚSALA SIEMPRE antes de agregar series para verificar que hay una rutina activa.
    Muestra detalles como nombre, ID, duración, series registradas, etc.
    Parámetros: phone_number (ej: "+51998555878")
    """
    args_schema: type = GetActiveWorkoutSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, phone_number: str) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(phone_number))
    
    async def _arun(self, phone_number: str) -> str:
        """Obtener rutina activa"""
        try:
            workout = await self.fitness_repo.get_active_workout(phone_number)
            
            if workout:
                workout_info = f"""
🏋️ **Rutina activa encontrada:**

📝 **Nombre:** {workout.name}
🆔 **ID:** {workout.id}
⏰ **Iniciada:** {workout.started_at.strftime('%H:%M:%S del %d/%m/%Y')}
📊 **Series registradas:** {workout.total_sets}
📋 **Descripción:** {workout.description or 'Sin descripción'}
                """
                return workout_info.strip()
            else:
                return "ℹ️ No hay rutinas activas. Puedes iniciar una nueva rutina."
                
        except Exception as e:
            logger.error(f"❌ Error en GetActiveWorkoutTool: {str(e)}")
            return "❌ Lo siento, no pude verificar tu rutina activa en este momento. Por favor, intenta nuevamente."


class GetExercisesTool(BaseTool):
    """Tool para obtener lista de ejercicios disponibles"""
    name: str = "get_exercises"
    description: str = """
    Obtiene la lista de ejercicios disponibles en la base de datos.
    Puede filtrar por categoría (fuerza, cardio, flexibilidad) y dificultad.
    Útil para sugerir ejercicios al usuario.
    """
    args_schema: type = GetExercisesSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(category, difficulty))
    
    async def _arun(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> str:
        """Obtener ejercicios disponibles"""
        try:
            # Convertir strings a enums si se proporcionan
            category_enum = None
            difficulty_enum = None
            
            if category:
                try:
                    category_enum = ExerciseCategory(category.lower())
                except ValueError:
                    pass
            
            if difficulty:
                try:
                    difficulty_enum = DifficultyLevel(difficulty.lower())
                except ValueError:
                    pass
            
            exercises = await self.fitness_repo.get_available_exercises(category_enum, difficulty_enum)
            
            if exercises:
                # Agrupar por categoría
                exercises_by_category = {}
                for exercise in exercises:
                    cat = exercise.category.value.title()
                    if cat not in exercises_by_category:
                        exercises_by_category[cat] = []
                    exercises_by_category[cat].append(exercise)
                
                result = "🏋️ **Ejercicios disponibles:**\n\n"
                
                for cat, cat_exercises in exercises_by_category.items():
                    result += f"**{cat}:**\n"
                    for exercise in cat_exercises:
                        difficulty_emoji = {"principiante": "🟢", "intermedio": "🟡", "avanzado": "🔴"}
                        emoji = difficulty_emoji.get(exercise.difficulty_level.value, "⚪")
                        result += f"• {emoji} **{exercise.name}** - {exercise.difficulty_level.value}\n"
                        if exercise.equipment and exercise.equipment != "ninguno":
                            result += f"  🛠️ Equipo: {exercise.equipment}\n"
                        if exercise.muscle_groups:
                            result += f"  💪 Músculos: {', '.join(exercise.muscle_groups)}\n"
                    result += "\n"
                
                return result.strip()
            else:
                filter_text = ""
                if category or difficulty:
                    filters = []
                    if category:
                        filters.append(f"categoría: {category}")
                    if difficulty:
                        filters.append(f"dificultad: {difficulty}")
                    filter_text = f" con filtros ({', '.join(filters)})"
                
                return f"ℹ️ No se encontraron ejercicios{filter_text}."
                
        except Exception as e:
            logger.error(f"❌ Error en GetExercisesTool: {str(e)}")
            return "❌ Lo siento, no pude obtener la lista de ejercicios en este momento. Por favor, intenta nuevamente."


# ==================== LISTA DE TOOLS ====================

class EndActiveWorkoutTool(BaseTool):
    """Tool para finalizar la rutina activa de un usuario por número de teléfono"""
    name: str = "end_active_workout"
    description: str = """
    Finaliza automáticamente la rutina activa del usuario usando su número de teléfono.
    Es más conveniente que end_workout cuando no conoces el workout_id específico.
    Usa esta herramienta cuando el usuario quiera terminar su entrenamiento actual.
    """
    args_schema: type = EndActiveWorkoutSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, phone_number: str, notes: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(phone_number, notes))
    
    async def _arun(self, phone_number: str, notes: Optional[str] = None) -> str:
        """Finalizar rutina activa por número de teléfono"""
        try:
            # Buscar rutina activa
            active_workout = await self.fitness_repo.get_active_workout(phone_number)
            
            if not active_workout:
                return "ℹ️ No tienes rutinas activas para finalizar. Puedes iniciar una nueva rutina cuando quieras."
            
            # Finalizar la rutina activa
            request = EndWorkoutRequest(
                workout_id=active_workout.id,
                notes=notes
            )
            
            response = await self.fitness_repo.end_workout(request)
            
            if response.success:
                # Obtener resumen de la rutina
                summary = await self.fitness_repo.get_workout_summary(active_workout.id)
                
                if summary:
                    summary_info = f"""
🎉 ¡Rutina completada exitosamente!

📝 **Rutina:** {summary.workout.name}
⏱️ **Duración:** {summary.duration_minutes or 0} minutos
📊 **Total de series:** {summary.total_sets}
🏋️ **Ejercicios realizados:** {', '.join(summary.exercises_performed) if summary.exercises_performed else 'Ninguno registrado'}
{f"⭐ **Dificultad promedio:** {summary.average_difficulty:.1f}/10" if summary.average_difficulty else ""}
{f"📝 **Notas:** {summary.workout.notes}" if summary.workout.notes else ""}

¡Excelente trabajo! 💪🔥

¿Te gustaría iniciar una nueva rutina o revisar tus ejercicios disponibles?
                    """
                    return summary_info.strip()
                else:
                    return "✅ Rutina finalizada exitosamente. ¡Buen trabajo! 💪"
            else:
                return f"❌ Hubo un problema al finalizar la rutina: {response.message}"
                
        except Exception as e:
            logger.error(f"❌ Error en EndActiveWorkoutTool: {str(e)}")
            return "❌ Lo siento, no pude finalizar la rutina en este momento. Por favor, intenta nuevamente."


class AddSetSimpleTool(BaseTool):
    """Tool simplificada para agregar series usando phone_number"""
    name: str = "add_set_simple"
    description: str = """
    Registra una serie de ejercicio en la rutina activa del usuario.
    Solo necesitas el número de teléfono, nombre del ejercicio y detalles básicos.
    Automáticamente encuentra la rutina activa del usuario.
    """
    args_schema: type = AddSetSimpleSchema
    
    def __init__(self):
        super().__init__()
    
    @property
    def fitness_repo(self):
        """Lazy loading del repositorio"""
        if not hasattr(self, '_fitness_repo'):
            self._fitness_repo = FitnessRepository()
        return self._fitness_repo
    
    def _run(self, phone_number: str, exercise: str, reps: Optional[int] = None,
             weight: Optional[float] = None, sets: int = 1, notes: Optional[str] = None) -> str:
        """Ejecutar la herramienta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(phone_number, exercise, reps, weight, sets, notes))
    
    async def _arun(self, phone_number: str, exercise: str, reps: Optional[int] = None,
                    weight: Optional[float] = None, sets: int = 1, notes: Optional[str] = None) -> str:
        """Agregar serie a la rutina activa"""
        try:
            # Buscar rutina activa
            active_workout = await self.fitness_repo.get_active_workout(phone_number)
            
            if not active_workout:
                return "❌ No hay rutinas activas. Por favor, inicia una rutina primero con start_workout."
            
            # Preparar request para agregar serie
            request = AddSetRequest(
                workout_id=active_workout.id,
                exercise_name=exercise,
                set_number=sets,
                weight=weight,
                weight_unit=WeightUnit.KG,
                repetitions=reps,
                notes=notes
            )
            
            response = await self.fitness_repo.add_set(request)
            
            if response.success:
                set_info = f"""
✅ ¡Serie registrada exitosamente!

🏋️ **Ejercicio:** {exercise}
📊 **Serie:** #{sets}
{f"⚖️ **Peso:** {weight} kg" if weight else ""}
{f"🔢 **Repeticiones:** {reps}" if reps else ""}
{f"📝 **Notas:** {notes}" if notes else ""}
🆔 **Rutina:** {active_workout.name}

¡Sigue así! 💪 ¿Vas a hacer otra serie?
                """
                return set_info.strip()
            else:
                return f"❌ Error al registrar la serie: {response.message}"
                
        except Exception as e:
            logger.error(f"❌ Error en AddSetSimpleTool: {str(e)}")
            return "❌ Lo siento, no pude registrar la serie en este momento. Por favor, intenta nuevamente."


def get_fitness_tools() -> List[BaseTool]:
    """
    Obtener todas las herramientas de fitness
    """
    return [
        StartWorkoutTool(),
        EndWorkoutTool(),
        EndActiveWorkoutTool(),
        AddSetTool(),
        AddSetSimpleTool(),  # Nueva herramienta simplificada
        GetActiveWorkoutTool(),
        GetExercisesTool()
    ]


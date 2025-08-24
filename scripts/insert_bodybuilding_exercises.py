"""
Script para insertar ejercicios clásicos de bodybuilding en la base de datos
"""
import asyncio
import logging
import os
import sys

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.supabase_client import get_supabase_direct_client
from domain.models import ExerciseCategory, DifficultyLevel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BodybuildingExerciseInserter:
    """Clase para insertar ejercicios de bodybuilding en la base de datos"""
    
    def __init__(self):
        self.client = get_supabase_direct_client()
        if not self.client:
            raise RuntimeError("No se pudo conectar a Supabase")
        
        # Definir ejercicios por grupos musculares
        self.exercises = {
            # PECHO
            "pecho": [
                # Básicos
                {"name": "Press de Banca", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra olímpica", "muscle_groups": ["pecho", "tríceps", "deltoides anterior"]},
                {"name": "Press de Banca Inclinado", "category": "fuerza", "difficulty": "intermedio", "equipment": "banca inclinada", "muscle_groups": ["pecho superior", "deltoides anterior", "tríceps"]},
                {"name": "Press de Banca Declinado", "category": "fuerza", "difficulty": "intermedio", "equipment": "banca declinada", "muscle_groups": ["pecho inferior", "tríceps"]},
                {"name": "Press con Mancuernas", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["pecho", "deltoides anterior", "tríceps"]},
                {"name": "Press Inclinado con Mancuernas", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["pecho superior", "deltoides anterior"]},
                {"name": "Flexiones", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["pecho", "tríceps", "core"]},
                
                # Aislamiento
                {"name": "Aperturas con Mancuernas", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["pecho"]},
                {"name": "Aperturas Inclinadas", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["pecho superior"]},
                {"name": "Cruces en Polea", "category": "fuerza", "difficulty": "intermedio", "equipment": "máquina de poleas", "muscle_groups": ["pecho"]},
                {"name": "Cruces en Polea Alta", "category": "fuerza", "difficulty": "intermedio", "equipment": "máquina de poleas", "muscle_groups": ["pecho inferior"]},
                {"name": "Cruces en Polea Baja", "category": "fuerza", "difficulty": "intermedio", "equipment": "máquina de poleas", "muscle_groups": ["pecho superior"]},
                {"name": "Pullover con Mancuerna", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuerna", "muscle_groups": ["pecho", "dorsales", "serratos"]},
                {"name": "Peck Deck", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina peck deck", "muscle_groups": ["pecho"]},
                {"name": "Flexiones Diamante", "category": "fuerza", "difficulty": "avanzado", "equipment": "ninguno", "muscle_groups": ["tríceps", "pecho"]},
            ],
            
            # ESPALDA
            "espalda": [
                # Básicos
                {"name": "Peso Muerto", "category": "fuerza", "difficulty": "avanzado", "equipment": "barra olímpica", "muscle_groups": ["dorsales", "trapecio", "romboides", "glúteos", "isquiotibiales"]},
                {"name": "Peso Muerto Rumano", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra olímpica", "muscle_groups": ["isquiotibiales", "glúteos", "espalda baja"]},
                {"name": "Dominadas", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra de dominadas", "muscle_groups": ["dorsales", "bíceps", "romboides"]},
                {"name": "Dominadas Supinas", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra de dominadas", "muscle_groups": ["dorsales", "bíceps"]},
                {"name": "Remo con Barra", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra olímpica", "muscle_groups": ["dorsales", "trapecio", "romboides", "bíceps"]},
                {"name": "Remo con Mancuerna", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuerna", "muscle_groups": ["dorsales", "trapecio", "romboides"]},
                
                # Aislamiento
                {"name": "Jalones al Pecho", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["dorsales", "bíceps"]},
                {"name": "Jalones tras Nuca", "category": "fuerza", "difficulty": "avanzado", "equipment": "máquina de poleas", "muscle_groups": ["dorsales", "trapecio"]},
                {"name": "Remo en Polea Baja", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["dorsales", "romboides", "trapecio"]},
                {"name": "Remo en T", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra en T", "muscle_groups": ["dorsales", "trapecio", "romboides"]},
                {"name": "Face Pulls", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["deltoides posterior", "trapecio", "romboides"]},
                {"name": "Encogimientos", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["trapecio"]},
                {"name": "Hiperextensiones", "category": "fuerza", "difficulty": "principiante", "equipment": "banco romano", "muscle_groups": ["espalda baja", "glúteos"]},
            ],
            
            # HOMBROS
            "hombros": [
                # Básicos
                {"name": "Press Militar", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra olímpica", "muscle_groups": ["deltoides", "tríceps", "core"]},
                {"name": "Press de Hombros con Mancuernas", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["deltoides", "tríceps"]},
                {"name": "Press Arnold", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["deltoides anterior", "deltoides medio"]},
                {"name": "Press tras Nuca", "category": "fuerza", "difficulty": "avanzado", "equipment": "barra", "muscle_groups": ["deltoides", "tríceps"]},
                
                # Aislamiento
                {"name": "Elevaciones Laterales", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["deltoides medio"]},
                {"name": "Elevaciones Frontales", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["deltoides anterior"]},
                {"name": "Pájaros", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["deltoides posterior"]},
                {"name": "Elevaciones Laterales en Polea", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["deltoides medio"]},
                {"name": "Remo al Mentón", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["deltoides medio", "trapecio"]},
                {"name": "Elevaciones Laterales Inclinadas", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["deltoides medio"]},
            ],
            
            # BRAZOS - BÍCEPS
            "biceps": [
                {"name": "Curl con Barra", "category": "fuerza", "difficulty": "principiante", "equipment": "barra", "muscle_groups": ["bíceps"]},
                {"name": "Curl con Mancuernas", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["bíceps"]},
                {"name": "Curl Martillo", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["bíceps", "braquial", "antebrazo"]},
                {"name": "Curl en Banco Scott", "category": "fuerza", "difficulty": "intermedio", "equipment": "banco scott", "muscle_groups": ["bíceps"]},
                {"name": "Curl Concentrado", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuerna", "muscle_groups": ["bíceps"]},
                {"name": "Curl en Polea", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["bíceps"]},
                {"name": "Curl 21s", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["bíceps"]},
                {"name": "Curl Zottman", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["bíceps", "antebrazos"]},
            ],
            
            # BRAZOS - TRÍCEPS
            "triceps": [
                {"name": "Press Francés", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra ez", "muscle_groups": ["tríceps"]},
                {"name": "Extensiones con Mancuerna", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuerna", "muscle_groups": ["tríceps"]},
                {"name": "Fondos en Paralelas", "category": "fuerza", "difficulty": "intermedio", "equipment": "barras paralelas", "muscle_groups": ["tríceps", "pecho inferior"]},
                {"name": "Fondos en Banco", "category": "fuerza", "difficulty": "principiante", "equipment": "banco", "muscle_groups": ["tríceps"]},
                {"name": "Extensiones en Polea", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["tríceps"]},
                {"name": "Press Cerrado", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["tríceps", "pecho"]},
                {"name": "Patadas de Tríceps", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["tríceps"]},
                {"name": "Extensiones sobre la Cabeza", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuerna", "muscle_groups": ["tríceps"]},
            ],
            
            # PIERNAS - CUÁDRICEPS
            "cuadriceps": [
                {"name": "Sentadillas", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra olímpica", "muscle_groups": ["cuádriceps", "glúteos", "core"]},
                {"name": "Sentadillas Frontales", "category": "fuerza", "difficulty": "avanzado", "equipment": "barra olímpica", "muscle_groups": ["cuádriceps", "core"]},
                {"name": "Prensa de Piernas", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina prensa", "muscle_groups": ["cuádriceps", "glúteos"]},
                {"name": "Extensiones de Cuádriceps", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina extensiones", "muscle_groups": ["cuádriceps"]},
                {"name": "Sentadillas Búlgaras", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["cuádriceps", "glúteos"]},
                {"name": "Lunges", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuernas", "muscle_groups": ["cuádriceps", "glúteos"]},
                {"name": "Sentadillas Goblet", "category": "fuerza", "difficulty": "principiante", "equipment": "mancuerna", "muscle_groups": ["cuádriceps", "glúteos"]},
                {"name": "Step Ups", "category": "fuerza", "difficulty": "principiante", "equipment": "cajón", "muscle_groups": ["cuádriceps", "glúteos"]},
            ],
            
            # PIERNAS - ISQUIOTIBIALES
            "isquiotibiales": [
                {"name": "Peso Muerto Rumano", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["isquiotibiales", "glúteos"]},
                {"name": "Curl de Piernas", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina curl", "muscle_groups": ["isquiotibiales"]},
                {"name": "Curl Nórdico", "category": "fuerza", "difficulty": "avanzado", "equipment": "ninguno", "muscle_groups": ["isquiotibiales"]},
                {"name": "Buenos Días", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["isquiotibiales", "glúteos", "espalda baja"]},
                {"name": "Peso Muerto Piernas Rígidas", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuernas", "muscle_groups": ["isquiotibiales", "glúteos"]},
            ],
            
            # GLÚTEOS
            "gluteos": [
                {"name": "Hip Thrust", "category": "fuerza", "difficulty": "intermedio", "equipment": "barra", "muscle_groups": ["glúteos"]},
                {"name": "Puentes de Glúteo", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["glúteos"]},
                {"name": "Sentadillas Sumo", "category": "fuerza", "difficulty": "intermedio", "equipment": "mancuerna", "muscle_groups": ["glúteos", "cuádriceps"]},
                {"name": "Patadas de Glúteo", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina de poleas", "muscle_groups": ["glúteos"]},
                {"name": "Caminata de Cangrejo", "category": "fuerza", "difficulty": "principiante", "equipment": "banda elástica", "muscle_groups": ["glúteos", "abductores"]},
            ],
            
            # PANTORRILLAS
            "pantorrillas": [
                {"name": "Elevaciones de Pantorrillas de Pie", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina", "muscle_groups": ["gastrocnemios"]},
                {"name": "Elevaciones de Pantorrillas Sentado", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina", "muscle_groups": ["sóleo"]},
                {"name": "Elevaciones en Prensa", "category": "fuerza", "difficulty": "principiante", "equipment": "máquina prensa", "muscle_groups": ["pantorrillas"]},
                {"name": "Saltos en Cajón", "category": "fuerza", "difficulty": "intermedio", "equipment": "cajón", "muscle_groups": ["pantorrillas", "cuádriceps"]},
            ],
            
            # CORE/ABDOMINALES
            "core": [
                {"name": "Plancha", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["core", "deltoides"]},
                {"name": "Plancha Lateral", "category": "fuerza", "difficulty": "intermedio", "equipment": "ninguno", "muscle_groups": ["oblicuos", "core"]},
                {"name": "Abdominales", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["abdominales"]},
                {"name": "Elevaciones de Piernas", "category": "fuerza", "difficulty": "intermedio", "equipment": "ninguno", "muscle_groups": ["abdominales inferiores"]},
                {"name": "Russian Twists", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["oblicuos"]},
                {"name": "Mountain Climbers", "category": "cardio", "difficulty": "intermedio", "equipment": "ninguno", "muscle_groups": ["core", "hombros"]},
                {"name": "Dead Bug", "category": "fuerza", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["core", "estabilidad"]},
                {"name": "Abdominales en Polea", "category": "fuerza", "difficulty": "intermedio", "equipment": "máquina de poleas", "muscle_groups": ["abdominales"]},
            ],
            
            # CARDIO
            "cardio": [
                {"name": "Correr", "category": "cardio", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["piernas", "cardiovascular"]},
                {"name": "Burpees", "category": "cardio", "difficulty": "intermedio", "equipment": "ninguno", "muscle_groups": ["cuerpo completo"]},
                {"name": "Jumping Jacks", "category": "cardio", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["piernas", "hombros"]},
                {"name": "Escalador", "category": "cardio", "difficulty": "intermedio", "equipment": "escaladora", "muscle_groups": ["piernas", "cardiovascular"]},
                {"name": "Remo en Máquina", "category": "cardio", "difficulty": "principiante", "equipment": "máquina de remo", "muscle_groups": ["espalda", "brazos", "piernas"]},
                {"name": "Bicicleta Estática", "category": "cardio", "difficulty": "principiante", "equipment": "bicicleta", "muscle_groups": ["piernas", "cardiovascular"]},
                {"name": "Elíptica", "category": "cardio", "difficulty": "principiante", "equipment": "elíptica", "muscle_groups": ["cuerpo completo"]},
            ],
            
            # FLEXIBILIDAD
            "flexibilidad": [
                {"name": "Estiramiento de Cuádriceps", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["cuádriceps"]},
                {"name": "Estiramiento de Isquiotibiales", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["isquiotibiales"]},
                {"name": "Estiramiento de Pecho", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["pecho", "deltoides anterior"]},
                {"name": "Gato-Vaca", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["espalda", "core"]},
                {"name": "Estiramiento de Hombros", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["deltoides", "trapecio"]},
                {"name": "Estiramiento de Gemelos", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["pantorrillas"]},
                {"name": "Mariposa", "category": "flexibilidad", "difficulty": "principiante", "equipment": "ninguno", "muscle_groups": ["aductores", "cadera"]},
            ]
        }
    
    async def insert_exercises(self):
        """Insertar todos los ejercicios en la base de datos"""
        logger.info("🏋️ Iniciando inserción de ejercicios de bodybuilding...")
        
        total_inserted = 0
        total_skipped = 0
        errors = []
        
        for muscle_group, exercises in self.exercises.items():
            logger.info(f"\n📝 Procesando grupo muscular: {muscle_group.upper()}")
            
            for exercise in exercises:
                try:
                    # Verificar si el ejercicio ya existe
                    existing = self.client.table("exercises").select("*").eq("name", exercise["name"]).execute()
                    
                    if existing.data:
                        logger.info(f"  ⏭️ Saltando '{exercise['name']}' (ya existe)")
                        total_skipped += 1
                        continue
                    
                    # Preparar datos para inserción
                    exercise_data = {
                        "name": exercise["name"],
                        "category": exercise["category"],
                        "difficulty_level": exercise["difficulty"],
                        "equipment": exercise["equipment"],
                        "muscle_groups": exercise["muscle_groups"],
                        "instructions": f"Ejercicio de {muscle_group} para trabajar {', '.join(exercise['muscle_groups'])}. Equipo: {exercise['equipment']}."
                    }
                    
                    # Insertar ejercicio
                    result = self.client.table("exercises").insert(exercise_data).execute()
                    
                    if result.data:
                        logger.info(f"  ✅ Insertado: '{exercise['name']}'")
                        total_inserted += 1
                    else:
                        logger.error(f"  ❌ Error insertando '{exercise['name']}': No se retornaron datos")
                        errors.append(f"No data returned for {exercise['name']}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error insertando '{exercise['name']}': {str(e)}")
                    errors.append(f"{exercise['name']}: {str(e)}")
        
        # Resumen final
        logger.info(f"\n{'='*50}")
        logger.info(f"📊 RESUMEN DE INSERCIÓN")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Ejercicios insertados: {total_inserted}")
        logger.info(f"⏭️ Ejercicios saltados: {total_skipped}")
        logger.info(f"❌ Errores: {len(errors)}")
        
        if errors:
            logger.info(f"\n🔍 DETALLES DE ERRORES:")
            for error in errors[:10]:  # Mostrar solo los primeros 10 errores
                logger.error(f"  - {error}")
            if len(errors) > 10:
                logger.info(f"  ... y {len(errors) - 10} errores más")
        
        return total_inserted, total_skipped, len(errors)
    
    async def verify_insertion(self):
        """Verificar que los ejercicios se insertaron correctamente"""
        logger.info(f"\n🔍 VERIFICANDO INSERCIÓN...")
        
        try:
            # Contar ejercicios por categoría
            result = self.client.table("exercises").select("category").execute()
            
            if not result.data:
                logger.error("❌ No se encontraron ejercicios en la base de datos")
                return False
            
            # Agrupar por categoría
            categories = {}
            for exercise in result.data:
                cat = exercise["category"]
                categories[cat] = categories.get(cat, 0) + 1
            
            logger.info("📊 Ejercicios por categoría:")
            for category, count in categories.items():
                logger.info(f"  {category}: {count} ejercicios")
            
            total = len(result.data)
            logger.info(f"\n🎯 Total de ejercicios en BD: {total}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando inserción: {str(e)}")
            return False


async def main():
    """Función principal"""
    logger.info("🏋️ INSERCIÓN DE EJERCICIOS DE BODYBUILDING")
    logger.info("=" * 60)
    
    try:
        inserter = BodybuildingExerciseInserter()
        
        # Insertar ejercicios
        inserted, skipped, errors = await inserter.insert_exercises()
        
        # Verificar inserción
        if inserted > 0:
            await inserter.verify_insertion()
        
        # Resultado final
        if errors == 0:
            logger.info("\n🎉 ¡Inserción completada exitosamente!")
        elif inserted > 0:
            logger.info(f"\n⚠️ Inserción completada con {errors} errores")
        else:
            logger.error("\n❌ La inserción falló completamente")
            return False
        
        logger.info(f"\n💡 Los ejercicios están listos para usar en el chatbot")
        logger.info(f"   Los usuarios pueden usar nombres como:")
        logger.info(f"   - 'Press de Banca', 'Sentadillas', 'Dominadas'")
        logger.info(f"   - 'Curl con Mancuernas', 'Peso Muerto'")
        logger.info(f"   - 'Elevaciones Laterales', 'Hip Thrust'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en main: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

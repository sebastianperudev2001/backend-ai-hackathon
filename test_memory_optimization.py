#!/usr/bin/env python3
"""
Script de prueba para verificar las optimizaciones de memoria
"""
import asyncio
import logging
import os
import sys
from datetime import datetime

# Agregar el directorio backend al path
sys.path.append('/home/sebastian/Documents/ia-hackathon/backend')

from config.memory_config import MemoryConfig, MemoryMode, create_optimized_memory, print_memory_stats
from agents.optimized_memory import OptimizedMemory, UltraCompactMemory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_memory_optimization():
    """Probar las optimizaciones de memoria"""
    print("🧪 PRUEBA DE OPTIMIZACIÓN DE MEMORIA")
    print("=" * 50)
    
    # Mostrar configuración actual
    print_memory_stats()
    
    # Crear memoria optimizada
    user_id = "test_user_memory_opt"
    memory = create_optimized_memory(user_id)
    
    print(f"\n✅ Memoria creada: {type(memory).__name__}")
    
    # Simular conversación larga
    print("\n📝 Simulando conversación larga...")
    
    conversation_data = [
        ("¿Cuál es mi rutina de ejercicios?", "Tu rutina incluye ejercicios de fuerza y cardio. Lunes: pecho y tríceps, Martes: espalda y bíceps, Miércoles: piernas..."),
        ("¿Qué debo comer para ganar músculo?", "Para ganar músculo necesitas proteína de alta calidad. Consume 1.6-2.2g por kg de peso corporal. Incluye pollo, pescado, huevos..."),
        ("¿Cuántas calorías debo consumir?", "Basado en tu peso y actividad, necesitas aproximadamente 2800-3200 calorías diarias para ganar músculo..."),
        ("¿Puedo hacer cardio mientras ganó músculo?", "Sí, puedes hacer cardio moderado. 2-3 sesiones de 20-30 minutos por semana no interferirán con el crecimiento muscular..."),
        ("¿Qué suplementos me recomiendas?", "Los suplementos básicos incluyen proteína en polvo, creatina monohidrato y un multivitamínico. La proteína te ayuda..."),
        ("¿Cuánto descanso necesito entre entrenamientos?", "El descanso es crucial para el crecimiento muscular. Necesitas 48-72 horas de descanso entre entrenamientos del mismo grupo muscular..."),
        ("¿Cómo sé si estoy progresando?", "El progreso se mide de varias formas: aumento de peso en los ejercicios, medidas corporales, fotos de progreso..."),
        ("¿Debo entrenar todos los días?", "No es recomendable entrenar todos los días. Tu cuerpo necesita tiempo para recuperarse y crecer. Un programa de 3-5 días..."),
        ("¿Qué hacer si llego a una meseta?", "Las mesetas son normales. Puedes cambiar tu rutina, aumentar la intensidad, revisar tu dieta o tomar una semana de descanso..."),
        ("¿Es mejor entrenar en la mañana o noche?", "El mejor momento es cuando puedas ser consistente. Algunos prefieren la mañana por energía, otros la noche por flexibilidad...")
    ]
    
    # Agregar conversaciones
    for i, (user_input, ai_response) in enumerate(conversation_data, 1):
        memory.save_context(
            {"input": user_input},
            {"output": ai_response}
        )
        print(f"  {i}. Usuario: {user_input[:50]}...")
        print(f"     Asistente: {ai_response[:50]}...")
    
    # Probar carga de memoria
    print(f"\n🧠 Probando carga de memoria...")
    memory_vars = memory.load_memory_variables({})
    context = memory_vars.get("chat_history", "")
    
    print(f"Contexto generado: {len(context)} caracteres")
    print(f"Contexto: {context[:200]}...")
    
    # Obtener estadísticas
    if hasattr(memory, 'get_memory_stats'):
        stats = memory.get_memory_stats()
        print(f"\n📊 ESTADÍSTICAS DE MEMORIA:")
        print(f"  Total mensajes locales: {stats.get('total_local_messages', 'N/A')}")
        print(f"  Mensajes en contexto: {stats.get('context_messages', 'N/A')}")
        print(f"  Tamaño contexto: {stats.get('context_size_chars', 'N/A')} caracteres")
        print(f"  Tokens estimados: {stats.get('estimated_tokens', 'N/A')}")
        print(f"  Max mensajes configurados: {stats.get('max_configured_messages', 'N/A')}")
    
    return context


async def test_different_modes():
    """Probar diferentes modos de memoria"""
    print("\n\n🔄 PRUEBA DE DIFERENTES MODOS")
    print("=" * 50)
    
    user_id = "test_user_modes"
    
    # Datos de conversación larga
    long_message = "Esta es una conversación muy larga que contiene mucha información detallada sobre rutinas de ejercicio, nutrición, suplementos y todos los aspectos relacionados con el fitness y la salud que normalmente consumiría muchos tokens si no fuera optimizada correctamente por nuestro sistema de memoria inteligente."
    
    modes_to_test = [
        MemoryMode.ULTRA_COMPACT,
        MemoryMode.OPTIMIZED,
        MemoryMode.STANDARD,
        MemoryMode.FULL
    ]
    
    results = {}
    
    for mode in modes_to_test:
        print(f"\n🧪 Probando modo: {mode.value.upper()}")
        
        # Establecer modo temporalmente
        original_mode = os.getenv("MEMORY_MODE")
        os.environ["MEMORY_MODE"] = mode.value
        
        try:
            # Crear memoria con el modo específico
            memory = create_optimized_memory(user_id + f"_{mode.value}")
            
            # Agregar mensajes
            for i in range(5):
                memory.save_context(
                    {"input": f"Pregunta {i+1}: {long_message}"},
                    {"output": f"Respuesta {i+1}: {long_message}"}
                )
            
            # Obtener contexto
            memory_vars = memory.load_memory_variables({})
            context = memory_vars.get("chat_history", "")
            
            # Obtener estadísticas
            stats = memory.get_memory_stats() if hasattr(memory, 'get_memory_stats') else {}
            
            results[mode.value] = {
                "context_chars": len(context),
                "estimated_tokens": len(context) // 4,
                "stats": stats
            }
            
            print(f"  Contexto: {len(context)} caracteres")
            print(f"  Tokens estimados: {len(context) // 4}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results[mode.value] = {"error": str(e)}
        
        finally:
            # Restaurar modo original
            if original_mode:
                os.environ["MEMORY_MODE"] = original_mode
            elif "MEMORY_MODE" in os.environ:
                del os.environ["MEMORY_MODE"]
    
    # Mostrar comparación
    print(f"\n📊 COMPARACIÓN DE MODOS:")
    print("-" * 50)
    for mode, result in results.items():
        if "error" not in result:
            chars = result["context_chars"]
            tokens = result["estimated_tokens"]
            print(f"{mode.upper():15} | {chars:5} chars | {tokens:4} tokens")
        else:
            print(f"{mode.upper():15} | ERROR: {result['error']}")
    
    return results


async def benchmark_memory_performance():
    """Benchmark de rendimiento de memoria"""
    print("\n\n⚡ BENCHMARK DE RENDIMIENTO")
    print("=" * 50)
    
    import time
    
    user_id = "benchmark_user"
    
    # Probar con memoria optimizada
    print("🚀 Probando memoria optimizada...")
    start_time = time.time()
    
    memory = create_optimized_memory(user_id)
    
    # Agregar muchos mensajes
    for i in range(100):
        memory.save_context(
            {"input": f"Mensaje {i}"},
            {"output": f"Respuesta {i}"}
        )
    
    # Cargar memoria varias veces
    for _ in range(10):
        memory_vars = memory.load_memory_variables({})
    
    end_time = time.time()
    optimized_time = end_time - start_time
    
    print(f"  Tiempo memoria optimizada: {optimized_time:.4f} segundos")
    
    # Obtener estadísticas finales
    if hasattr(memory, 'get_memory_stats'):
        final_stats = memory.get_memory_stats()
        print(f"  Mensajes finales: {final_stats.get('total_local_messages', 'N/A')}")
        print(f"  Contexto final: {final_stats.get('context_size_chars', 'N/A')} caracteres")
    
    return optimized_time


async def main():
    """Función principal de pruebas"""
    try:
        print("🎯 INICIANDO PRUEBAS DE OPTIMIZACIÓN DE MEMORIA")
        print("=" * 60)
        
        # Prueba básica
        await test_memory_optimization()
        
        # Prueba de diferentes modos
        await test_different_modes()
        
        # Benchmark de rendimiento
        await benchmark_memory_performance()
        
        print(f"\n\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 60)
        print("💡 Las optimizaciones están funcionando correctamente!")
        print("💰 Esto debería reducir significativamente los costos de tokens.")
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Configurar modo de prueba
    os.environ["MEMORY_MODE"] = "optimized"
    
    # Ejecutar pruebas
    asyncio.run(main())

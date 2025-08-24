#!/usr/bin/env python3
"""
Test simple para la herramienta start_workout
"""
import asyncio
import logging
import os
import sys

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fitness_tools import StartWorkoutTool

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_start_workout():
    """Test básico de la herramienta start_workout"""
    print("🧪 Iniciando test de start_workout...")
    
    # Crear instancia de la herramienta
    tool = StartWorkoutTool()
    
    # Datos de prueba
    phone_number = "+51998555878"  # Usuario demo
    workout_name = "Rutina de Prueba"
    description = "Test de la herramienta start_workout"
    
    try:
        print(f"📱 Testeando con usuario: {phone_number}")
        print(f"🏋️ Rutina: {workout_name}")
        print(f"📝 Descripción: {description}")
        print("-" * 50)
        
        # Ejecutar la herramienta
        result = await tool._arun(
            phone_number=phone_number,
            name=workout_name,
            description=description
        )
        
        print("✅ RESULTADO:")
        print(result)
        print("-" * 50)
        
        # Verificar que el resultado contiene información esperada
        if "Rutina iniciada exitosamente" in result:
            print("✅ Test EXITOSO: La rutina se inició correctamente")
            return True
        else:
            print("❌ Test FALLIDO: La rutina no se inició como se esperaba")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en el test: {str(e)}")
        logger.error(f"Error en test_start_workout: {str(e)}")
        return False


def test_start_workout_sync():
    """Test síncrono usando el método _run"""
    print("\n🧪 Test síncrono de start_workout...")
    
    tool = StartWorkoutTool()
    
    phone_number = "+51998555878"
    workout_name = "Rutina Sync Test"
    description = "Test síncrono de start_workout"
    
    try:
        print(f"📱 Usuario: {phone_number}")
        print(f"🏋️ Rutina: {workout_name}")
        print("-" * 50)
        
        # Ejecutar versión síncrona
        result = tool._run(
            phone_number=phone_number,
            name=workout_name,
            description=description
        )
        
        print("✅ RESULTADO SYNC:")
        print(result)
        print("-" * 50)
        
        if "Rutina iniciada exitosamente" in result:
            print("✅ Test SYNC EXITOSO")
            return True
        else:
            print("❌ Test SYNC FALLIDO")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en test sync: {str(e)}")
        return False


async def main():
    """Función principal para ejecutar todos los tests"""
    print("🚀 INICIANDO TESTS DE START_WORKOUT TOOL")
    print("=" * 60)
    
    # Test 1: Versión asíncrona
    success_async = await test_start_workout()
    
    # Test 2: Versión síncrona
    success_sync = test_start_workout_sync()
    
    # Resumen
    print("\n📊 RESUMEN DE TESTS:")
    print("=" * 60)
    print(f"Test Async: {'✅ EXITOSO' if success_async else '❌ FALLIDO'}")
    print(f"Test Sync:  {'✅ EXITOSO' if success_sync else '❌ FALLIDO'}")
    
    if success_async and success_sync:
        print("\n🎉 TODOS LOS TESTS PASARON!")
        return True
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        return False


if __name__ == "__main__":
    # Ejecutar tests
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Script completado exitosamente")
        exit(0)
    else:
        print("\n❌ Script completado con errores")
        exit(1)

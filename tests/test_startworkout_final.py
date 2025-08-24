#!/usr/bin/env python3
"""
Test final y simple para start_workout
Enfoque directo sin complicaciones de mocking
"""
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fitness_tools import StartWorkoutTool
from domain.models import User, Workout, DifficultyLevel, FitnessGoal, WorkoutResponse


def create_mock_user():
    """Crear un usuario mock para tests"""
    return User(
        id="test-user-123",
        phone_number="+51998555878",
        name="Usuario Test",
        fitness_level=DifficultyLevel.PRINCIPIANTE,
        goals=[FitnessGoal.GANAR_MUSCULO],
        medical_conditions=[],
        is_active=True,
        created_at=datetime.now()
    )


def create_mock_workout():
    """Crear un workout mock para tests"""
    return Workout(
        id="workout-123",
        user_id="test-user-123",
        name="Rutina de Prueba",
        description="Test de la herramienta start_workout",
        started_at=datetime.now(),
        total_sets=0
    )


async def test_start_workout_with_repository_mock():
    """Test con mock del repositorio completo"""
    print("🧪 Test de start_workout con mock de repositorio")
    print("=" * 50)
    
    try:
        # Crear mocks
        mock_user = create_mock_user()
        mock_workout = create_mock_workout()
        mock_response = WorkoutResponse(
            success=True,
            workout=mock_workout,
            message="Rutina iniciada exitosamente"
        )
        
        # Mock del FitnessRepository
        with patch('agents.fitness_tools.FitnessRepository') as MockRepo:
            # Configurar el mock del repositorio
            mock_repo_instance = MockRepo.return_value
            mock_repo_instance.get_or_create_user = AsyncMock(return_value=mock_user)
            mock_repo_instance.start_workout = AsyncMock(return_value=mock_response)
            
            # Crear herramienta (ahora usará el mock del repositorio)
            tool = StartWorkoutTool()
            
            # Ejecutar herramienta
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina de Prueba",
                description="Test con mock de repositorio"
            )
            
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar que se llamaron los métodos correctos
            mock_repo_instance.get_or_create_user.assert_called_once_with("+51998555878")
            mock_repo_instance.start_workout.assert_called_once()
            
            # Verificar contenido del resultado
            assert "Rutina iniciada exitosamente" in result
            assert "workout-123" in result
            assert "Rutina de Prueba" in result
            
            print("✅ Test exitoso: Herramienta funciona correctamente con mock")
            return True
            
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_start_workout_error_scenario():
    """Test de escenario de error"""
    print("\n🧪 Test de escenario de error")
    print("=" * 50)
    
    try:
        # Mock response con error
        mock_response = WorkoutResponse(
            success=False,
            message="Error en la base de datos",
            error="Connection failed"
        )
        
        with patch('agents.fitness_tools.FitnessRepository') as MockRepo:
            mock_repo_instance = MockRepo.return_value
            mock_repo_instance.get_or_create_user = AsyncMock(return_value=None)
            
            tool = StartWorkoutTool()
            
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina Test",
                description="Test error"
            )
            
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar manejo del error
            assert "Error: No se pudo obtener información del usuario" in result
            
            print("✅ Test de error: Manejo correcto del error")
            return True
            
    except Exception as e:
        print(f"❌ Error en test de error: {str(e)}")
        return False


def test_tool_basic_properties():
    """Test de propiedades básicas de la herramienta"""
    print("\n🧪 Test de propiedades básicas")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        
        # Verificar propiedades
        assert tool.name == "start_workout"
        assert "Inicia una nueva rutina de ejercicio" in tool.description
        assert hasattr(tool, 'args_schema')
        
        # Verificar schema
        schema_fields = tool.args_schema.__fields__
        assert 'phone_number' in schema_fields
        assert 'name' in schema_fields
        assert 'description' in schema_fields
        
        print("✅ Nombre: start_workout")
        print("✅ Descripción presente")
        print("✅ Schema con campos requeridos")
        print("✅ Propiedades básicas correctas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de propiedades: {str(e)}")
        return False


async def main():
    """Función principal"""
    print("🚀 TEST FINAL DE START_WORKOUT TOOL")
    print("=" * 60)
    
    # Ejecutar tests
    tests = [
        test_tool_basic_properties,
        test_start_workout_with_repository_mock,
        test_start_workout_error_scenario
    ]
    
    results = []
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {str(e)}")
            results.append(False)
    
    # Resumen
    print("\n📊 RESUMEN FINAL:")
    print("=" * 60)
    
    test_names = [
        "Propiedades básicas",
        "Funcionalidad con mock",
        "Manejo de errores"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"{i+1}. {name}: {status}")
    
    # Resultado final
    all_passed = all(results)
    if all_passed:
        print("\n🎉 TODOS LOS TESTS FINALES PASARON!")
        print("\n📋 RESUMEN DE LA HERRAMIENTA START_WORKOUT:")
        print("  • ✅ Estructura correcta")
        print("  • ✅ Parámetros válidos")
        print("  • ✅ Funcionalidad operativa")
        print("  • ✅ Manejo de errores")
        print("\n🚀 La herramienta start_workout está lista para usar!")
        return True
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Test final completado exitosamente")
        exit(0)
    else:
        print("\n❌ Test final completado con errores")
        exit(1)

#!/usr/bin/env python3
"""
Test completo para start_workout con mocks
Este test simula la funcionalidad sin depender de la base de datos real
"""
import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fitness_tools import StartWorkoutTool
from domain.models import User, Workout, DifficultyLevel, FitnessGoal, StartWorkoutRequest, WorkoutResponse


def create_mock_user():
    """Crear un usuario mock para tests"""
    return User(
        id="test-user-123",
        phone_number="+51998555878",
        name="Usuario Test",
        fitness_level=DifficultyLevel.PRINCIPIANTE,
        goals=[FitnessGoal.GANAR_MUSCULO],
        medical_conditions=[],  # Lista vacía en lugar de None
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


async def test_start_workout_success():
    """Test exitoso de start_workout con mocks"""
    print("🧪 Test de start_workout exitoso (con mocks)")
    print("=" * 50)
    
    try:
        # Crear herramienta
        tool = StartWorkoutTool()
        
        # Crear mocks
        mock_user = create_mock_user()
        mock_workout = create_mock_workout()
        mock_response = WorkoutResponse(
            success=True,
            workout=mock_workout,
            message="Rutina iniciada exitosamente"
        )
        
        # Mock del repositorio (necesitamos acceder a la propiedad primero)
        _ = tool.fitness_repo  # Inicializar la propiedad lazy
        with patch.object(tool, '_fitness_repo') as mock_repo:
            # Configurar mocks
            mock_repo.get_or_create_user = AsyncMock(return_value=mock_user)
            mock_repo.start_workout = AsyncMock(return_value=mock_response)
            
            # Ejecutar herramienta
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina de Prueba",
                description="Test mock"
            )
            
            # Verificar resultado
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar que se llamaron los métodos correctos
            mock_repo.get_or_create_user.assert_called_once_with("+51998555878")
            mock_repo.start_workout.assert_called_once()
            
            # Verificar contenido del resultado
            assert "Rutina iniciada exitosamente" in result
            assert "workout-123" in result
            assert "Rutina de Prueba" in result
            
            print("✅ Test exitoso: Todos los checks pasaron")
            return True
            
    except Exception as e:
        print(f"❌ Error en test exitoso: {str(e)}")
        return False


async def test_start_workout_user_error():
    """Test de error al obtener usuario"""
    print("\n🧪 Test de error al obtener usuario")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        
        # Mock del repositorio que retorna None (usuario no encontrado)
        _ = tool.fitness_repo  # Inicializar la propiedad lazy
        with patch.object(tool, '_fitness_repo') as mock_repo:
            mock_repo.get_or_create_user = AsyncMock(return_value=None)
            
            # Ejecutar herramienta
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina Test",
                description="Test error usuario"
            )
            
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar que maneja el error correctamente
            assert "Error: No se pudo obtener información del usuario" in result
            
            print("✅ Test de error de usuario: Manejo correcto del error")
            return True
            
    except Exception as e:
        print(f"❌ Error en test de error de usuario: {str(e)}")
        return False


async def test_start_workout_repository_error():
    """Test de error en el repositorio"""
    print("\n🧪 Test de error en el repositorio")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        mock_user = create_mock_user()
        
        # Mock response con error
        mock_response = WorkoutResponse(
            success=False,
            message="Error en la base de datos",
            error="Connection failed"
        )
        
        _ = tool.fitness_repo  # Inicializar la propiedad lazy
        with patch.object(tool, '_fitness_repo') as mock_repo:
            mock_repo.get_or_create_user = AsyncMock(return_value=mock_user)
            mock_repo.start_workout = AsyncMock(return_value=mock_response)
            
            # Ejecutar herramienta
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina Test",
                description="Test error repo"
            )
            
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar manejo del error
            assert "Error al iniciar rutina" in result
            assert "Connection failed" in result or "Error en la base de datos" in result
            
            print("✅ Test de error de repositorio: Manejo correcto del error")
            return True
            
    except Exception as e:
        print(f"❌ Error en test de error de repositorio: {str(e)}")
        return False


async def test_start_workout_exception():
    """Test de excepción inesperada"""
    print("\n🧪 Test de excepción inesperada")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        
        # Mock que lanza excepción
        _ = tool.fitness_repo  # Inicializar la propiedad lazy
        with patch.object(tool, '_fitness_repo') as mock_repo:
            mock_repo.get_or_create_user = AsyncMock(side_effect=Exception("Database connection failed"))
            
            # Ejecutar herramienta
            result = await tool._arun(
                phone_number="+51998555878",
                name="Rutina Test",
                description="Test excepción"
            )
            
            print("✅ RESULTADO:")
            print(result)
            print("-" * 30)
            
            # Verificar manejo de excepción
            assert "Error interno al iniciar rutina" in result
            assert "Database connection failed" in result
            
            print("✅ Test de excepción: Manejo correcto de excepciones")
            return True
            
    except Exception as e:
        print(f"❌ Error en test de excepción: {str(e)}")
        return False


def test_sync_method():
    """Test del método síncrono _run"""
    print("\n🧪 Test del método síncrono _run")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        mock_user = create_mock_user()
        mock_workout = create_mock_workout()
        mock_response = WorkoutResponse(
            success=True,
            workout=mock_workout,
            message="Rutina iniciada exitosamente"
        )
        
        _ = tool.fitness_repo  # Inicializar la propiedad lazy
        with patch.object(tool, '_fitness_repo') as mock_repo:
            mock_repo.get_or_create_user = AsyncMock(return_value=mock_user)
            mock_repo.start_workout = AsyncMock(return_value=mock_response)
            
            # Ejecutar método síncrono
            result = tool._run(
                phone_number="+51998555878",
                name="Rutina Sync Test",
                description="Test método síncrono"
            )
            
            print("✅ RESULTADO SYNC:")
            print(result)
            print("-" * 30)
            
            # Verificar resultado
            assert "Rutina iniciada exitosamente" in result
            
            print("✅ Test método síncrono: Funciona correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error en test método síncrono: {str(e)}")
        return False


async def main():
    """Función principal para ejecutar todos los tests"""
    print("🚀 TESTS COMPLETOS DE START_WORKOUT TOOL (CON MOCKS)")
    print("=" * 60)
    print("Estos tests simulan la funcionalidad completa sin base de datos real")
    print("=" * 60)
    
    # Tests asíncronos
    async_tests = [
        test_start_workout_success,
        test_start_workout_user_error,
        test_start_workout_repository_error,
        test_start_workout_exception
    ]
    
    # Tests síncronos
    sync_tests = [
        test_sync_method
    ]
    
    results = []
    
    # Ejecutar tests asíncronos
    for test in async_tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {str(e)}")
            results.append(False)
    
    # Ejecutar tests síncronos
    for test in sync_tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Error ejecutando {test.__name__}: {str(e)}")
            results.append(False)
    
    # Resumen
    print("\n📊 RESUMEN DE TESTS:")
    print("=" * 60)
    
    test_names = [
        "Start workout exitoso",
        "Error al obtener usuario",
        "Error en repositorio",
        "Manejo de excepciones",
        "Método síncrono"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"{i+1}. {name}: {status}")
    
    # Resultado final
    all_passed = all(results)
    if all_passed:
        print("\n🎉 TODOS LOS TESTS CON MOCKS PASARON!")
        print("La herramienta start_workout funciona correctamente.")
        return True
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Tests con mocks completados exitosamente")
        exit(0)
    else:
        print("\n❌ Tests con mocks completados con errores")
        exit(1)

#!/usr/bin/env python3
"""
Test simple y básico para la herramienta start_workout
Este test verifica la estructura y configuración de la herramienta sin depender de la base de datos
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fitness_tools import StartWorkoutTool


def test_tool_structure():
    """Test de la estructura básica de la herramienta"""
    print("🧪 Test de estructura de StartWorkoutTool")
    print("=" * 50)
    
    try:
        # Crear instancia de la herramienta
        tool = StartWorkoutTool()
        
        # Verificar propiedades básicas
        print(f"✅ Nombre de la herramienta: {tool.name}")
        print(f"✅ Descripción: {tool.description[:100]}...")
        print(f"✅ Schema de argumentos: {tool.args_schema.__name__}")
        
        # Verificar que tiene los métodos necesarios
        assert hasattr(tool, '_run'), "❌ Falta método _run"
        assert hasattr(tool, '_arun'), "❌ Falta método _arun"
        assert hasattr(tool, 'fitness_repo'), "❌ Falta propiedad fitness_repo"
        
        print("✅ Todos los métodos requeridos están presentes")
        
        # Verificar schema de argumentos
        schema_fields = tool.args_schema.__fields__
        required_fields = ['phone_number', 'name']
        
        for field in required_fields:
            assert field in schema_fields, f"❌ Falta campo requerido: {field}"
            print(f"✅ Campo '{field}' presente en schema")
        
        print("\n🎉 ESTRUCTURA DE LA HERRAMIENTA: ✅ CORRECTA")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de estructura: {str(e)}")
        return False


def test_tool_parameters():
    """Test de los parámetros de la herramienta"""
    print("\n🧪 Test de parámetros de StartWorkoutTool")
    print("=" * 50)
    
    try:
        tool = StartWorkoutTool()
        schema = tool.args_schema
        
        # Verificar campos del schema
        fields = schema.__fields__
        
        print("📋 Campos disponibles:")
        for field_name, field_info in fields.items():
            field_type = field_info.annotation
            is_required = field_info.is_required()
            default = field_info.default if hasattr(field_info, 'default') else 'N/A'
            
            print(f"  • {field_name}: {field_type} (Requerido: {is_required}, Default: {default})")
        
        # Verificar campos específicos
        assert 'phone_number' in fields, "❌ Falta campo phone_number"
        assert 'name' in fields, "❌ Falta campo name"
        assert 'description' in fields, "❌ Falta campo description"
        
        print("\n🎉 PARÁMETROS DE LA HERRAMIENTA: ✅ CORRECTOS")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de parámetros: {str(e)}")
        return False


def test_tool_instantiation():
    """Test de instanciación de la herramienta"""
    print("\n🧪 Test de instanciación de StartWorkoutTool")
    print("=" * 50)
    
    try:
        # Crear múltiples instancias
        tool1 = StartWorkoutTool()
        tool2 = StartWorkoutTool()
        
        # Verificar que son instancias independientes
        assert tool1 is not tool2, "❌ Las instancias no son independientes"
        print("✅ Instancias independientes creadas correctamente")
        
        # Verificar que tienen las mismas propiedades
        assert tool1.name == tool2.name, "❌ Nombres diferentes entre instancias"
        assert tool1.description == tool2.description, "❌ Descripciones diferentes"
        
        print("✅ Propiedades consistentes entre instancias")
        
        print("\n🎉 INSTANCIACIÓN DE LA HERRAMIENTA: ✅ CORRECTA")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de instanciación: {str(e)}")
        return False


def main():
    """Función principal para ejecutar todos los tests"""
    print("🚀 TESTS BÁSICOS DE START_WORKOUT TOOL")
    print("=" * 60)
    print("Estos tests verifican la estructura sin conectar a la base de datos")
    print("=" * 60)
    
    # Ejecutar tests
    tests = [
        test_tool_structure,
        test_tool_parameters,
        test_tool_instantiation
    ]
    
    results = []
    for test in tests:
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
        "Estructura de la herramienta",
        "Parámetros de la herramienta", 
        "Instanciación de la herramienta"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"{i+1}. {name}: {status}")
    
    # Resultado final
    all_passed = all(results)
    if all_passed:
        print("\n🎉 TODOS LOS TESTS BÁSICOS PASARON!")
        print("La herramienta start_workout está correctamente configurada.")
        return True
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("Revisa la configuración de la herramienta.")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Tests básicos completados exitosamente")
        exit(0)
    else:
        print("\n❌ Tests básicos completados con errores")
        exit(1)

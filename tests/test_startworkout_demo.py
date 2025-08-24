#!/usr/bin/env python3
"""
Demo simple de cómo usar la herramienta start_workout
Este archivo muestra ejemplos prácticos de uso
"""
import sys
import os
import asyncio

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fitness_tools import StartWorkoutTool


def demo_tool_info():
    """Mostrar información de la herramienta"""
    print("🔧 INFORMACIÓN DE LA HERRAMIENTA START_WORKOUT")
    print("=" * 60)
    
    tool = StartWorkoutTool()
    
    print(f"📛 Nombre: {tool.name}")
    print(f"📝 Descripción:")
    print(f"   {tool.description.strip()}")
    
    print(f"\n📋 Parámetros requeridos:")
    schema_fields = tool.args_schema.__fields__
    for field_name, field_info in schema_fields.items():
        field_type = field_info.annotation
        is_required = field_info.is_required()
        default = getattr(field_info, 'default', 'N/A')
        
        required_text = "✅ Requerido" if is_required else "⚪ Opcional"
        print(f"   • {field_name}: {field_type} - {required_text}")
        if not is_required and default != 'N/A':
            print(f"     Default: {default}")


def demo_usage_examples():
    """Mostrar ejemplos de uso"""
    print("\n💡 EJEMPLOS DE USO")
    print("=" * 60)
    
    print("📱 Ejemplo 1: Rutina básica")
    print("   phone_number: '+51998555878'")
    print("   name: 'Rutina Matutina'")
    print("   description: 'Ejercicios de fuerza para la mañana'")
    
    print("\n📱 Ejemplo 2: Rutina sin descripción")
    print("   phone_number: '+51987654321'")
    print("   name: 'Cardio Rápido'")
    print("   description: None  # Opcional")
    
    print("\n📱 Ejemplo 3: Rutina personalizada")
    print("   phone_number: '+51999888777'")
    print("   name: 'Entrenamiento HIIT'")
    print("   description: 'Intervalos de alta intensidad - 20 minutos'")


async def demo_tool_execution():
    """Demostrar ejecución de la herramienta (sin base de datos real)"""
    print("\n🚀 DEMO DE EJECUCIÓN")
    print("=" * 60)
    
    tool = StartWorkoutTool()
    
    print("⚠️  NOTA: Esta demo intentará conectar a la base de datos real.")
    print("   Si no hay conexión, mostrará el error correspondiente.")
    print("   Esto es normal y demuestra el manejo de errores.")
    print()
    
    # Ejemplo de parámetros
    phone_number = "+51998555878"
    workout_name = "Demo Rutina"
    description = "Rutina de demostración para test"
    
    print(f"📞 Ejecutando con:")
    print(f"   • Teléfono: {phone_number}")
    print(f"   • Rutina: {workout_name}")
    print(f"   • Descripción: {description}")
    print()
    
    try:
        print("🔄 Ejecutando herramienta...")
        result = await tool._arun(
            phone_number=phone_number,
            name=workout_name,
            description=description
        )
        
        print("📤 RESULTADO:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Analizar resultado
        if "Rutina iniciada exitosamente" in result:
            print("✅ ÉXITO: La rutina se inició correctamente")
        elif "Error" in result:
            print("⚠️  ERROR ESPERADO: Problema de conexión o configuración")
            print("   Esto es normal en un entorno de desarrollo")
        else:
            print("❓ RESULTADO INESPERADO")
            
    except Exception as e:
        print(f"⚠️  EXCEPCIÓN CAPTURADA: {str(e)}")
        print("   Esto puede ocurrir por problemas de configuración")
        print("   La herramienta maneja las excepciones correctamente")


def demo_integration_tips():
    """Consejos de integración"""
    print("\n🔗 CONSEJOS DE INTEGRACIÓN")
    print("=" * 60)
    
    print("1. 📋 Uso en FitnessAgent:")
    print("   - El agente usa esta herramienta automáticamente")
    print("   - Se activa cuando el usuario quiere iniciar una rutina")
    print("   - El phone_number se extrae del contexto del mensaje")
    
    print("\n2. 🔄 Flujo típico:")
    print("   - Usuario: 'Quiero empezar a entrenar'")
    print("   - Agente verifica rutina activa (get_active_workout)")
    print("   - Si no hay rutina activa, usa start_workout")
    print("   - Registra series con add_set durante el entrenamiento")
    print("   - Finaliza con end_workout")
    
    print("\n3. ⚙️ Configuración necesaria:")
    print("   - Variables de entorno de Supabase configuradas")
    print("   - Usuario existente en la base de datos")
    print("   - Políticas RLS configuradas correctamente")
    
    print("\n4. 🛠️ Debugging:")
    print("   - Revisar logs para errores de conexión")
    print("   - Verificar que el usuario existe en Supabase")
    print("   - Comprobar permisos de RLS")


async def main():
    """Función principal de la demo"""
    print("🎯 DEMO COMPLETA DE START_WORKOUT TOOL")
    print("=" * 70)
    print("Esta demo muestra cómo usar la herramienta start_workout")
    print("=" * 70)
    
    # Mostrar información
    demo_tool_info()
    
    # Mostrar ejemplos
    demo_usage_examples()
    
    # Ejecutar demo (puede fallar por conexión DB)
    await demo_tool_execution()
    
    # Consejos
    demo_integration_tips()
    
    print("\n" + "=" * 70)
    print("🎉 DEMO COMPLETADA")
    print("=" * 70)
    print("La herramienta start_workout está lista para usar en tu aplicación!")
    print("Revisa los logs y configuración si encuentras errores de conexión.")


if __name__ == "__main__":
    asyncio.run(main())

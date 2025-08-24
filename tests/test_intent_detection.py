#!/usr/bin/env python3
"""
Test para verificar la detección de intención del FitnessAgent
"""
import sys
import os

from agents.fitness_agent import FitnessAgent

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



def test_intent_detection():
    """Test de la detección de intención"""
    print("🧪 TEST DE DETECCIÓN DE INTENCIÓN")
    print("=" * 60)
    
    agent = FitnessAgent()
    
    # Casos que SÍ deben usar herramientas
    tool_cases = [
        "Quiero empezar a entrenar",
        "Vamos a comenzar rutina",
        "Iniciar workout ahora",
        "Empezar entrenamiento",
        "Terminé de entrenar",
        "Finalizar rutina",
        "Hice 10 flexiones",
        "Completé una serie",
        "Registra mi serie",
        "¿Tengo rutina activa?",
        "¿Qué rutina estoy haciendo?",
        "Muestra ejercicios disponibles",
        "¿Qué ejercicios hay?",
        "Quiero iniciar una rutina",
        "Ayúdame a empezar"
    ]
    
    # Casos que NO deben usar herramientas
    general_cases = [
        "¿Cómo hacer flexiones?",
        "¿Cuál es la técnica correcta de sentadillas?",
        "Consejos para principiantes",
        "¿Qué beneficios tiene el cardio?",
        "Crea una rutina para principiantes",
        "Diseña un plan de entrenamiento",
        "¿Qué comer antes de entrenar?",
        "Consejos de nutrición",
        "¿Cuánto debo entrenar?",
        "¿Cuándo es mejor hacer ejercicio?",
        "Rutina para ganar músculo",
        "Ejercicios para abdomen",
        "¿Para qué sirve el foam rolling?",
        "Beneficios del yoga",
        "¿Qué es HIIT?"
    ]
    
    print("✅ CASOS QUE DEBEN USAR HERRAMIENTAS:")
    print("-" * 40)
    tool_results = []
    for case in tool_cases:
        result = agent._detect_tool_intent(case)
        tool_results.append(result)
        status = "✅" if result else "❌"
        print(f"{status} '{case}' -> {result}")
    
    print(f"\n❌ CASOS QUE NO DEBEN USAR HERRAMIENTAS:")
    print("-" * 40)
    general_results = []
    for case in general_cases:
        result = agent._detect_tool_intent(case)
        general_results.append(result)
        status = "✅" if not result else "❌"  # Invertido porque esperamos False
        print(f"{status} '{case}' -> {result}")
    
    # Calcular precisión
    tool_accuracy = sum(tool_results) / len(tool_results) * 100
    general_accuracy = sum(1 for r in general_results if not r) / len(general_results) * 100
    overall_accuracy = (sum(tool_results) + sum(1 for r in general_results if not r)) / (len(tool_results) + len(general_results)) * 100
    
    print(f"\n📊 RESULTADOS:")
    print("=" * 60)
    print(f"Precisión casos con herramientas: {tool_accuracy:.1f}% ({sum(tool_results)}/{len(tool_results)})")
    print(f"Precisión casos generales: {general_accuracy:.1f}% ({sum(1 for r in general_results if not r)}/{len(general_results)})")
    print(f"Precisión general: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 80:
        print(f"\n🎉 EXCELENTE: La detección de intención funciona bien!")
        return True
    elif overall_accuracy >= 60:
        print(f"\n⚠️ ACEPTABLE: La detección funciona pero puede mejorar")
        return True
    else:
        print(f"\n❌ NECESITA MEJORAS: La detección no es suficientemente precisa")
        return False


def test_edge_cases():
    """Test de casos límite"""
    print(f"\n🧪 TEST DE CASOS LÍMITE")
    print("=" * 60)
    
    agent = FitnessAgent()
    
    edge_cases = [
        ("", False, "Texto vacío"),
        ("Hola", False, "Saludo simple"),
        ("¿Qué tal?", False, "Pregunta casual"),
        ("Gracias", False, "Agradecimiento"),
        ("Quiero saber sobre ejercicios", False, "Consulta general con 'quiero'"),
        ("Voy a preguntar algo", False, "Frase de acción sin contexto fitness"),
        ("Empezar a leer sobre fitness", False, "Acción no relacionada con entrenamiento"),
        ("Quiero entrenar mañana", True, "Intención futura de entrenar"),
        ("Necesito empezar una rutina", True, "Necesidad de acción"),
    ]
    
    results = []
    for text, expected, description in edge_cases:
        result = agent._detect_tool_intent(text)
        correct = result == expected
        results.append(correct)
        status = "✅" if correct else "❌"
        print(f"{status} {description}: '{text}' -> {result} (esperado: {expected})")
    
    accuracy = sum(results) / len(results) * 100
    print(f"\nPrecisión en casos límite: {accuracy:.1f}%")
    
    return accuracy >= 70


def main():
    """Función principal"""
    print("🚀 TESTS DE DETECCIÓN DE INTENCIÓN - FITNESS AGENT")
    print("=" * 70)
    
    # Ejecutar tests
    test1_result = test_intent_detection()
    test2_result = test_edge_cases()
    
    print(f"\n📋 RESUMEN FINAL:")
    print("=" * 70)
    print(f"Test principal: {'✅ EXITOSO' if test1_result else '❌ FALLIDO'}")
    print(f"Test casos límite: {'✅ EXITOSO' if test2_result else '❌ FALLIDO'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 TODOS LOS TESTS PASARON!")
        print("La detección de intención está funcionando correctamente.")
        print("El agente ahora debería usar herramientas solo cuando sea necesario.")
        return True
    else:
        print(f"\n⚠️ ALGUNOS TESTS FALLARON")
        print("Considera ajustar las palabras clave en _detect_tool_intent()")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ Tests completados exitosamente")
        exit(0)
    else:
        print(f"\n❌ Tests completados con errores")
        exit(1)

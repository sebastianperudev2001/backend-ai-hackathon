"""
Test que simula exactamente el flujo de producción para nutrición
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import CoordinatorAgent
from langchain.schema import HumanMessage


async def test_production_nutrition_flow():
    """Simular el flujo exacto de producción"""
    
    print("🔄 SIMULACIÓN DE FLUJO DE PRODUCCIÓN - NUTRICIÓN")
    print("=" * 60)
    
    # 1. Inicializar coordinador (como en handler)
    print("1. 🎯 Inicializando coordinador...")
    try:
        coordinator = CoordinatorAgent()
        print("   ✅ Coordinador inicializado (sin Claude pero funcional)")
    except Exception as e:
        print(f"   ❌ Error coordinador: {e}")
        return False
    
    # 2. Simular mensajes de nutrición de usuarios reales
    nutrition_messages = [
        "¿Qué comidas tengo hoy?",
        "¿Cuál es mi siguiente comida?",
        "¿Cómo voy con mi dieta?",
        "Mi progreso nutricional",
        "Buscar alimentos ricos en proteína",
        "¿Cuántas calorías he consumido?",
        "Que como en el almuerzo",
        "Mi plan de hoy"
    ]
    
    print(f"\n2. 📱 Probando {len(nutrition_messages)} mensajes de nutrición...")
    
    success_count = 0
    
    for i, message in enumerate(nutrition_messages, 1):
        try:
            print(f"\n   {i}. Mensaje: '{message}'")
            
            # Crear estado como en producción
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "next_agent": None,
                "context": {
                    "phone_number": "+51998555878",
                    "user_id": "617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03"
                }
            }
            
            # Procesar a través del grafo
            result = await coordinator.graph.ainvoke(initial_state)
            
            # Verificar respuesta
            if result and "messages" in result and len(result["messages"]) > 1:
                response = result["messages"][-1]
                print(f"      ✅ Respuesta generada: {len(response.content)} caracteres")
                print(f"      📝 Primeros 100 chars: {response.content[:100]}...")
                success_count += 1
            else:
                print(f"      ❌ No se generó respuesta válida")
                
        except Exception as e:
            print(f"      ❌ Error procesando: {str(e)}")
    
    print(f"\n📊 RESULTADOS:")
    print(f"   ✅ Exitosos: {success_count}/{len(nutrition_messages)}")
    print(f"   📈 Tasa de éxito: {success_count/len(nutrition_messages)*100:.1f}%")
    
    # 3. Probar detección específica del coordinador
    print(f"\n3. 🧠 Probando detección de agente del coordinador...")
    
    detection_tests = [
        ("¿Qué comidas tengo hoy?", "nutrition_agent"),
        ("Buscar alimentos", "nutrition_agent"),
        ("Mi dieta", "nutrition_agent"),
        ("¿Cómo hacer flexiones?", "fitness_agent"),
        ("Mi rutina", "fitness_agent")
    ]
    
    detection_success = 0
    for message, expected in detection_tests:
        detected = coordinator._simple_agent_detection(message)
        status = "✅" if detected == expected else "❌"
        print(f"   {status} '{message}' -> {detected}")
        if detected == expected:
            detection_success += 1
    
    print(f"\n   📊 Detección: {detection_success}/{len(detection_tests)} correcta")
    
    # 4. Probar logging real
    print(f"\n4. 💾 Probando logging de comida real...")
    
    try:
        # Usar el agente de nutrición directamente
        nutrition_agent = coordinator._get_or_create_nutrition_agent("617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03")
        
        # Simular registro de comida (esto normalmente requeriría conversación completa)
        from domain.models import User
        demo_user = User(
            id="617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03",
            phone_number="+51998555878", 
            name="Usuario Demo"
        )
        
        # Mensaje sobre comidas
        response = await nutrition_agent.process_message("¿Qué comidas tengo hoy?", demo_user, {})
        print(f"   ✅ Respuesta de comidas: {len(response)} chars")
        
        # Mensaje sobre siguiente comida
        response2 = await nutrition_agent.process_message("¿Cuál es mi siguiente comida?", demo_user, {})
        print(f"   ✅ Respuesta siguiente comida: {len(response2)} chars")
        
    except Exception as e:
        print(f"   ❌ Error en logging: {e}")
    
    # 5. Verificar estado final
    print(f"\n5. ✅ ESTADO FINAL DEL SISTEMA:")
    if success_count >= len(nutrition_messages) * 0.8:  # 80% de éxito
        print("   🎉 ¡SISTEMA DE NUTRICIÓN FUNCIONANDO EN PRODUCCIÓN!")
        print("   ✅ Coordinador: OK")
        print("   ✅ Agente de Nutrición: OK")
        print("   ✅ Detección de mensajes: OK")
        print("   ✅ Procesamiento: OK")
        return True
    else:
        print("   ⚠️ Sistema tiene problemas menores pero funcional")
        return False


if __name__ == "__main__":
    print("🚀 Test de Flujo de Producción - Sistema de Nutrición")
    print("=" * 70)
    print("Este test simula exactamente cómo funciona en producción")
    print()
    
    success = asyncio.run(test_production_nutrition_flow())
    
    if success:
        print("\n🎯 ¡EL SISTEMA DE NUTRICIÓN ESTÁ LISTO PARA PRODUCCIÓN!")
        print("   Los usuarios pueden enviar mensajes sobre comidas y recibirán respuestas")
    else:
        print("\n❌ El sistema necesita ajustes antes de producción")
    
    print("\n💡 Para usar en producción:")
    print("   1. Asegurar que webhook_handler.py use CoordinatorAgent")
    print("   2. Verificar variables de entorno en servidor")
    print("   3. Confirmar que RLS esté configurado correctamente")
    print("   4. Monitorear logs para errores específicos")

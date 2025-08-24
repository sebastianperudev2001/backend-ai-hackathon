"""
Script para diagnosticar problemas del sistema de nutrición en producción
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import CoordinatorAgent
from agents.nutrition_agent_simple import NutritionAgent
from repository.diet_repository import DietRepository
from repository.supabase_client import get_supabase_client
from domain.models import User, LogMealRequest, MealType


async def debug_production_flow():
    """Simular el flujo completo como en producción"""
    
    print("🚨 DIAGNÓSTICO DEL SISTEMA DE NUTRICIÓN EN PRODUCCIÓN")
    print("=" * 60)
    
    # 1. Verificar componentes básicos
    print("1. 🔧 Verificando componentes básicos...")
    
    try:
        supabase = get_supabase_client()
        print("   ✅ Supabase client inicializado")
    except Exception as e:
        print(f"   ❌ Error Supabase: {e}")
        return
    
    try:
        diet_repo = DietRepository()
        print("   ✅ DietRepository inicializado")
    except Exception as e:
        print(f"   ❌ Error DietRepository: {e}")
        return
    
    # 2. Verificar agente de nutrición
    print("\n2. 🤖 Verificando NutritionAgent...")
    
    try:
        nutrition_agent = NutritionAgent(user_id="617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03")
        print("   ✅ NutritionAgent creado")
        
        # Probar detección de mensajes
        test_messages = [
            "¿Qué comidas tengo hoy?",
            "¿Cuál es mi siguiente comida?", 
            "¿Cómo voy con mi dieta?",
            "Buscar pollo"
        ]
        
        for msg in test_messages:
            can_handle = nutrition_agent.can_handle(msg, {})
            status = "✅" if can_handle else "❌"
            print(f"   {status} '{msg}' -> {can_handle}")
            
    except Exception as e:
        print(f"   ❌ Error NutritionAgent: {e}")
        return
    
    # 3. Verificar coordinador (si es posible)
    print("\n3. 🎯 Verificando Coordinador...")
    
    try:
        # Solo probar creación del agente de nutrición del coordinador
        coordinator = CoordinatorAgent()
        nutrition_from_coordinator = coordinator._get_or_create_nutrition_agent("617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03")
        print("   ✅ Coordinador puede crear NutritionAgent")
    except Exception as e:
        print(f"   ❌ Error Coordinador: {e}")
        print("   💡 Esto podría explicar por qué no funciona en producción")
    
    # 4. Simular mensaje de usuario como en producción
    print("\n4. 📱 Simulando mensaje de usuario como en producción...")
    
    try:
        # Usuario demo
        demo_user = User(
            id="617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03",
            phone_number="+51998555878",
            name="Usuario Demo"
        )
        
        # Simular mensaje
        test_message = "¿Qué comidas tengo hoy?"
        
        # Verificar si el agente puede manejar
        can_handle = nutrition_agent.can_handle(test_message, {})
        print(f"   ✅ Agente puede manejar: {can_handle}")
        
        if can_handle:
            # Procesar mensaje
            response = await nutrition_agent.process_message(test_message, demo_user, {})
            print(f"   ✅ Respuesta generada: {len(response)} caracteres")
            print(f"   📝 Primeros 200 caracteres: {response[:200]}...")
        else:
            print("   ❌ Agente no puede manejar el mensaje")
            
    except Exception as e:
        print(f"   ❌ Error procesando mensaje: {e}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
    
    # 5. Verificar herramientas específicas
    print("\n5. 🔧 Verificando herramientas específicas...")
    
    try:
        from agents.nutrition_tools import NutritionTools
        tools = NutritionTools()
        
        # Probar búsqueda de alimentos
        search_result = await tools.search_foods("pollo", limit=3)
        print(f"   ✅ Búsqueda de alimentos: {search_result['success']}")
        if search_result['success']:
            print(f"   📊 Alimentos encontrados: {len(search_result['foods'])}")
        
        # Probar comidas del día
        today_result = await tools.get_today_meals("617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03")
        print(f"   ✅ Comidas del día: {today_result['success']}")
        
        # Probar siguiente comida
        next_result = await tools.get_next_meal("617ebc4e-d3f0-42d4-a8ea-1cf5afca8f03")
        print(f"   ✅ Siguiente comida: {next_result['success']}")
        
    except Exception as e:
        print(f"   ❌ Error en herramientas: {e}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
    
    # 6. Verificar RLS y permisos
    print("\n6. 🔒 Verificando RLS y permisos...")
    
    try:
        # Verificar si RLS está habilitado/deshabilitado
        rls_check = supabase.table('consumed_meals').select('*').limit(1).execute()
        print("   ✅ Acceso a consumed_meals OK")
        
        foods_check = supabase.table('foods').select('*').limit(1).execute()
        print("   ✅ Acceso a foods OK")
        
    except Exception as e:
        print(f"   ❌ Error de permisos: {e}")
        print("   💡 Podría ser un problema de RLS")
    
    # 7. Verificar logs recientes
    print("\n7. 📜 Verificando si hay comidas recientes...")
    
    try:
        # Buscar cualquier comida de las últimas 24 horas
        recent_meals = supabase.table('consumed_meals').select('*').gte(
            'created_at', (datetime.now() - timedelta(days=1)).isoformat()
        ).execute()
        
        print(f"   📊 Comidas últimas 24h: {len(recent_meals.data)}")
        
        if recent_meals.data:
            for meal in recent_meals.data[:3]:
                print(f"   📝 {meal['meal_name']} - {meal['created_at']}")
        
    except Exception as e:
        print(f"   ❌ Error consultando comidas recientes: {e}")


def check_webhook_integration():
    """Verificar integración con webhook"""
    
    print("\n8. 🌐 Verificando integración webhook...")
    
    try:
        # Simular payload de WhatsApp
        test_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "test",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {"phone_number_id": "test"},
                        "messages": [{
                            "from": "51998555878",
                            "id": "test_msg",
                            "type": "text",
                            "text": {"body": "¿Qué comidas tengo hoy?"},
                            "timestamp": "1234567890"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        print("   ✅ Payload de prueba creado")
        print(f"   📝 Mensaje: {test_payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']}")
        print("   💡 Para probar webhook completo, usar este payload en webhook_handler.py")
        
    except Exception as e:
        print(f"   ❌ Error creando payload: {e}")


if __name__ == "__main__":
    print("🔍 Diagnóstico del Sistema de Nutrición en Producción")
    print("=" * 70)
    
    # Importar timedelta que faltaba
    from datetime import timedelta
    
    # Ejecutar diagnóstico
    asyncio.run(debug_production_flow())
    
    # Verificar webhook
    check_webhook_integration()
    
    print("\n" + "=" * 70)
    print("💡 POSIBLES CAUSAS SI NO FUNCIONA EN PRODUCCIÓN:")
    print("   1. ❌ Error en coordinador (Claude API)")
    print("   2. ❌ RLS habilitado bloqueando acceso")
    print("   3. ❌ Variables de entorno no configuradas")
    print("   4. ❌ Usuario no existe en tabla users")
    print("   5. ❌ Webhook no está reenviando a agente correcto")
    print("   6. ❌ Errores en process_message no capturados")
    print("\n🔧 SIGUIENTE PASO: Revisar logs específicos del error en producción")

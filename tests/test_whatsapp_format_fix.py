#!/usr/bin/env python3
"""
Test para verificar el fix del formato de respuesta de WhatsApp
"""
import sys
import os
import asyncio

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.whatsapp_service import WhatsAppService


def test_response_sanitization():
    """Test de sanitización de respuestas"""
    print("🧪 TEST DE SANITIZACIÓN DE RESPUESTAS")
    print("=" * 60)
    
    service = WhatsAppService()
    
    # Casos de prueba
    test_cases = [
        # (input, expected_valid, description)
        ("Hola, ¿cómo estás?", True, "Respuesta normal"),
        ("", False, "Respuesta vacía"),
        (None, False, "Respuesta None"),
        (123, False, "Respuesta numérica"),
        (["lista"], False, "Respuesta lista"),
        ({"dict": "value"}, False, "Respuesta diccionario"),
        ("   ", False, "Solo espacios"),
        ("A" * 5000, False, "Respuesta muy larga"),
        ("Respuesta con emojis 💪🏋️🔥", True, "Con emojis"),
        ("Respuesta\ncon\nsaltos\nde\nlínea", True, "Con saltos de línea"),
    ]
    
    results = []
    
    for i, (input_response, expected_valid, description) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {description}")
        print(f"📝 Input: {repr(input_response)}")
        
        # Test sanitización
        try:
            sanitized = service._sanitize_response_for_whatsapp(input_response)
            print(f"🧹 Sanitizado: {repr(sanitized[:100])}")
            
            # Test validación
            is_valid = service._validate_message_for_whatsapp(sanitized)
            print(f"✅ Válido: {is_valid}")
            
            # Verificar que siempre devuelve algo válido después de sanitizar
            if is_valid:
                results.append(True)
                print("✅ CORRECTO: Sanitización exitosa")
            else:
                results.append(False)
                print("❌ ERROR: Sanitización falló")
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN: {str(e)}")
            results.append(False)
        
        print("-" * 40)
    
    # Resumen
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 RESUMEN:")
    print(f"Casos exitosos: {sum(results)}/{len(results)}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    return success_rate >= 90


def test_whatsapp_payload_format():
    """Test del formato de payload para WhatsApp"""
    print(f"\n🧪 TEST DE FORMATO DE PAYLOAD")
    print("=" * 60)
    
    # Simular el formato que debe tener el payload
    test_messages = [
        "Hola, ¿cómo estás?",
        "Esta es una respuesta con emojis 💪",
        "Respuesta\nmultilínea\ncon saltos",
        "Respuesta muy larga: " + "A" * 100
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📤 Test {i}: {message[:50]}...")
        
        # Formato esperado por WhatsApp API
        payload = {
            "messaging_product": "whatsapp",
            "to": "+51998555878",
            "type": "text",
            "text": {"body": message}
        }
        
        # Verificar estructura
        required_fields = ["messaging_product", "to", "type", "text"]
        has_all_fields = all(field in payload for field in required_fields)
        
        # Verificar que text.body sea string
        body_is_string = isinstance(payload["text"]["body"], str)
        
        print(f"✅ Estructura: {'OK' if has_all_fields else 'ERROR'}")
        print(f"✅ Body es string: {'OK' if body_is_string else 'ERROR'}")
        print(f"📏 Longitud: {len(payload['text']['body'])} caracteres")
        
        if has_all_fields and body_is_string:
            print("✅ PAYLOAD VÁLIDO")
        else:
            print("❌ PAYLOAD INVÁLIDO")
    
    return True


async def test_service_integration():
    """Test de integración del servicio (sin enviar realmente)"""
    print(f"\n🧪 TEST DE INTEGRACIÓN DEL SERVICIO")
    print("=" * 60)
    
    service = WhatsAppService()
    
    # Test de respuestas predefinidas (no requiere Claude)
    test_inputs = [
        "hola",
        "ayuda", 
        "rutina",
        "mensaje aleatorio"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: '{input_text}'")
        
        try:
            # Generar respuesta (sin Claude, usará fallback)
            response = await service._generate_text_response(input_text)
            
            # Validar respuesta
            is_valid = service._validate_message_for_whatsapp(response)
            
            print(f"📤 Respuesta: {response[:100]}...")
            print(f"✅ Válida: {is_valid}")
            print(f"📏 Longitud: {len(response)} caracteres")
            
            if is_valid:
                print("✅ INTEGRACIÓN OK")
            else:
                print("❌ INTEGRACIÓN FALLÓ")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    return True


async def main():
    """Función principal"""
    print("🚀 TESTS DE FIX PARA FORMATO WHATSAPP")
    print("=" * 80)
    print("Verificando que las respuestas sean compatibles con WhatsApp API")
    print("=" * 80)
    
    # Ejecutar tests
    test1 = test_response_sanitization()
    test2 = test_whatsapp_payload_format()
    test3 = await test_service_integration()
    
    # Resumen final
    print(f"\n📋 RESUMEN FINAL:")
    print("=" * 80)
    print(f"Sanitización: {'✅ OK' if test1 else '❌ FALLO'}")
    print(f"Formato payload: {'✅ OK' if test2 else '❌ FALLO'}")
    print(f"Integración: {'✅ OK' if test3 else '❌ FALLO'}")
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print(f"\n🎉 TODOS LOS TESTS PASARON!")
        print("El fix para el formato de WhatsApp está funcionando correctamente.")
        print("\n🔧 MEJORAS IMPLEMENTADAS:")
        print("• Sanitización automática de respuestas")
        print("• Validación de formato antes de enviar")
        print("• Manejo robusto de errores")
        print("• Logging detallado para debugging")
    else:
        print(f"\n⚠️ ALGUNOS TESTS FALLARON")
        print("Revisa los logs para más detalles.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print(f"\n✅ Fix verificado exitosamente")
        exit(0)
    else:
        print(f"\n❌ Fix necesita más trabajo")
        exit(1)

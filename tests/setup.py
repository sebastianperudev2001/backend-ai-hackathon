#!/usr/bin/env python3
"""
Script de configuración rápida para el sistema multi-agente
Ejecutar con: python setup.py
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header():
    """Mostrar header del setup"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🚀 SETUP - SISTEMA MULTI-AGENTE CON CLAUDE 🚀        ║
    ║              Bot de Fitness y Nutrición                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Verificar versión de Python"""
    print("🔍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")


def install_dependencies():
    """Instalar dependencias"""
    print("\n📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        print("Intenta ejecutar manualmente: pip install -r requirements.txt")
        return False
    return True


def create_env_file():
    """Crear archivo .env con configuración básica"""
    print("\n⚙️ Configurando variables de entorno...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        response = input("Ya existe un archivo .env. ¿Quieres sobrescribirlo? (s/n): ")
        if response.lower() != 's':
            print("⏭️ Saltando configuración de .env")
            return
    
    print("\n📝 Vamos a configurar tu archivo .env")
    print("-" * 50)
    
    # Solicitar API Key de Anthropic (requerido)
    print("\n🔑 CONFIGURACIÓN DE CLAUDE (REQUERIDO)")
    anthropic_key = input("Ingresa tu ANTHROPIC_API_KEY (ve a console.anthropic.com): ").strip()
    
    if not anthropic_key:
        print("⚠️ ADVERTENCIA: Sin API key de Anthropic el sistema usará respuestas predefinidas")
        anthropic_key = ""
    
    # Preguntar si quiere configurar WhatsApp
    print("\n📱 CONFIGURACIÓN DE WHATSAPP (OPCIONAL)")
    configure_whatsapp = input("¿Quieres configurar WhatsApp Business API? (s/n): ").lower() == 's'
    
    whatsapp_token = ""
    whatsapp_phone_id = ""
    verify_token = "fitness_bot_verify_123"
    
    if configure_whatsapp:
        whatsapp_token = input("WHATSAPP_TOKEN: ").strip()
        whatsapp_phone_id = input("WHATSAPP_PHONE_ID: ").strip()
        custom_verify = input(f"VERIFY_TOKEN (Enter para usar '{verify_token}'): ").strip()
        if custom_verify:
            verify_token = custom_verify
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración de Claude API (REQUERIDO para IA)
ANTHROPIC_API_KEY={anthropic_key}
CLAUDE_MODEL=claude-3-5-sonnet-latest

# Configuración de WhatsApp Business API
WHATSAPP_TOKEN={whatsapp_token}
WHATSAPP_PHONE_ID={whatsapp_phone_id}
VERIFY_TOKEN={verify_token}
WHATSAPP_API_VERSION=v18.0

# Configuración de la aplicación
APP_ENV=development
PORT=8000
LOG_LEVEL=INFO

# Feature Flags
ENABLE_IMAGE_PROCESSING=true
ENABLE_AI_RESPONSES=true
ENABLE_MULTI_AGENT=true

# Configuración de agentes
AGENT_MAX_ITERATIONS=10
AGENT_TIMEOUT=30.0
"""
    
    # Escribir archivo
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado correctamente")
    
    if anthropic_key:
        print("✅ Sistema multi-agente con Claude configurado")
    else:
        print("⚠️ Sistema funcionará con respuestas predefinidas (sin IA)")


def test_setup():
    """Probar que todo esté configurado correctamente"""
    print("\n🧪 Probando configuración...")
    
    try:
        # Intentar importar las dependencias principales
        import anthropic
        import langgraph
        import langchain
        print("✅ Librerías principales importadas correctamente")
        
        # Verificar que se puede leer la configuración
        from config.settings import get_settings
        settings = get_settings()
        
        if settings.ANTHROPIC_API_KEY:
            print("✅ API Key de Anthropic detectada")
            
            # Intentar inicializar el coordinador
            try:
                from agents.coordinator import CoordinatorAgent
                coordinator = CoordinatorAgent()
                print("✅ Sistema multi-agente inicializado correctamente")
            except Exception as e:
                print(f"⚠️ Error inicializando agentes: {str(e)}")
                print("   Verifica que tu API key sea válida")
        else:
            print("⚠️ No se detectó API Key de Anthropic")
            print("   El sistema funcionará con respuestas predefinidas")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {str(e)}")
        print("   Verifica que las dependencias se instalaron correctamente")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False


def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n" + "="*60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("="*60)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. Para probar el sistema multi-agente:")
    print("   python test_agents.py")
    
    print("\n2. Para iniciar el servidor de WhatsApp:")
    print("   python main.py")
    
    print("\n3. Para desarrollo local con hot-reload:")
    print("   uvicorn main:app --reload --port 8000")
    
    print("\n📚 RECURSOS:")
    print("• Documentación completa: CLAUDE_INTEGRATION.md")
    print("• Obtener API Key de Claude: https://console.anthropic.com")
    print("• Configurar WhatsApp: https://developers.facebook.com/docs/whatsapp")
    
    print("\n💡 TIPS:")
    print("• Usa el modo interactivo de test_agents.py para probar conversaciones")
    print("• Los logs están en LOG_LEVEL=INFO por defecto (cambia en .env)")
    print("• Puedes agregar más agentes en la carpeta 'agents/'")
    
    print("\n¡Buena suerte con tu bot de fitness! 💪🚀")


def main():
    """Función principal del setup"""
    print_header()
    
    # Verificar Python
    check_python_version()
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Setup incompleto. Resuelve los errores e intenta nuevamente.")
        sys.exit(1)
    
    # Crear archivo .env
    create_env_file()
    
    # Probar configuración
    if test_setup():
        show_next_steps()
    else:
        print("\n⚠️ Setup completado con advertencias.")
        print("Revisa los mensajes anteriores y configura lo necesario.")
        show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script de verificación pre-despliegue para Railway
Ejecuta: python check_deploy.py
"""

import os
import sys
from pathlib import Path

def check_file_exists(filename, required=True):
    """Verificar si un archivo existe"""
    exists = Path(filename).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filename}: {'Encontrado' if exists else 'No encontrado'}")
    return exists

def check_env_variables():
    """Verificar variables de entorno críticas"""
    print("\n📋 Variables de Entorno:")
    
    critical_vars = [
        "WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_ID", 
        "VERIFY_TOKEN"
    ]
    
    optional_vars = [
        "APP_ENV",
        "PORT",
        "LOG_LEVEL"
    ]
    
    all_good = True
    
    for var in critical_vars:
        value = os.getenv(var)
        if value and value not in ["your_whatsapp_token", "your_phone_id", "fitness_bot_verify_123"]:
            print(f"✅ {var}: Configurado")
        else:
            print(f"❌ {var}: No configurado o usando valor por defecto")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"ℹ️  {var}: {value}")
    
    return all_good

def main():
    print("🚂 Verificación de Railway Deployment")
    print("=" * 40)
    
    print("\n📁 Archivos de Configuración:")
    
    # Archivos requeridos
    required_files = [
        "main.py",
        "requirements.txt",
        "Procfile",
        "config/settings.py"
    ]
    
    # Archivos opcionales pero recomendados
    optional_files = [
        "railway.json",
        "runtime.txt",
        ".gitignore",
        "README.md"
    ]
    
    all_required = True
    for file in required_files:
        if not check_file_exists(file, required=True):
            all_required = False
    
    for file in optional_files:
        check_file_exists(file, required=False)
    
    # Verificar variables de entorno
    env_ok = check_env_variables()
    
    # Verificar importaciones
    print("\n🐍 Verificando imports:")
    try:
        import fastapi
        print("✅ FastAPI instalado")
    except ImportError:
        print("❌ FastAPI no instalado - ejecuta: pip install -r requirements.txt")
        all_required = False
    
    try:
        import uvicorn
        print("✅ Uvicorn instalado")
    except ImportError:
        print("❌ Uvicorn no instalado - ejecuta: pip install -r requirements.txt")
        all_required = False
    
    try:
        import dotenv
        print("✅ Python-dotenv instalado")
    except ImportError:
        print("❌ Python-dotenv no instalado - ejecuta: pip install -r requirements.txt")
        all_required = False
    
    # Resultado final
    print("\n" + "=" * 40)
    if all_required:
        print("✅ ¡Tu proyecto está listo para Railway!")
        print("\nPróximos pasos:")
        print("1. git add .")
        print("2. git commit -m 'Ready for Railway deployment'")
        print("3. git push origin main")
        print("4. Conecta con Railway y configura las variables de entorno")
        
        if not env_ok:
            print("\n⚠️  Recuerda configurar las variables de WhatsApp en Railway")
    else:
        print("❌ Faltan archivos o dependencias requeridas")
        print("Por favor, revisa los errores arriba")
        sys.exit(1)

if __name__ == "__main__":
    main()

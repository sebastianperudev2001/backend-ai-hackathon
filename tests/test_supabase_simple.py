#!/usr/bin/env python3
"""
Script SÚPER SIMPLE para probar Supabase
Solo lo básico para validar la conexión
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 Prueba súper simple de Supabase")
print("-" * 40)

# 1. Verificar variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL configurada: {'✅ Sí' if url else '❌ No'}")
print(f"Key configurada: {'✅ Sí' if key else '❌ No'}")

if not url or not key:
    print("\n❌ Faltan variables de entorno!")
    print("Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en tu .env")
    exit(1)

# 2. Intentar conectar
try:
    from supabase import create_client
    print("\n📦 Librería supabase importada ✅")
    
    client = create_client(url, key)
    print("🔗 Cliente creado ✅")
    
    # 3. Prueba básica
    result = client.table("users").select("count", count="exact").execute()
    print(f"📊 Conexión exitosa! Usuarios en DB: {result.count}")
    
    print("\n🎉 ¡Todo funciona perfectamente!")
    
except ImportError:
    print("\n❌ Librería supabase no instalada")
    print("Ejecuta: pip install supabase")
    
except Exception as e:
    print(f"\n⚠️ Error: {e}")
    print("💡 La conexión puede estar bien, solo sin permisos de consulta")

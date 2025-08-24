#!/usr/bin/env python3
"""
Script simple para probar la conexión con Supabase
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_supabase_connection():
    """Probar conexión básica con Supabase"""
    
    print("🔍 Probando conexión con Supabase...")
    print("=" * 50)
    
    # 1. Verificar variables de entorno
    print("1. Verificando variables de entorno:")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL no está configurada")
        return False
    else:
        print(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
    
    if not supabase_key:
        print("❌ SUPABASE_KEY no está configurada")
        return False
    else:
        print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
    
    print()
    
    # 2. Intentar importar supabase
    print("2. Verificando instalación de supabase:")
    try:
        from supabase import create_client, Client
        print("✅ Librería supabase importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando supabase: {e}")
        print("💡 Instala con: pip install supabase")
        return False
    
    print()
    
    # 3. Crear cliente
    print("3. Creando cliente de Supabase:")
    try:
        client = create_client(supabase_url, supabase_key)
        print("✅ Cliente de Supabase creado correctamente")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return False
    
    print()
    
    # 4. Probar conexión básica
    print("4. Probando conexión básica:")
    try:
        # Intentar hacer una consulta simple a la tabla users
        result = client.table("users").select("count", count="exact").execute()
        print(f"✅ Conexión exitosa! Tabla 'users' tiene {result.count} registros")
    except Exception as e:
        print(f"⚠️ Error consultando tabla 'users': {e}")
        print("💡 Esto puede ser normal si la tabla no existe o no tienes permisos")
        
        # Intentar una consulta más básica
        try:
            # Probar con una función RPC simple si existe
            result = client.rpc('version').execute()
            print("✅ Conexión básica exitosa (función version)")
        except Exception as e2:
            print(f"⚠️ Error en consulta básica: {e2}")
            print("💡 La conexión puede estar funcionando pero sin permisos de consulta")
    
    print()
    
    # 5. Probar usando nuestro cliente personalizado
    print("5. Probando con nuestro cliente personalizado:")
    try:
        from repository.supabase_client import get_supabase_client
        
        supabase_client = get_supabase_client()
        
        if supabase_client.is_connected():
            print("✅ Cliente personalizado conectado correctamente")
            
            # Intentar una consulta con nuestro cliente
            try:
                result = supabase_client.client.table("users").select("count", count="exact").execute()
                print(f"✅ Consulta exitosa con cliente personalizado! {result.count} usuarios")
            except Exception as e:
                print(f"⚠️ Error en consulta con cliente personalizado: {e}")
                
        else:
            print("❌ Cliente personalizado no pudo conectarse")
            return False
            
    except Exception as e:
        print(f"❌ Error con cliente personalizado: {e}")
        return False
    
    print()
    print("🎉 Prueba de conexión completada!")
    return True


def test_specific_query():
    """Probar la consulta específica que está fallando"""
    print("\n" + "=" * 50)
    print("🔍 Probando consulta específica de usuarios...")
    
    try:
        from repository.supabase_client import get_supabase_client
        
        supabase_client = get_supabase_client()
        
        if not supabase_client.is_connected():
            print("❌ Cliente no conectado")
            return False
        
        # Probar la consulta que está en el código
        phone_number = "+51998555878"  # Número de prueba
        print(f"Buscando usuario con teléfono: {phone_number}")
        
        result = supabase_client.client.table("users").select("*").eq("phone_number", phone_number).execute()
        print(f"✅ Consulta exitosa: {result}")
        
    except Exception as e:
        print(f"❌ Error en consulta específica: {e}")
        print("💡 Esto es normal si no existe un usuario con ese teléfono")


if __name__ == "__main__":
    print("🚀 Iniciando prueba de conexión con Supabase")
    print()
    
    success = test_supabase_connection()
    
    if success:
        test_specific_query()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Todas las pruebas completadas!")
    else:
        print("❌ Algunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1)

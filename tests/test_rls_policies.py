#!/usr/bin/env python3
"""
Script para diagnosticar problemas de RLS (Row Level Security) en Supabase
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_rls_policies():
    """Diagnosticar problemas de políticas RLS"""
    
    print("🔐 Diagnosticando políticas RLS en Supabase")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            print("❌ Faltan credenciales básicas")
            return False
        
        # 1. Probar con clave anónima (la que usas normalmente)
        print("1. Probando con clave anónima/pública:")
        client_anon = create_client(url, key)
        
        try:
            result = client_anon.table("users").select("*").limit(1).execute()
            print(f"✅ Consulta anónima exitosa: {len(result.data)} registros")
            if not result.data:
                print("📝 Tabla vacía o sin permisos de lectura")
        except Exception as e:
            print(f"❌ Error con clave anónima: {e}")
            if "permission denied" in str(e).lower() or "rls" in str(e).lower():
                print("🚨 PROBLEMA CONFIRMADO: Faltan políticas RLS para usuarios anónimos")
            elif "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print("🚨 PROBLEMA: La tabla 'users' no existe")
            else:
                print("🤔 Error desconocido, puede ser problema de RLS")
        
        print()
        
        # 2. Probar con service key si está disponible
        if service_key:
            print("2. Probando con service key (bypassa RLS):")
            client_service = create_client(url, service_key)
            
            try:
                result = client_service.table("users").select("*").limit(5).execute()
                print(f"✅ Consulta con service key exitosa: {len(result.data)} registros")
                if result.data:
                    print("📋 Datos encontrados con service key:")
                    for i, user in enumerate(result.data[:2]):
                        print(f"   {i+1}. ID: {user.get('id', 'N/A')}, Phone: {user.get('phone_number', 'N/A')}")
                    print("✅ CONFIRMADO: Los datos existen, el problema son las políticas RLS")
                else:
                    print("📝 Tabla vacía (pero accesible con service key)")
            except Exception as e:
                print(f"❌ Error con service key: {e}")
        else:
            print("2. ⚠️ SUPABASE_SERVICE_KEY no configurada")
            print("   💡 Configúrala para hacer pruebas que bypassen RLS")
        
        print()
        
        # 3. Verificar información de la tabla
        print("3. Verificando información de la tabla:")
        try:
            # Intentar obtener información del esquema
            result = client_anon.rpc('get_table_info', {'table_name': 'users'}).execute()
            print(f"✅ Información de tabla obtenida: {result.data}")
        except Exception as e:
            print(f"⚠️ No se pudo obtener info de tabla: {e}")
        
        print()
        
        # 4. Sugerencias de solución
        print("4. 🛠️ SOLUCIONES SUGERIDAS:")
        print()
        print("   A) Crear política para SELECT (lectura):")
        print("   ```sql")
        print("   CREATE POLICY \"Allow public read access\" ON public.users")
        print("   FOR SELECT USING (true);")
        print("   ```")
        print()
        print("   B) Crear política para INSERT (escritura):")
        print("   ```sql") 
        print("   CREATE POLICY \"Allow public insert\" ON public.users")
        print("   FOR INSERT WITH CHECK (true);")
        print("   ```")
        print()
        print("   C) Crear política para UPDATE:")
        print("   ```sql")
        print("   CREATE POLICY \"Allow public update\" ON public.users")
        print("   FOR UPDATE USING (true) WITH CHECK (true);")
        print("   ```")
        print()
        print("   D) O deshabilitar RLS temporalmente (NO recomendado para producción):")
        print("   ```sql")
        print("   ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;")
        print("   ```")
        print()
        print("   💡 Ve al SQL Editor en tu dashboard de Supabase y ejecuta estas consultas")
        
        return True
        
    except ImportError:
        print("❌ Librería supabase no instalada")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


def check_table_exists():
    """Verificar si la tabla users existe"""
    print("\n" + "=" * 50)
    print("📋 Verificando si la tabla 'users' existe...")
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not service_key:
            print("⚠️ Necesitas SUPABASE_SERVICE_KEY para esta verificación")
            return
        
        client = create_client(url, service_key)
        
        # Consultar el esquema de información
        result = client.rpc('get_schema_info').execute()
        print(f"✅ Esquema obtenido: {result.data}")
        
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de políticas RLS")
    print()
    
    success = test_rls_policies()
    
    if success:
        check_table_exists()
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN:")
    print("- Si ves 'permission denied' o errores RLS → Faltan políticas")
    print("- Si funciona con service key pero no con anon key → Problema de RLS")
    print("- Si no funciona ni con service key → Problema de tabla o conexión")
    print("\n💡 Revisa las soluciones sugeridas arriba")

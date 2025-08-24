#!/usr/bin/env python3
"""
Script para demostrar cómo configurar el contexto de usuario para RLS
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_with_user_context():
    """Probar consultas configurando el contexto de usuario"""
    
    print("🔐 Probando consultas con contexto de usuario para RLS")
    print("=" * 60)
    
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Faltan credenciales")
            return False
        
        client = create_client(url, key)
        
        # 1. Intentar consulta SIN contexto (debería fallar)
        print("1. Consulta SIN contexto de usuario:")
        try:
            result = client.table("users").select("*").execute()
            print(f"✅ Consulta exitosa (inesperado): {len(result.data)} registros")
        except Exception as e:
            print(f"❌ Error esperado: {e}")
            if "permission denied" in str(e).lower():
                print("✅ CONFIRMADO: RLS está funcionando, bloquea acceso sin contexto")
        
        print()
        
        # 2. Configurar contexto de usuario y probar
        print("2. Configurando contexto de usuario:")
        
        # Obtener el ID del usuario demo que insertamos
        demo_phone = "+51998555878"
        
        # Primero necesitamos obtener el ID del usuario usando service key
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        if service_key:
            print("   Obteniendo ID de usuario demo con service key...")
            admin_client = create_client(url, service_key)
            
            try:
                user_result = admin_client.table("users").select("id").eq("phone_number", demo_phone).single().execute()
                user_id = user_result.data["id"]
                print(f"   ✅ Usuario demo encontrado: {user_id}")
                
                # Ahora configurar el contexto en el cliente normal
                print("   Configurando contexto de usuario...")
                
                # Método 1: Usando set_config
                try:
                    client.rpc('set_config', {
                        'setting_name': 'app.current_user_id',
                        'new_value': user_id,
                        'is_local': True
                    }).execute()
                    print("   ✅ Contexto configurado con set_config")
                    
                    # Probar consulta con contexto
                    result = client.table("users").select("*").execute()
                    print(f"   ✅ Consulta CON contexto exitosa: {len(result.data)} registros")
                    
                    if result.data:
                        user = result.data[0]
                        print(f"   📋 Usuario: {user.get('name')} ({user.get('phone_number')})")
                    
                except Exception as e:
                    print(f"   ❌ Error configurando contexto: {e}")
                    
                    # Método 2: Usando headers (alternativo)
                    print("   Probando método alternativo con headers...")
                    try:
                        # Crear nuevo cliente con headers personalizados
                        client_with_headers = create_client(
                            url, 
                            key,
                            options={
                                "headers": {
                                    "x-user-id": user_id
                                }
                            }
                        )
                        
                        # Configurar usando SQL directo
                        client_with_headers.rpc('exec', {
                            'sql': f"SELECT set_config('app.current_user_id', '{user_id}', true)"
                        }).execute()
                        
                        result = client_with_headers.table("users").select("*").execute()
                        print(f"   ✅ Método alternativo exitoso: {len(result.data)} registros")
                        
                    except Exception as e2:
                        print(f"   ❌ Método alternativo falló: {e2}")
                
            except Exception as e:
                print(f"   ❌ Error obteniendo usuario demo: {e}")
                print("   💡 Asegúrate de que el usuario demo existe en la BD")
        else:
            print("   ⚠️ SUPABASE_SERVICE_KEY no configurada")
            print("   💡 Necesaria para obtener el ID del usuario")
        
        print()
        
        # 3. Mostrar la solución para tu código
        print("3. 🛠️ SOLUCIÓN PARA TU CÓDIGO:")
        print()
        print("   Modifica tu SupabaseClient para configurar el contexto:")
        print("   ```python")
        print("   def set_user_context(self, user_id: str):")
        print("       if self._client:")
        print("           try:")
        print("               self._client.rpc('set_config', {")
        print("                   'setting_name': 'app.current_user_id',")
        print("                   'new_value': user_id,")
        print("                   'is_local': True")
        print("               }).execute()")
        print("           except Exception as e:")
        print("               logger.warning(f'Error setting user context: {e}')")
        print("   ```")
        print()
        print("   Y en tu FitnessRepository:")
        print("   ```python")
        print("   def get_user_by_phone(self, phone_number: str):")
        print("       # Primero obtener el usuario con service key")
        print("       # Luego configurar el contexto")
        print("       # Finalmente hacer la consulta")
        print("   ```")
        
        return True
        
    except ImportError:
        print("❌ Librería supabase no instalada")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


def show_alternative_solutions():
    """Mostrar soluciones alternativas"""
    print("\n" + "=" * 60)
    print("🔧 SOLUCIONES ALTERNATIVAS:")
    print()
    
    print("OPCIÓN A - Política más permisiva (TEMPORAL):")
    print("```sql")
    print("-- Permitir acceso público de lectura (solo para desarrollo)")
    print("DROP POLICY IF EXISTS \"Users can manage their own profile\" ON users;")
    print("CREATE POLICY \"Allow public read access\" ON users")
    print("    FOR SELECT USING (true);")
    print("```")
    print()
    
    print("OPCIÓN B - Usar service key para operaciones internas:")
    print("```python")
    print("# En tu repository, usar service key para consultas internas")
    print("admin_client = create_client(url, service_key)")
    print("result = admin_client.table('users').select('*').eq('phone_number', phone).execute()")
    print("```")
    print()
    
    print("OPCIÓN C - Configurar contexto antes de cada consulta:")
    print("```python")
    print("# Antes de cada consulta de usuario")
    print("supabase_client.set_user_context(user_id)")
    print("result = supabase_client.client.table('users').select('*').execute()")
    print("```")
    print()
    
    print("💡 RECOMENDACIÓN:")
    print("- Para desarrollo: Usa OPCIÓN A (política permisiva)")
    print("- Para producción: Usa OPCIÓN C (contexto de usuario)")
    print("- Para operaciones internas: Usa OPCIÓN B (service key)")


if __name__ == "__main__":
    print("🚀 Iniciando prueba de contexto RLS")
    print()
    
    success = test_with_user_context()
    
    if success:
        show_alternative_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Ejecuta este script para confirmar el diagnóstico")
    print("2. Elige una de las soluciones mostradas")
    print("3. Implementa la solución en tu código")
    print("4. Prueba con el script original")

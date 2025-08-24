#!/usr/bin/env python3
"""
Prueba rápida de un agente con memoria optimizada
"""
import asyncio
import sys
import os

# Agregar el directorio backend al path
sys.path.append('/home/sebastian/Documents/ia-hackathon/backend')

from agents.base_agent import BaseAgent

async def test_agent_with_optimized_memory():
    """Probar agente con memoria optimizada"""
    print("🤖 PRUEBA DE AGENTE CON MEMORIA OPTIMIZADA")
    print("=" * 50)
    
    # Configurar modo optimizado
    os.environ["MEMORY_MODE"] = "optimized"
    
    # Crear agente
    agent = BaseAgent(
        name="TestAgent",
        system_prompt="Eres un asistente útil y conciso.",
        user_id="test_user_123"
    )
    
    print(f"✅ Agente creado: {agent.name}")
    print(f"📊 Tipo de memoria: {type(agent.memory).__name__}")
    
    # Obtener estadísticas de memoria
    if hasattr(agent.memory, 'get_memory_stats'):
        stats = agent.memory.get_memory_stats()
        print(f"📈 Configuración memoria:")
        print(f"  - Max mensajes: {stats.get('max_configured_messages', 'N/A')}")
        print(f"  - Max chars/mensaje: {stats.get('max_chars_per_message', 'N/A')}")
        print(f"  - Tokens estimados: {stats.get('estimated_tokens', 0)}")
    
    # Simular conversación
    print(f"\n💬 Simulando conversación...")
    
    test_inputs = [
        "Hola, ¿cómo estás?",
        "¿Qué ejercicios me recomiendas para ganar músculo?", 
        "¿Cuántas repeticiones debo hacer?",
        "¿Qué debo comer después del entrenamiento?"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Usuario: {user_input}")
        
        # Simular respuesta (sin llamar a Claude para no gastar tokens)
        mock_response = f"Respuesta simulada #{i} para: {user_input[:30]}..."
        
        # Guardar en memoria
        agent.memory.save_context(
            {"input": user_input},
            {"output": mock_response}
        )
        
        print(f"   Asistente: {mock_response}")
        
        # Mostrar contexto actual
        memory_vars = agent.memory.load_memory_variables({})
        context = memory_vars.get("chat_history", "")
        print(f"   📏 Contexto: {len(context)} caracteres")
    
    # Estadísticas finales
    if hasattr(agent.memory, 'get_memory_stats'):
        final_stats = agent.memory.get_memory_stats()
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"  Total mensajes: {final_stats.get('total_local_messages', 'N/A')}")
        print(f"  Contexto final: {final_stats.get('context_size_chars', 'N/A')} chars")
        print(f"  Tokens estimados: {final_stats.get('estimated_tokens', 'N/A')}")
        
        # Mostrar contexto completo
        memory_vars = agent.memory.load_memory_variables({})
        context = memory_vars.get("chat_history", "")
        print(f"\n💬 CONTEXTO FINAL:")
        print(f"  {context}")
    
    return agent

if __name__ == "__main__":
    asyncio.run(test_agent_with_optimized_memory())

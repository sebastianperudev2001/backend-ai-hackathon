"""
Configuración de memoria para optimizar costos de tokens
"""
import os
from enum import Enum
from typing import Dict, Any

class MemoryMode(Enum):
    """Modos de optimización de memoria"""
    ULTRA_COMPACT = "ultra_compact"      # Máximo ahorro (4 mensajes, 100 chars)
    OPTIMIZED = "optimized"              # Balanceado (6 mensajes, 200 chars)
    STANDARD = "standard"                # Normal (10 mensajes, 500 chars)
    FULL = "full"                        # Sin límites (30 mensajes, sin truncar)

class MemoryConfig:
    """Configuración de memoria basada en variables de entorno"""
    
    @staticmethod
    def get_memory_mode() -> MemoryMode:
        """
        Obtener modo de memoria desde variable de entorno
        Default: OPTIMIZED para ahorrar tokens
        """
        mode = os.getenv("MEMORY_MODE", "optimized").lower()
        try:
            return MemoryMode(mode)
        except ValueError:
            return MemoryMode.OPTIMIZED
    
    @staticmethod
    def get_memory_settings(mode: MemoryMode = None) -> Dict[str, Any]:
        """
        Obtener configuración de memoria según el modo
        
        Args:
            mode: Modo de memoria (si no se especifica, usa variable de entorno)
            
        Returns:
            Diccionario con configuración de memoria
        """
        if mode is None:
            mode = MemoryConfig.get_memory_mode()
        
        settings = {
            MemoryMode.ULTRA_COMPACT: {
                "max_context_messages": 4,
                "max_chars_per_message": 100,
                "use_compression": True,
                "context_prefix": "C:",  # Prefijo ultra corto
                "description": "Ultra compacto - máximo ahorro de tokens"
            },
            MemoryMode.OPTIMIZED: {
                "max_context_messages": 6,
                "max_chars_per_message": 200,
                "use_compression": True,
                "context_prefix": "Contexto:",
                "description": "Optimizado - buen balance ahorro/funcionalidad"
            },
            MemoryMode.STANDARD: {
                "max_context_messages": 10,
                "max_chars_per_message": 500,
                "use_compression": False,
                "context_prefix": "Historial de conversación:",
                "description": "Estándar - funcionalidad completa"
            },
            MemoryMode.FULL: {
                "max_context_messages": 30,
                "max_chars_per_message": None,  # Sin límite
                "use_compression": False,
                "context_prefix": "Historial completo de conversación:",
                "description": "Completo - sin optimizaciones"
            }
        }
        
        return settings.get(mode, settings[MemoryMode.OPTIMIZED])
    
    @staticmethod
    def estimate_token_savings(current_chars: int, mode: MemoryMode = None) -> Dict[str, Any]:
        """
        Estimar ahorro de tokens con diferentes modos
        
        Args:
            current_chars: Caracteres actuales del contexto
            mode: Modo propuesto
            
        Returns:
            Estimación de ahorro
        """
        if mode is None:
            mode = MemoryConfig.get_memory_mode()
        
        settings = MemoryConfig.get_memory_settings(mode)
        
        # Estimación rough de tokens (1 token ≈ 4 caracteres)
        current_tokens = current_chars / 4
        
        if mode == MemoryMode.ULTRA_COMPACT:
            # 4 mensajes * 100 chars = 400 chars máximo
            max_chars = 4 * 100
        elif mode == MemoryMode.OPTIMIZED:
            # 6 mensajes * 200 chars = 1200 chars máximo
            max_chars = 6 * 200
        elif mode == MemoryMode.STANDARD:
            # 10 mensajes * 500 chars = 5000 chars máximo
            max_chars = 10 * 500
        else:  # FULL
            max_chars = current_chars  # Sin límite
        
        optimized_chars = min(current_chars, max_chars)
        optimized_tokens = optimized_chars / 4
        
        savings_tokens = current_tokens - optimized_tokens
        savings_percentage = (savings_tokens / current_tokens * 100) if current_tokens > 0 else 0
        
        return {
            "mode": mode.value,
            "current_chars": current_chars,
            "current_tokens": int(current_tokens),
            "optimized_chars": optimized_chars,
            "optimized_tokens": int(optimized_tokens),
            "savings_tokens": int(savings_tokens),
            "savings_percentage": round(savings_percentage, 1),
            "description": settings["description"]
        }
    
    @staticmethod
    def get_emergency_mode_settings() -> Dict[str, Any]:
        """
        Configuración de emergencia para cuando los costos son críticos
        """
        return {
            "max_context_messages": 2,  # Solo 2 mensajes
            "max_chars_per_message": 50,  # Solo 50 caracteres
            "use_compression": True,
            "context_prefix": "",  # Sin prefijo
            "description": "EMERGENCIA - ahorro extremo de tokens"
        }


def get_optimized_memory_class():
    """
    Factory function para obtener la clase de memoria según configuración
    """
    from agents.optimized_memory import OptimizedMemory, UltraCompactMemory
    
    mode = MemoryConfig.get_memory_mode()
    
    if mode == MemoryMode.ULTRA_COMPACT:
        return UltraCompactMemory
    else:
        return OptimizedMemory


def create_optimized_memory(user_id: str, **kwargs):
    """
    Factory function para crear memoria optimizada según configuración
    
    Args:
        user_id: ID del usuario
        **kwargs: Argumentos adicionales
        
    Returns:
        Instancia de memoria optimizada
    """
    mode = MemoryConfig.get_memory_mode()
    settings = MemoryConfig.get_memory_settings(mode)
    
    # Obtener clase de memoria
    if mode == MemoryMode.ULTRA_COMPACT:
        from agents.optimized_memory import UltraCompactMemory
        return UltraCompactMemory(user_id=user_id, **kwargs)
    else:
        from agents.optimized_memory import OptimizedMemory
        return OptimizedMemory(
            user_id=user_id,
            max_context_messages=settings["max_context_messages"],
            max_chars_per_message=settings["max_chars_per_message"],
            **kwargs
        )


# Función de utilidad para debugging
def print_memory_stats():
    """Imprimir estadísticas de configuración de memoria"""
    mode = MemoryConfig.get_memory_mode()
    settings = MemoryConfig.get_memory_settings(mode)
    
    print(f"""
🧠 CONFIGURACIÓN DE MEMORIA
========================
Modo actual: {mode.value.upper()}
Descripción: {settings['description']}
Max mensajes: {settings['max_context_messages']}
Max caracteres por mensaje: {settings.get('max_chars_per_message', 'Sin límite')}
Compresión: {'Sí' if settings.get('use_compression') else 'No'}

💡 Para cambiar el modo, establece la variable de entorno:
   export MEMORY_MODE=ultra_compact  # Máximo ahorro
   export MEMORY_MODE=optimized      # Balanceado (default)
   export MEMORY_MODE=standard       # Estándar
   export MEMORY_MODE=full          # Sin optimizaciones
""")


if __name__ == "__main__":
    print_memory_stats()
    
    # Ejemplo de estimación de ahorro
    print("\n📊 ESTIMACIÓN DE AHORRO DE TOKENS")
    print("=" * 35)
    
    # Simulación con contexto de 2000 caracteres
    current_chars = 2000
    
    for mode in MemoryMode:
        savings = MemoryConfig.estimate_token_savings(current_chars, mode)
        print(f"""
{mode.value.upper()}:
  Tokens actuales: {savings['current_tokens']}
  Tokens optimizados: {savings['optimized_tokens']}
  Ahorro: {savings['savings_tokens']} tokens ({savings['savings_percentage']}%)
""")

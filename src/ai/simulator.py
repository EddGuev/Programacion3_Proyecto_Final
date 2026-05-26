# src/ai/simulator.py
"""
Simulador de IA que genera respuestas basadas en el contexto del archivo.
"""
import random
import re
from typing import Optional


def get_ai_response(prompt: str, contexto: Optional[str] = None) -> str:
    """
    Genera una respuesta simulada basada en el prompt y el contexto del archivo.
    """
    prompt = (prompt or "").strip().lower()
    contexto = (contexto or "").strip()
    
    # Si no hay contexto (chat sin archivo)
    if not contexto or len(contexto) < 10:
        return _respuesta_sin_archivo(prompt)
    
    # Chat con archivo cargado
    return _respuesta_con_archivo(prompt, contexto)


def _respuesta_sin_archivo(prompt: str) -> str:
    """Respuestas cuando no hay archivo cargado."""
    respuestas_generales = [
        f"🤖 **Simulación IA:** Entiendo tu pregunta sobre '{prompt[:50]}...'\n\nPuedo ayudarte mejor si cargas un archivo para analizar. ¿Quieres que te explique cómo funciona ChatDoc?",
        f"💡 Pregunta recibida: '{prompt[:60]}...'\n\nActualmente estoy en modo simulación. Carga un archivo (TXT, PDF, JSON, XML) para que pueda analizarlo y responder preguntas específicas sobre su contenido.",
        f"📚 Hola! Soy el asistente de ChatDoc en modo simulación.\n\nPara darte respuestas precisas, necesito que cargues un documento. Mientras tanto, puedo responder preguntas generales sobre el sistema.",
    ]
    
    # Detectar preguntas específicas
    if any(word in prompt for word in ['hola', 'hello', 'hi', 'qué tal']):
        return "👋 ¡Hola! Soy el asistente de ChatDoc en modo **Simulación IA**.\n\nPuedo ayudarte a analizar documentos (TXT, PDF, JSON, XML). Carga un archivo usando el botón '📂 Cargar Archivo' para comenzar."
    
    elif any(word in prompt for word in ['cómo', 'funciona', 'ayuda', 'help']):
        return "ℹ️ **Cómo usar ChatDoc:**\n\n1. Carga un archivo (TXT, PDF, JSON, XML)\n2. Haz preguntas sobre su contenido\n3. Exporta la conversación a JSON/XML\n4. Cambia entre Simulación IA y IA Real\n\n💡 *Actualmente en modo Simulación IA*"
    
    return random.choice(respuestas_generales)


def _respuesta_con_archivo(prompt: str, contexto: str) -> str:
    """Respuestas cuando hay archivo cargado."""
    # Extraer primeras líneas del contexto
    lineas = contexto.split('\n')[:10]
    preview = '\n'.join(lineas)
    
    # Detectar tipo de pregunta
    if any(word in prompt for word in ['resumen', 'resume', 'trata', 'sobre qué', 'tema']):
        return f"📋 **Resumen del archivo:**\n\nEl documento contiene aproximadamente {len(contexto)} caracteres. Las primeras líneas son:\n\n{preview[:300]}...\n\n💡 *Nota: Esta es una respuesta simulada. Activa el modo REAL para análisis completo con IA.*"
    
    elif any(word in prompt for word in ['cuánto', 'cantidad', 'número', 'líneas']):
        num_lineas = len(lineas)
        num_palabras = len(contexto.split())
        return f"📊 **Estadísticas del archivo:**\n- Líneas: ~{num_lineas}\n- Palabras: ~{num_palabras}\n- Caracteres: {len(contexto)}\n\n💡 *Respuesta simulada*"
    
    elif any(word in prompt for word in ['busca', 'encuentra', 'contiene', 'hay']):
        # Buscar palabras clave en el prompt
        palabras = [p for p in prompt.split() if len(p) > 3 and p not in ['busca', 'encuentra', 'contiene', 'archivo']]
        if palabras:
            palabra = palabras[0]
            count = contexto.lower().count(palabra)
            if count > 0:
                return f"🔍 Encontré **{count}** ocurrencia(s) de '{palabra}' en el archivo.\n\n💡 *Respuesta simulada*"
            else:
                return f"🔍 No encontré '{palabra}' en el archivo.\n\n💡 *Respuesta simulada*"
    
    # Respuesta genérica
    respuestas = [
        f"🤖 He analizado el archivo. Contiene {len(contexto)} caracteres de información.\n\nPrimeras líneas:\n{preview[:200]}...\n\n💡 *Respuesta simulada. Cambia a modo REAL para análisis completo.*",
        f"📖 El documento parece contener información técnica. Aquí un extracto:\n\n{preview[:250]}...\n\n💡 *Modo Simulación IA activo*",
        f"✅ Pregunta recibida: '{prompt[:50]}...'\n\nContexto disponible: {len(contexto)} caracteres.\n\n💡 *Activa modo REAL para respuestas precisas con IA*"
    ]
    
    return random.choice(respuestas)

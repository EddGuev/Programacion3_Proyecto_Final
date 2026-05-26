# src/services/ai_handler.py
"""
Servicio para manejar la interaccion con la API de Gemini
"""
import os
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None
        
        # Inicializar cliente solo si hay API key valida
        if self.api_key and self.api_key != "tu-api-key-aqui":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Advertencia: No se pudo inicializar Gemini: {e}")

    def obtener_respuesta(self, pregunta: str, contexto: str = "") -> str:
        """
        Obtiene una respuesta de Gemini basada en la pregunta y el contexto
        """
        if not self.client:
            return "❌ Error: API de Gemini no configurada. Verifica tu GEMINI_API_KEY en el archivo .env"
        
        try:
            # Construir el prompt
            if contexto:
                prompt = f"""Contexto del documento:
{contexto[:3000]}

Pregunta del usuario: {pregunta}

Responde de forma clara y concisa basandote en el contexto proporcionado."""
            else:
                prompt = f"Pregunta del usuario: {pregunta}\n\nResponde de forma clara y concisa."
            
            # Llamar a Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            return f"❌ Error al obtener respuesta de Gemini: {str(e)} 💡 Cambia a modo Simulacion IA para continuar."

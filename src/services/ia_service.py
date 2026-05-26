"""
Servicio de IA con Mock y Google Gemini
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class IAService:
    """Servicio de IA con toggle Mock/Gemini"""

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.gemini_model = None
        self.context = ""

        if not use_mock:
            self._init_gemini()

    def _init_gemini(self):
        """Inicializar Google Gemini"""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                print("⚠️ GEMINI_API_KEY no encontrada, usando Mock")
                self.use_mock = True
                return

            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Google Gemini inicializado")
        except ImportError:
            print("⚠️ google-generativeai no instalado, usando Mock")
            self.use_mock = True
        except Exception as e:
            print(f"⚠️ Error al inicializar Gemini: {e}, usando Mock")
            self.use_mock = True

    def set_context(self, content: str):
        """Establecer contexto del documento"""
        self.context = content

    def toggle_mode(self):
        """Cambiar entre Mock y Gemini"""
        self.use_mock = not self.use_mock
        if not self.use_mock and not self.gemini_model:
            self._init_gemini()

        mode = "Mock" if self.use_mock else "Gemini"
        return f"Modo cambiado a: {mode}"

    def get_current_mode(self) -> str:
        """Obtener modo actual"""
        return "Mock" if self.use_mock else "Gemini"

    def ask(self, question: str) -> str:
        """Hacer pregunta sobre el documento"""
        if self.use_mock:
            return self._mock_response(question)
        else:
            return self._gemini_response(question)

    def _mock_response(self, question: str) -> str:
        """Respuesta simulada"""
        if not self.context:
            return "⚠️ No hay documento cargado. Por favor, carga un archivo primero."

        question_lower = question.lower()

        # Respuestas inteligentes basadas en palabras clave
        if any(word in question_lower for word in ['resumen', 'resume', 'trata', 'sobre']):
            preview = self.context[:300] + "..." if len(self.context) > 300 else self.context
            return f"📄 Resumen del documento:\n\n{preview}\n\n(Respuesta generada por Mock IA)"

        elif any(word in question_lower for word in ['cuánto', 'cuantas', 'cantidad', 'número']):
            words = len(self.context.split())
            chars = len(self.context)
            lines = self.context.count('\n') + 1
            return f"📊 Estadísticas del documento:\n- Palabras: {words}\n- Caracteres: {chars}\n- Líneas: {lines}\n\n(Respuesta generada por Mock IA)"

        elif any(word in question_lower for word in ['busca', 'encuentra', 'contiene', 'menciona']):
            # Buscar palabras clave en el contexto
            words_to_find = [w for w in question.split() if len(w) > 4]
            found = []
            for word in words_to_find:
                if word.lower() in self.context.lower():
                    found.append(word)

            if found:
                return f"✅ Encontré las siguientes palabras: {', '.join(found)}\n\n(Respuesta generada por Mock IA)"
            else:
                return f"❌ No encontré esas palabras en el documento.\n\n(Respuesta generada por Mock IA)"

        else:
            return f"🤖 Pregunta recibida: '{question}'\n\nDocumento cargado: {len(self.context)} caracteres\n\n💡 Sugerencia: Pregunta sobre el resumen, estadísticas o búsqueda de palabras.\n\n(Respuesta generada por Mock IA)"

    def _gemini_response(self, question: str) -> str:
        """Respuesta con Google Gemini"""
        if not self.gemini_model:
            return "⚠️ Gemini no está disponible. Cambiando a Mock..."

        if not self.context:
            return "⚠️ No hay documento cargado. Por favor, carga un archivo primero."

        try:
            prompt = f"""Contexto del documento:
{self.context[:4000]}

Pregunta del usuario: {question}

Responde de forma clara y concisa basándote en el contexto proporcionado."""

            response = self.gemini_model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"❌ Error con Gemini: {str(e)}\n\nCambiando a Mock..."

# src/models/chat_model.py
from datetime import datetime
from database.db_manager import DatabaseManager
from services.file_loader import cargar_archivo
from services.ai_handler import AIHandler
import json
import xml.etree.ElementTree as ET

class ModeloChat:
    def __init__(self, usuario: str):
        self.usuario = usuario
        self.db = DatabaseManager()
        self.ai_handler = AIHandler()
        self.contenido_archivo = ""
        self.archivo_actual = None
        self.conversacion_id = None
        self.modo_ia = "simulacion"
        
        # Crear nueva conversación al iniciar
        self.nueva_conversacion()

    def nueva_conversacion(self):
        """Crea una nueva conversación en la base de datos"""
        self.conversacion_id = self.db.crear_conversacion(self.usuario)
        self.contenido_archivo = ""
        self.archivo_actual = None

    def cargar_archivo(self, ruta: str):
        """Carga un archivo y guarda su contenido"""
        self.contenido_archivo = cargar_archivo(ruta)
        self.archivo_actual = ruta
        
        # Actualizar conversación con el archivo
        if self.conversacion_id:
            self.db.actualizar_archivo_conversacion(self.conversacion_id, ruta)

    def set_modo_ia(self, modo: str):
        """Cambia el modo de IA (simulacion/real)"""
        self.modo_ia = modo

    def procesar_pregunta(self, pregunta: str) -> str:
        """Procesa una pregunta y retorna la respuesta"""
        # Guardar pregunta del usuario
        self.db.guardar_mensaje(
            conversacion_id=self.conversacion_id,
            emisor="usuario",
            texto=pregunta
        )
        
        # Generar respuesta
        if self.modo_ia == "real":
            respuesta = self.ai_handler.obtener_respuesta(
                pregunta=pregunta,
                contexto=self.contenido_archivo
            )
        else:
            respuesta = self._simular_respuesta(pregunta)
        
        # Guardar respuesta del sistema
        self.db.guardar_mensaje(
            conversacion_id=self.conversacion_id,
            emisor="modelo",
            texto=respuesta
        )
        
        return respuesta

    def _simular_respuesta(self, pregunta: str) -> str:
        """Simula una respuesta de IA"""
        import random
        
        # Si hay archivo cargado, responder sobre el archivo
        if self.contenido_archivo:
            num_chars = len(self.contenido_archivo)
            primeras_lineas = self.contenido_archivo[:200].replace('\n', ' ')
            return f"🤖 He analizado el archivo. Contiene {num_chars} caracteres de información. Primeras líneas: {primeras_lineas}... 💡 *Respuesta simulada. Cambia a modo REAL para análisis completo.*"
        
        # Si NO hay archivo, responder como chatbot general
        respuestas_generales = [
            f"🤖 Entiendo tu pregunta sobre '{pregunta}'. En modo simulación, puedo ayudarte con conversación general. Para análisis de documentos, carga un archivo primero.",
            f"💡 Interesante pregunta. Como IA simulada, puedo conversar contigo. Si necesitas analizar un documento específico, usa el botón '📂 Cargar Archivo'.",
            f"🔍 He procesado tu mensaje: '{pregunta}'. Estoy en modo simulación. Para respuestas más precisas basadas en documentos, cambia a modo REAL.",
            f"✨ Gracias por tu pregunta. En este modo puedo mantener una conversación básica. ¿Necesitas ayuda con algo más?",
            f"🎯 Pregunta recibida: '{pregunta}'. Como simulador, puedo responder de forma general. Para análisis profundo de archivos, activa el modo REAL."
        ]
        
        return random.choice(respuestas_generales)

    def obtener_historial_conversaciones(self) -> list:
        """Obtiene el historial de conversaciones del usuario
        Retorna: lista de tuplas (id, fecha, archivo, num_mensajes)
        """
        return self.db.obtener_conversaciones_usuario(self.usuario)

    def obtener_mensajes_conversacion(self, conv_id: int) -> list:
        """Obtiene los mensajes de una conversación específica
        Retorna: lista de tuplas (emisor, texto, fecha_hora)
        """
        return self.db.obtener_mensajes(conv_id)

    def obtener_archivo_conversacion(self, conv_id: int) -> str:
        """Obtiene el archivo asociado a una conversación"""
        return self.db.obtener_archivo_conversacion(conv_id)

    def exportar_json(self, ruta: str):
        """Exporta la conversación actual a JSON"""
        if not self.conversacion_id:
            raise ValueError("No hay conversación activa")
        
        mensajes = self.db.obtener_mensajes(self.conversacion_id)
        
        data = {
            "conversacion_id": self.conversacion_id,
            "usuario": self.usuario,
            "archivo": self.archivo_actual or "Sin archivo",
            "mensajes": [
                {
                    "emisor": emisor,
                    "texto": texto,
                    "fecha_hora": fecha_hora
                }
                for emisor, texto, fecha_hora in mensajes
            ]
        }
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def exportar_xml(self, ruta: str):
        """Exporta la conversación actual a XML"""
        if not self.conversacion_id:
            raise ValueError("No hay conversación activa")
        
        mensajes = self.db.obtener_mensajes(self.conversacion_id)
        
        root = ET.Element("conversacion", id=str(self.conversacion_id))
        
        usuario_elem = ET.SubElement(root, "usuario")
        usuario_elem.text = self.usuario
        
        archivo_elem = ET.SubElement(root, "archivo")
        archivo_elem.text = self.archivo_actual or "Sin archivo"
        
        mensajes_elem = ET.SubElement(root, "mensajes")
        
        for emisor, texto, fecha_hora in mensajes:
            msg_elem = ET.SubElement(mensajes_elem, "mensaje", emisor=emisor)
            
            texto_elem = ET.SubElement(msg_elem, "texto")
            texto_elem.text = texto
            
            fecha_elem = ET.SubElement(msg_elem, "fecha_hora")
            fecha_elem.text = fecha_hora
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(ruta, encoding='utf-8', xml_declaration=True)



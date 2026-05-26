"""
Controlador principal de la aplicación
"""
from services.ia_service import IAService
from services.file_processor import FileProcessor
from db.orm import SessionLocal
from db.conversation_model import Conversation
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


class MainController:
    """Controlador principal con gestión de archivos, IA y conversaciones"""

    def __init__(self, user):
        self.user = user
        self.ia_service = IAService(use_mock=True)
        self.current_file = None
        self.conversation_history = []

    def load_file(self, file_path: str):
        """Cargar archivo y establecer contexto"""
        success, message, content = FileProcessor.load_file(file_path)

        if success:
            self.current_file = file_path
            self.ia_service.set_context(content)
            self.add_to_history("Sistema", message)

        return success, message

    def process_message(self, message: str) -> str:
        """Procesar mensaje del usuario"""
        # Agregar mensaje del usuario al historial
        self.add_to_history("Usuario", message)

        # Obtener respuesta de IA
        response = self.ia_service.ask(message)

        # Agregar respuesta al historial
        self.add_to_history("ChatDoc", response)

        # Guardar en base de datos
        self.save_to_db(message, response)

        return response

    def toggle_ia_mode(self) -> str:
        """Cambiar entre Mock y Gemini"""
        message = self.ia_service.toggle_mode()
        self.add_to_history("Sistema", message)
        return message

    def get_ia_mode(self) -> str:
        """Obtener modo actual de IA"""
        return self.ia_service.get_current_mode()

    def add_to_history(self, sender: str, message: str):
        """Agregar mensaje al historial"""
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    def save_to_db(self, question: str, response: str):
        """Guardar conversación en SQLite"""
        session = SessionLocal()
        try:
            conversation = Conversation(
                user_id=self.user.id,
                question=question,
                response=response,
                file_path=self.current_file,
                timestamp=datetime.now()
            )
            session.add(conversation)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al guardar conversación: {e}")
        finally:
            session.close()

    def export_to_json(self, file_path: str):
        """Exportar conversación a JSON"""
        try:
            data = {
                'user': self.user.to_dict(),
                'export_date': datetime.now().isoformat(),
                'conversation': self.conversation_history
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True, f"✅ Conversación exportada a JSON: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar JSON: {str(e)}"

    def export_to_xml(self, file_path: str):
        """Exportar conversación a XML"""
        try:
            root = ET.Element('conversation')

            # Usuario
            user_elem = ET.SubElement(root, 'user')
            ET.SubElement(user_elem, 'id').text = str(self.user.id)
            ET.SubElement(user_elem, 'nombre').text = self.user.nombre
            ET.SubElement(user_elem, 'codigo').text = self.user.codigo

            # Fecha de exportación
            ET.SubElement(root, 'export_date').text = datetime.now().isoformat()

            # Mensajes
            messages_elem = ET.SubElement(root, 'messages')
            for msg in self.conversation_history:
                msg_elem = ET.SubElement(messages_elem, 'message')
                ET.SubElement(msg_elem, 'sender').text = msg['sender']
                ET.SubElement(msg_elem, 'content').text = msg['message']
                ET.SubElement(msg_elem, 'timestamp').text = msg['timestamp']

            # Formatear XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            return True, f"✅ Conversación exportada a XML: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar XML: {str(e)}"

    def clear_conversation(self):
        """Limpiar historial de conversación"""
        self.conversation_history = []
        self.current_file = None
        self.ia_service.set_context("")

"""
Controlador de Chat con Historial de Conversaciones
Maneja conversaciones, mensajes, archivos y exportaciÃ³n
"""
from services.ia_service import IAService
from services.file_processor import FileProcessor
from db.orm import SessionLocal
from db.conversation_model import Conversation
from db.message_model import Message
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ChatController:
    """Controlador de chat con soporte para mÃºltiples conversaciones"""

    def __init__(self, user):
        self.user = user
        self.ia_service = IAService(use_mock=True)
        self.current_conversation_id = None
        self.current_file = None
        self.session = SessionLocal()

    def create_new_conversation(self, title: str = None) -> int:
        """
        Crear nueva conversaciÃ³n

        Returns:
            conversation_id
        """
        try:
            if not title:
                # Generar tÃ­tulo automÃ¡tico
                count = self.session.query(Conversation).filter_by(user_id=self.user.id).count()
                title = f"ConversaciÃ³n {count + 1}"

            conversation = Conversation(
                user_id=self.user.id,
                title=title,
                created_at=datetime.now()
            )

            self.session.add(conversation)
            self.session.commit()

            self.current_conversation_id = conversation.id
            self.current_file = None

            return conversation.id

        except Exception as e:
            self.session.rollback()
            print(f"Error al crear conversaciÃ³n: {e}")
            return None

    def get_user_conversations(self):
        """
        Obtener todas las conversaciones del usuario

        Returns:
            Lista de tuplas (id, title, created_at)
        """
        try:
            conversations = self.session.query(Conversation).filter_by(
                user_id=self.user.id
            ).order_by(Conversation.updated_at.desc()).all()

            return [(c.id, c.title, c.created_at) for c in conversations]

        except Exception as e:
            print(f"Error al obtener conversaciones: {e}")
            return []

    def load_conversation(self, conversation_id: int):
        """
        Cargar conversaciÃ³n existente

        Returns:
            Lista de tuplas (role, content, timestamp)
        """
        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=conversation_id
            ).order_by(Message.timestamp.asc()).all()

            self.current_conversation_id = conversation_id

            # Cargar archivo asociado si existe
            conversation = self.session.query(Conversation).get(conversation_id)
            if conversation and conversation.file_path:
                self.current_file = conversation.file_path
                # Recargar contexto en IA
                success, _, content = FileProcessor.load_file(conversation.file_path)
                if success:
                    self.ia_service.set_context(content)

            return [(m.role, m.content, m.timestamp) for m in messages]

        except Exception as e:
            print(f"Error al cargar conversaciÃ³n: {e}")
            return []

    def add_message(self, role: str, content: str):
        """
        Agregar mensaje a la conversaciÃ³n actual

        Args:
            role: 'user', 'assistant', 'system'
            content: Contenido del mensaje
        """
        if not self.current_conversation_id:
            # Crear conversaciÃ³n automÃ¡ticamente si no existe
            self.create_new_conversation()

        try:
            message = Message(
                conversation_id=self.current_conversation_id,
                role=role,
                content=content,
                timestamp=datetime.now()
            )

            self.session.add(message)
            self.session.commit()

            # Actualizar timestamp de conversaciÃ³n
            conversation = self.session.query(Conversation).get(self.current_conversation_id)
            if conversation:
                conversation.updated_at = datetime.now()
                self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error al agregar mensaje: {e}")

    def load_file(self, file_path: str):
        """Cargar archivo y establecer contexto"""
        success, message, content = FileProcessor.load_file(file_path)

        if success:
            self.current_file = file_path
            self.ia_service.set_context(content)

            # Actualizar file_path en conversaciÃ³n actual
            if self.current_conversation_id:
                try:
                    conversation = self.session.query(Conversation).get(self.current_conversation_id)
                    if conversation:
                        conversation.file_path = file_path
                        # Actualizar tÃ­tulo si es la primera carga
                        if conversation.title.startswith("ConversaciÃ³n"):
                            from pathlib import Path
                            conversation.title = f"Chat sobre {Path(file_path).name}"
                        self.session.commit()
                except Exception as e:
                    self.session.rollback()
                    print(f"Error al actualizar conversaciÃ³n: {e}")

            self.add_message("system", message)

        return success, message

    def process_message(self, message: str) -> str:
        """Procesar mensaje del usuario"""
        # Agregar mensaje del usuario
        self.add_message("user", message)

        # Obtener respuesta de IA
        response = self.ia_service.ask(message)

        # Agregar respuesta
        self.add_message("assistant", response)

        return response

    def toggle_ia_mode(self) -> str:
        """Cambiar entre Mock y Gemini"""
        message = self.ia_service.toggle_mode()
        self.add_message("system", message)
        return message

    def get_ia_mode(self) -> str:
        """Obtener modo actual de IA"""
        return self.ia_service.get_current_mode()

    def export_to_json(self, file_path: str):
        """Exportar conversaciÃ³n actual a JSON"""
        if not self.current_conversation_id:
            return False, "No hay conversaciÃ³n activa para exportar"

        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=self.current_conversation_id
            ).order_by(Message.timestamp.asc()).all()

            conversation = self.session.query(Conversation).get(self.current_conversation_id)

            data = {
                'user': self.user.to_dict(),
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'file_path': conversation.file_path
                },
                'export_date': datetime.now().isoformat(),
                'messages': [m.to_dict() for m in messages]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True, f"âœ… ConversaciÃ³n exportada a JSON: {file_path}"
        except Exception as e:
            return False, f"âŒ Error al exportar JSON: {str(e)}"

    def export_to_xml(self, file_path: str):
        """Exportar conversaciÃ³n actual a XML"""
        if not self.current_conversation_id:
            return False, "No hay conversaciÃ³n activa para exportar"

        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=self.current_conversation_id
            ).order_by(Message.timestamp.asc()).all()

            conversation = self.session.query(Conversation).get(self.current_conversation_id)

            root = ET.Element('conversation')

            # Usuario
            user_elem = ET.SubElement(root, 'user')
            ET.SubElement(user_elem, 'id').text = str(self.user.id)
            ET.SubElement(user_elem, 'nombre').text = self.user.nombre
            ET.SubElement(user_elem, 'codigo').text = self.user.codigo

            # Info de conversaciÃ³n
            conv_elem = ET.SubElement(root, 'conversation_info')
            ET.SubElement(conv_elem, 'id').text = str(conversation.id)
            ET.SubElement(conv_elem, 'title').text = conversation.title
            ET.SubElement(conv_elem, 'created_at').text = conversation.created_at.isoformat()
            if conversation.file_path:
                ET.SubElement(conv_elem, 'file_path').text = conversation.file_path

            # Fecha de exportaciÃ³n
            ET.SubElement(root, 'export_date').text = datetime.now().isoformat()

            # Mensajes
            messages_elem = ET.SubElement(root, 'messages')
            for msg in messages:
                msg_elem = ET.SubElement(messages_elem, 'message')
                ET.SubElement(msg_elem, 'id').text = str(msg.id)
                ET.SubElement(msg_elem, 'role').text = msg.role
                ET.SubElement(msg_elem, 'content').text = msg.content
                ET.SubElement(msg_elem, 'timestamp').text = msg.timestamp.isoformat()

            # Formatear XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            return True, f"âœ… ConversaciÃ³n exportada a XML: {file_path}"
        except Exception as e:
            return False, f"âŒ Error al exportar XML: {str(e)}"

    def delete_conversation(self, conversation_id: int):
        """Eliminar conversaciÃ³n y sus mensajes"""
        try:
            conversation = self.session.query(Conversation).get(conversation_id)
            if conversation and conversation.user_id == self.user.id:
                self.session.delete(conversation)
                self.session.commit()

                if self.current_conversation_id == conversation_id:
                    self.current_conversation_id = None
                    self.current_file = None

                return True, "ConversaciÃ³n eliminada"
            return False, "ConversaciÃ³n no encontrada"
        except Exception as e:
            self.session.rollback()
            return False, f"Error al eliminar: {str(e)}"

    def close(self):
        """Cerrar sesiÃ³n de base de datos"""
        if self.session:
            self.session.close()

"""
Controlador principal de la aplicación
"""
from services.ia_service import IAService
from services.file_processor import FileProcessor
from db.orm import SessionLocal
from db.conversation_model import Conversation, ChatSession, Message
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
        self.current_session_id = None  # ID de la sesión actual
        self._create_new_session()

    def _create_new_session(self):
        """Crear nueva sesión de chat"""
        session = SessionLocal()
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            chat_session = ChatSession(
                user_id=self.user.id,
                title=f"Chat {timestamp}",
                created_at=datetime.now()
            )
            session.add(chat_session)
            session.commit()
            self.current_session_id = chat_session.id
            print(f"✅ Nueva sesión creada: ID {self.current_session_id}")
        except Exception as e:
            session.rollback()
            print(f"Error al crear sesión: {e}")
        finally:
            session.close()

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
        """Agregar mensaje al historial y guardar en BD"""
        timestamp = datetime.now()

        # Agregar a historial en memoria
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp.isoformat()
        })

        # Guardar en BD (nueva tabla Message)
        self._save_message_to_db(sender, message, timestamp)

    def _save_message_to_db(self, sender: str, content: str, timestamp: datetime):
        """Guardar mensaje individual en BD"""
        if not self.current_session_id:
            self._create_new_session()

        session = SessionLocal()
        try:
            msg = Message(
                session_id=self.current_session_id,
                sender=sender,
                content=content,
                timestamp=timestamp
            )
            session.add(msg)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error al guardar mensaje: {e}")
        finally:
            session.close()

    def save_to_db(self, question: str, response: str):
        """DEPRECATED - Mantener para compatibilidad"""
        pass  # Ya se guarda automáticamente en add_to_history

    def get_user_sessions(self):
        """Obtener todas las sesiones del usuario actual"""
        session = SessionLocal()
        try:
            sessions = session.query(ChatSession).filter_by(
                user_id=self.user.id
            ).order_by(ChatSession.created_at.desc()).all()

            return [s.to_dict() for s in sessions]
        except Exception as e:
            print(f"Error al obtener sesiones: {e}")
            return []
        finally:
            session.close()

    def load_session(self, session_id: int):
        """Cargar una sesión específica del historial"""
        session = SessionLocal()
        try:
            chat_session = session.query(ChatSession).filter_by(
                id=session_id,
                user_id=self.user.id
            ).first()

            if not chat_session:
                return False, "Sesión no encontrada"

            # Cargar mensajes
            messages = session.query(Message).filter_by(
                session_id=session_id
            ).order_by(Message.timestamp.asc()).all()

            # Actualizar historial en memoria
            self.conversation_history = [msg.to_dict() for msg in messages]
            self.current_session_id = session_id

            return True, self.conversation_history
        except Exception as e:
            print(f"Error al cargar sesión: {e}")
            return False, str(e)
        finally:
            session.close()

    def export_to_json(self, file_path: str = None, session_id: int = None):
        """Exportar conversación a JSON"""
        try:
            # Si no se especifica sesión, usar la actual
            if session_id is None:
                history = self.conversation_history
            else:
                success, history = self.load_session(session_id)
                if not success:
                    return False, "Error al cargar sesión"

            data = {
                'user': self.user.to_dict(),
                'export_date': datetime.now().isoformat(),
                'conversation': history
            }

            if not file_path:
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_dir = Path("exports")
                export_dir.mkdir(exist_ok=True)
                file_path = export_dir / f"chat_{self.user.codigo}_{timestamp}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True, f"✅ Conversación exportada a JSON: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar JSON: {str(e)}"

    def export_to_xml(self, file_path: str = None, session_id: int = None):
        """Exportar conversación a XML"""
        try:
            # Si no se especifica sesión, usar la actual
            if session_id is None:
                history = self.conversation_history
            else:
                success, history = self.load_session(session_id)
                if not success:
                    return False, "Error al cargar sesión"

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
            for msg in history:
                msg_elem = ET.SubElement(messages_elem, 'message')
                ET.SubElement(msg_elem, 'sender').text = msg['sender']
                ET.SubElement(msg_elem, 'content').text = msg['message'] if 'message' in msg else msg['content']
                ET.SubElement(msg_elem, 'timestamp').text = msg['timestamp']

            # Formatear XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            if not file_path:
                from pathlib import Path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_dir = Path("exports")
                export_dir.mkdir(exist_ok=True)
                file_path = export_dir / f"chat_{self.user.codigo}_{timestamp}.xml"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            return True, f"✅ Conversación exportada a XML: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar XML: {str(e)}"

    def clear_conversation(self):
        """Limpiar historial de conversación y crear nueva sesión"""
        self.conversation_history = []
        self.current_file = None
        self.ia_service.set_context("")
        self._create_new_session()  # Crear nueva sesión para el próximo chat

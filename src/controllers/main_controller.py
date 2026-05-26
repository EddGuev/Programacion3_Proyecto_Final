"""
Controlador Principal de ChatDoc
Maneja la lógica de la ventana principal (chat, archivos, exportación)
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime


class MainController:
    """
    Controlador de la ventana principal
    Maneja carga de archivos, mensajes y exportación
    """

    def __init__(self, user):
        """
        Inicializa el controlador

        Args:
            user: Objeto User del usuario autenticado
        """
        self.user = user
        self.current_file_content = None
        self.conversation_history = []

    def load_file(self, file_path: str) -> tuple[bool, str]:
        """
        Carga un archivo y extrae su contenido

        Args:
            file_path (str): Ruta del archivo

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_file_content = f.read()
                return True, "Archivo TXT cargado correctamente"

            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_file_content = json.dumps(data, indent=2)
                return True, "Archivo JSON cargado correctamente"

            elif file_path.endswith('.xml'):
                tree = ET.parse(file_path)
                root = tree.getroot()
                self.current_file_content = ET.tostring(root, encoding='unicode')
                return True, "Archivo XML cargado correctamente"

            elif file_path.endswith('.pdf'):
                # TODO: Implementar lectura de PDF con pdfplumber
                return False, "Lectura de PDF pendiente de implementar"

            else:
                return False, "Formato de archivo no soportado"

        except Exception as e:
            return False, f"Error al cargar archivo: {str(e)}"

    def process_message(self, message: str) -> str:
        """
        Procesa un mensaje del usuario y genera respuesta

        Args:
            message (str): Mensaje del usuario

        Returns:
            str: Respuesta del sistema
        """
        # Guardar en historial
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': self.user.id_usuario,
            'message': message,
            'type': 'user'
        })

        # TODO: Integrar con servicio de IA (Gemini o Mock)
        response = f"Respuesta simulada a: {message}"

        # Guardar respuesta en historial
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': 'Sistema',
            'message': response,
            'type': 'system'
        })

        return response

    def export_to_json(self, file_path: str) -> tuple[bool, str]:
        """
        Exporta la conversación a JSON

        Args:
            file_path (str): Ruta donde guardar el archivo

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            data = {
                'user': self.user.to_dict(),
                'export_date': datetime.now().isoformat(),
                'conversation': self.conversation_history
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True, f"Conversación exportada a {file_path}"
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

    def export_to_xml(self, file_path: str) -> tuple[bool, str]:
        """
        Exporta la conversación a XML

        Args:
            file_path (str): Ruta donde guardar el archivo

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            root = ET.Element('conversation')

            # Información del usuario
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
                ET.SubElement(msg_elem, 'timestamp').text = msg['timestamp']
                ET.SubElement(msg_elem, 'user').text = msg['user']
                ET.SubElement(msg_elem, 'type').text = msg['type']
                ET.SubElement(msg_elem, 'content').text = msg['message']

            # Guardar archivo
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)

            return True, f"Conversación exportada a {file_path}"
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

    def clear_conversation(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
        self.current_file_content = None

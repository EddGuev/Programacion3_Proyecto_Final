"""
Aplicación Principal de ChatDoc (ACTUALIZADO CON HISTORIAL)
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt

# Agregar src al path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from db.orm import init_db
from views.login_window import LoginWindow
from views.main_window import MainWindow
from controllers.chat_controller import ChatController


class ChatDocApp(QStackedWidget):
    """Aplicación principal con gestión de ventanas"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatDoc")
        self.resize(450, 550)

        # Inicializar base de datos
        init_db()

        # Crear ventana de login
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)

        # Agregar ventana de login al stack
        self.addWidget(self.login_window)

        # Variables para ventana principal
        self.main_window = None
        self.chat_controller = None

    def on_login_success(self, user):
        """Maneja el evento de login exitoso"""
        # Crear controlador de chat
        self.chat_controller = ChatController(user)

        # Crear ventana principal
        self.main_window = MainWindow(user)

        # Conectar señales de la ventana principal
        self.main_window.file_loaded.connect(self.on_file_loaded)
        self.main_window.message_sent.connect(self.on_message_sent)
        self.main_window.export_json.connect(self.on_export_json)
        self.main_window.export_xml.connect(self.on_export_xml)
        self.main_window.toggle_ia.connect(self.on_toggle_ia)
        self.main_window.logout.connect(self.on_logout)

        # NUEVAS SEÑALES PARA HISTORIAL
        self.main_window.new_conversation.connect(self.on_new_conversation)
        self.main_window.load_conversation.connect(self.on_load_conversation)

        # Agregar ventana principal al stack
        self.addWidget(self.main_window)

        # Cambiar a ventana principal
        self.setCurrentWidget(self.main_window)
        self.resize(1400, 800)

        # Cargar historial inicial
        self.refresh_history()

        # Crear primera conversación
        self.on_new_conversation()

    def on_new_conversation(self):
        """Crear nueva conversación"""
        conv_id = self.chat_controller.create_new_conversation()
        if conv_id:
            self.refresh_history()
            self.main_window.add_message("Sistema", "Nueva conversación iniciada. 🆕\n\nCarga un archivo para comenzar.")

    def on_load_conversation(self, conversation_id: int):
        """Cargar conversación existente"""
        messages = self.chat_controller.load_conversation(conversation_id)
        self.main_window.load_conversation_messages(messages)

    def refresh_history(self):
        """Actualizar lista de conversaciones"""
        conversations = self.chat_controller.get_user_conversations()
        self.main_window.update_history(conversations)

    def on_file_loaded(self, file_path: str):
        """Maneja la carga de archivos"""
        success, message = self.chat_controller.load_file(file_path)
        if success:
            self.main_window.add_message("Sistema", message)
            self.refresh_history()  # Actualizar título si cambió
        else:
            self.main_window.add_message("Sistema", f"Error: {message}")

    def on_message_sent(self, message: str):
        """Maneja el envío de mensajes"""
        response = self.chat_controller.process_message(message)
        self.main_window.add_message("IA", response)
        self.refresh_history()  # Actualizar timestamp

    def on_export_json(self):
        """Maneja la exportación a JSON"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como JSON",
            "conversacion.json",
            "JSON Files (*.json)"
        )

        if file_path:
            success, message = self.chat_controller.export_to_json(file_path)
            self.main_window.add_message("Sistema", message)

    def on_export_xml(self):
        """Maneja la exportación a XML"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como XML",
            "conversacion.xml",
            "XML Files (*.xml)"
        )

        if file_path:
            success, message = self.chat_controller.export_to_xml(file_path)
            self.main_window.add_message("Sistema", message)

    def on_toggle_ia(self):
        """Maneja el toggle de IA"""
        message = self.chat_controller.toggle_ia_mode()
        mode = self.chat_controller.get_ia_mode()
        self.main_window.update_ia_mode(mode)
        self.main_window.add_message("Sistema", message)

    def on_logout(self):
        """Maneja el cierre de sesión"""
        # Cerrar controlador
        if self.chat_controller:
            self.chat_controller.close()
            self.chat_controller = None

        # Remover ventana principal
        if self.main_window:
            self.removeWidget(self.main_window)
            self.main_window.deleteLater()
            self.main_window = None

        # Crear nueva ventana de login
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.addWidget(self.login_window)
        self.setCurrentWidget(self.login_window)
        self.resize(450, 550)


def main():
    """Función principal de entrada"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    chatdoc_app = ChatDocApp()
    chatdoc_app.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

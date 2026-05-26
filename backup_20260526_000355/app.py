"""
Aplicación Principal de ChatDoc
Punto de entrada con QStackedWidget para transición suave entre ventanas
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt

# Agregar src al path para importaciones absolutas
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from db.orm import init_db
from views.login_window import LoginWindow
from views.main_window import MainWindow
from controllers.main_controller import MainController


class ChatDocApp(QStackedWidget):
    """
    Aplicación principal con gestión de ventanas
    Usa QStackedWidget para transición suave sin cerrar ventanas
    """

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
        self.main_controller = None

    def on_login_success(self, user):
        """
        Maneja el evento de login exitoso

        Args:
            user: Objeto User autenticado
        """
        # Crear controlador principal
        self.main_controller = MainController(user)

        # Crear ventana principal
        self.main_window = MainWindow(user)

        # Conectar señales de la ventana principal
        self.main_window.file_loaded.connect(self.on_file_loaded)
        self.main_window.message_sent.connect(self.on_message_sent)
        self.main_window.export_json.connect(self.on_export_json)
        self.main_window.export_xml.connect(self.on_export_xml)
        self.main_window.clear_chat.connect(self.on_clear_chat)
        self.main_window.toggle_ia.connect(self.on_toggle_ia)
        self.main_window.logout.connect(self.on_logout)

        # Agregar ventana principal al stack
        self.addWidget(self.main_window)

        # Cambiar a ventana principal
        self.setCurrentWidget(self.main_window)
        self.resize(1000, 700)

    def on_file_loaded(self, file_path: str):
        """Maneja la carga de archivos"""
        success, message = self.main_controller.load_file(file_path)
        if success:
            self.main_window.add_message("Sistema", message)
        else:
            self.main_window.add_message("Sistema", f"Error: {message}")

    def on_message_sent(self, message: str):
        """Maneja el envío de mensajes"""
        response = self.main_controller.process_message(message)
        self.main_window.add_message("ChatDoc", response)

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
            success, message = self.main_controller.export_to_json(file_path)
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
            success, message = self.main_controller.export_to_xml(file_path)
            self.main_window.add_message("Sistema", message)

    def on_clear_chat(self):
        """Maneja la limpieza del chat"""
        self.main_controller.clear_conversation()

    def on_toggle_ia(self):
        """Maneja el toggle de IA"""
        message = self.main_controller.toggle_ia_mode()
        mode = self.main_controller.get_ia_mode()
        self.main_window.update_ia_mode(mode)
        self.main_window.add_message("Sistema", message)

    def on_logout(self):
        """Maneja el cierre de sesión"""
        # Limpiar controlador
        if self.main_controller:
            self.main_controller.clear_conversation()
            self.main_controller = None

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

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')

    # Crear y mostrar aplicación
    chatdoc_app = ChatDocApp()
    chatdoc_app.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

"""
Aplicación Principal de ChatDoc
Punto de entrada con QStackedWidget para transición suave entre ventanas
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt

# Imports absolutos
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
        self.addWidget(self.login_window)

        # Main window se crea después del login
        self.main_window = None
        self.controller = None

    def on_login_success(self, user_data):
        """Callback cuando el login es exitoso"""
        # Crear ventana principal y controlador
        self.main_window = MainWindow()
        self.controller = MainController(self.main_window, user_data)
        
        self.addWidget(self.main_window)
        self.setCurrentWidget(self.main_window)


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

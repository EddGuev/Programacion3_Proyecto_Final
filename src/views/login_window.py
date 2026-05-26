"""
Vista de Login/Registro para ChatDoc
Ventana dual que alterna entre modo Login y Registro
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


class LoginWindow(QWidget):
    """
    Ventana de Login/Registro con transición suave

    Señales:
        login_successful: Emitida cuando el login es exitoso (envía objeto User)
    """
    login_successful = pyqtSignal(object)  # Emite el objeto User

    def __init__(self):
        super().__init__()
        self.is_register_mode = False  # False = Login, True = Registro
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz gráfica"""
        self.setWindowTitle("ChatDoc - Iniciar Sesión")
        self.setFixedSize(450, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white; color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#btnPrimary {
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton#btnPrimary:hover {
                background-color: #45a049;
            }
            QPushButton#btnSecondary {
                background-color: transparent;
                color: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QPushButton#btnSecondary:hover {
                background-color: #e8f5e9;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Título
        self.title_label = QLabel("Iniciar Sesión")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #333;")
        main_layout.addWidget(self.title_label)

        # Subtítulo
        subtitle = QLabel("Bienvenido a ChatDoc")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(20)

        # Campos de entrada
        # Nombre completo (solo en modo registro)
        self.nombre_label = QLabel("Nombre Completo:")
        self.nombre_label.setStyleSheet("color: #333; font-weight: bold;")
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Juan Pérez García")
        self.nombre_label.hide()
        self.nombre_input.hide()

        # Código (solo en modo registro)
        self.codigo_label = QLabel("Código de Estudiante:")
        self.codigo_label.setStyleSheet("color: #333; font-weight: bold;")
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Ej: 123456789")
        self.codigo_label.hide()
        self.codigo_input.hide()

        # Usuario (siempre visible)
        usuario_label = QLabel("Usuario:")
        usuario_label.setStyleSheet("color: #333; font-weight: bold;")
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Ingresa tu usuario")

        # Contraseña (siempre visible)
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("color: #333; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Ingresa tu contraseña")

        # Agregar campos al layout
        main_layout.addWidget(self.nombre_label)
        main_layout.addWidget(self.nombre_input)
        main_layout.addWidget(self.codigo_label)
        main_layout.addWidget(self.codigo_input)
        main_layout.addWidget(usuario_label)
        main_layout.addWidget(self.usuario_input)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)

        main_layout.addSpacing(10)

        # Botón principal (Login/Registro)
        self.btn_primary = QPushButton("Iniciar Sesión")
        self.btn_primary.setObjectName("btnPrimary")
        self.btn_primary.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_primary.clicked.connect(self.handle_primary_action)
        main_layout.addWidget(self.btn_primary)

        # Separador
        separator_layout = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("background-color: #ddd;")
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #ddd;")
        separator_label = QLabel("o")
        separator_label.setStyleSheet("color: #999;")
        separator_layout.addWidget(line1)
        separator_layout.addWidget(separator_label)
        separator_layout.addWidget(line2)
        main_layout.addLayout(separator_layout)

        # Botón secundario (cambiar modo)
        self.btn_secondary = QPushButton("Crear cuenta nueva")
        self.btn_secondary.setObjectName("btnSecondary")
        self.btn_secondary.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_secondary.clicked.connect(self.toggle_mode)
        main_layout.addWidget(self.btn_secondary)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def toggle_mode(self):
        """Alterna entre modo Login y Registro"""
        self.is_register_mode = not self.is_register_mode

        if self.is_register_mode:
            # Cambiar a modo Registro
            self.title_label.setText("Crear Cuenta")
            self.btn_primary.setText("Registrarse")
            self.btn_secondary.setText("Ya tengo cuenta")
            self.nombre_label.show()
            self.nombre_input.show()
            self.codigo_label.show()
            self.codigo_input.show()
            self.setFixedSize(450, 700)
        else:
            # Cambiar a modo Login
            self.title_label.setText("Iniciar Sesión")
            self.btn_primary.setText("Iniciar Sesión")
            self.btn_secondary.setText("Crear cuenta nueva")
            self.nombre_label.hide()
            self.nombre_input.hide()
            self.codigo_label.hide()
            self.codigo_input.hide()
            self.setFixedSize(450, 550)

        # Limpiar campos
        self.clear_fields()

    def handle_primary_action(self):
        """Maneja el clic en el botón principal (Login o Registro)"""
        if self.is_register_mode:
            self.handle_register()
        else:
            self.handle_login()

    def handle_login(self):
        """Maneja el proceso de login"""
        usuario = self.usuario_input.text().strip()
        password = self.password_input.text()

        if not usuario or not password:
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos")
            return

        # Emitir señal para que el controlador maneje el login
        from ..controllers.login_controller import LoginController
        success, message, user = LoginController.login(usuario, password)

        if success:
            QMessageBox.information(self, "Éxito", message)
            self.login_successful.emit(user)  # Emitir señal con el usuario
        else:
            QMessageBox.warning(self, "Error", message)

    def handle_register(self):
        """Maneja el proceso de registro"""
        nombre = self.nombre_input.text().strip()
        codigo = self.codigo_input.text().strip()
        usuario = self.usuario_input.text().strip()
        password = self.password_input.text()

        if not all([nombre, codigo, usuario, password]):
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos")
            return

        # Emitir señal para que el controlador maneje el registro
        from ..controllers.login_controller import LoginController
        success, message = LoginController.register(nombre, codigo, usuario, password)

        if success:
            QMessageBox.information(self, "Éxito", message)
            self.toggle_mode()  # Volver a modo login
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_fields(self):
        """Limpia todos los campos de entrada"""
        self.nombre_input.clear()
        self.codigo_input.clear()
        self.usuario_input.clear()
        self.password_input.clear()

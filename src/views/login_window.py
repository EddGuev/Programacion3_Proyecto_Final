"""
Ventana de Login
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from controllers.login_controller import LoginController


class LoginWindow(QWidget):
    """Ventana de inicio de sesión"""

    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.controller = LoginController()
        self.init_ui()

    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle("ChatDoc - Login")
        self.setFixedSize(450, 550)

        # ESTILO GLOBAL - TODO EN NEGRO
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #000;
                font-size: 15px;
            }
            QLineEdit {
                padding: 14px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #fff;
                font-size: 15px;
                color: #000;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 14px;
                border: none;
                border-radius: 6px;
                font-size: 15px;
                font-weight: 600;
                color: #fff;
            }
            QPushButton#login {
                background-color: #4CAF50;
            }
            QPushButton#login:hover {
                background-color: #45a049;
            }
            QPushButton#register {
                background-color: #2196F3;
            }
            QPushButton#register:hover {
                background-color: #0b7dda;
            }
            QFrame#container {
                background-color: #fff;
                border-radius: 12px;
                border: 2px solid #e0e0e0;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        container = QFrame()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(15)

        title = QLabel("ChatDoc")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; font-size: 36px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        subtitle = QLabel("Sistema de Consulta de Documentos")
        subtitle.setStyleSheet("color: #000; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle)

        container_layout.addSpacing(15)

        # CAMPOS DE REGISTRO (se ocultan en modo login)
        self.lbl_nombre = QLabel("Nombre completo:")
        self.lbl_nombre.setStyleSheet("color: #000; font-weight: bold;")
        container_layout.addWidget(self.lbl_nombre)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej: Juan Pérez")
        container_layout.addWidget(self.txt_nombre)

        self.lbl_codigo = QLabel("Código:")
        self.lbl_codigo.setStyleSheet("color: #000; font-weight: bold;")
        container_layout.addWidget(self.lbl_codigo)

        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Ej: 123456789")
        container_layout.addWidget(self.txt_codigo)

        # CAMPOS COMUNES
        lbl_usuario = QLabel("Usuario:")
        lbl_usuario.setStyleSheet("color: #000; font-weight: bold;")
        container_layout.addWidget(lbl_usuario)

        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ej: juan.perez")
        container_layout.addWidget(self.txt_usuario)

        lbl_password = QLabel("Contraseña:")
        lbl_password.setStyleSheet("color: #000; font-weight: bold;")
        container_layout.addWidget(lbl_password)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("••••••••")
        self.txt_password.returnPressed.connect(self.login)
        container_layout.addWidget(self.txt_password)

        container_layout.addSpacing(10)

        # BOTONES
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_login = QPushButton("🔐 Iniciar Sesión")
        self.btn_login.setObjectName("login")
        self.btn_login.clicked.connect(self.login)
        btn_layout.addWidget(self.btn_login)

        self.btn_register = QPushButton("📝 Registrarse")
        self.btn_register.setObjectName("register")
        self.btn_register.clicked.connect(self.register)
        btn_layout.addWidget(self.btn_register)

        container_layout.addLayout(btn_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Iniciar en modo login (ocultar campos de registro)
        self.lbl_nombre.hide()
        self.txt_nombre.hide()
        self.lbl_codigo.hide()
        self.txt_codigo.hide()

    def login(self):
        """Manejar inicio de sesión"""
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        if not usuario or not password:
            self.show_message("Error", "Por favor completa todos los campos", QMessageBox.Icon.Warning)
            return

        success, message, user = self.controller.login(usuario, password)

        if success:
            self.login_successful.emit(user)
        else:
            self.show_message("Error de Login", message, QMessageBox.Icon.Critical)

    def register(self):
        """Manejar registro de nuevo usuario"""
        # Mostrar campos de registro
        self.lbl_nombre.show()
        self.txt_nombre.show()
        self.lbl_codigo.show()
        self.txt_codigo.show()

        nombre = self.txt_nombre.text().strip()
        codigo = self.txt_codigo.text().strip()
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        if not all([nombre, codigo, usuario, password]):
            self.show_message("Error", "Por favor completa todos los campos", QMessageBox.Icon.Warning)
            return

        success, message = self.controller.register(nombre, codigo, usuario, password)

        if success:
            self.show_message("Éxito", message + "\n\nYa puedes iniciar sesión.", QMessageBox.Icon.Information)
            self.clear_fields()
            # Ocultar campos de registro
            self.lbl_nombre.hide()
            self.txt_nombre.hide()
            self.lbl_codigo.hide()
            self.txt_codigo.hide()
        else:
            self.show_message("Error de Registro", message, QMessageBox.Icon.Critical)

    def show_message(self, title: str, message: str, icon):
        """Mostrar mensaje"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)

        # FORZAR TEXTO NEGRO
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fff;
            }
            QMessageBox QLabel {
                color: #000;
                font-size: 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                color: #000;
                background-color: #e0e0e0;
                padding: 10px 25px;
                font-size: 15px;
                border: 2px solid #999;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #ccc;
            }
        """)

        msg_box.exec()

    def clear_fields(self):
        """Limpiar campos"""
        self.txt_nombre.clear()
        self.txt_codigo.clear()
        self.txt_usuario.clear()
        self.txt_password.clear()

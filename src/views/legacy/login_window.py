from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor


class VentanaLogin(QWidget):
    login_exitoso = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._configurar_ventana()
        self._configurar_ui()
        self._animar_entrada()

    def _configurar_ventana(self):
        self.setWindowTitle("ChatDoc - Iniciar Sesión")
        self.setMinimumWidth(420)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QFrame#tarjeta {
                background-color: #24273a;
                border-radius: 16px;
                border: 1px solid #313244;
            }
            QLabel#titulo {
                font-size: 28px;
                font-weight: bold;
                color: #89b4fa;
                letter-spacing: 2px;
            }
            QLabel#subtitulo {
                font-size: 12px;
                color: #6c7086;
            }
            QLabel.etiqueta {
                font-size: 12px;
                color: #a6adc8;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1e1e2e;
                border: 1.5px solid #45475a;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 1.5px solid #89b4fa;
                background-color: #181825;
            }
            QLineEdit:hover {
                border: 1.5px solid #585b70;
            }
            QPushButton#btn_login {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton#btn_login:hover {
                background-color: #b4befe;
            }
            QPushButton#btn_login:pressed {
                background-color: #7287fd;
            }
            QPushButton#btn_registro {
                background-color: transparent;
                color: #89b4fa;
                border: none;
                font-size: 12px;
                padding: 4px;
            }
            QPushButton#btn_registro:hover {
                color: #b4befe;
            }
            QFrame#separador {
                background-color: #313244;
                max-height: 1px;
            }
        """)

    def _configurar_ui(self):
        # Layout principal centrado
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tarjeta central
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(35, 35, 35, 35)
        layout_tarjeta.setSpacing(14)

        # --- Encabezado ---
        titulo = QLabel("ChatDoc")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_tarjeta.addWidget(titulo)

        subtitulo = QLabel("Inicia sesión para continuar")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_tarjeta.addWidget(subtitulo)

        layout_tarjeta.addSpacing(8)

        # --- Campo Usuario ---
        lbl_usuario = QLabel("USUARIO")
        lbl_usuario.setProperty("class", "etiqueta")
        lbl_usuario.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout_tarjeta.addWidget(lbl_usuario)

        self.entrada_usuario = QLineEdit()
        self.entrada_usuario.setPlaceholderText("Ingresa tu usuario")
        self.entrada_usuario.setMinimumHeight(42)
        layout_tarjeta.addWidget(self.entrada_usuario)

        # --- Campo Contraseña ---
        lbl_pass = QLabel("CONTRASEÑA")
        lbl_pass.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout_tarjeta.addWidget(lbl_pass)

        self.entrada_pass = QLineEdit()
        self.entrada_pass.setPlaceholderText("Ingresa tu contraseña")
        self.entrada_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.entrada_pass.setMinimumHeight(42)
        # Permitir login con Enter
        self.entrada_pass.returnPressed.connect(self._emitir_enter)
        layout_tarjeta.addWidget(self.entrada_pass)

        layout_tarjeta.addSpacing(6)

        # --- Botón Login ---
        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setMinimumHeight(46)
        layout_tarjeta.addWidget(self.btn_login)

        # --- Separador ---
        separador = QFrame()
        separador.setObjectName("separador")
        separador.setFrameShape(QFrame.Shape.HLine)
        layout_tarjeta.addWidget(separador)

        # --- Botón Registro ---
        self.btn_registro = QPushButton("¿No tienes cuenta? Regístrate")
        self.btn_registro.setObjectName("btn_registro")
        self.btn_registro.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_tarjeta.addWidget(self.btn_registro)

        layout_principal.addWidget(tarjeta)
        self.adjustSize()

    def _animar_entrada(self):
        """Animación suave de opacidad al abrir."""
        self.setWindowOpacity(0.0)
        self.animacion = QPropertyAnimation(self, b"windowOpacity")
        self.animacion.setDuration(400)
        self.animacion.setStartValue(0.0)
        self.animacion.setEndValue(1.0)
        self.animacion.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animacion.start()

    def _emitir_enter(self):
        """Permite hacer login presionando Enter en el campo contraseña."""
        self.btn_login.click()

    # --- Métodos públicos para el Controlador ---

    def obtener_credenciales(self):
        return self.entrada_usuario.text().strip(), self.entrada_pass.text()

    def mostrar_error(self, mensaje: str):
        QMessageBox.critical(self, "Error de acceso", mensaje)

    def mostrar_exito(self, mensaje: str):
        QMessageBox.information(self, "¡Éxito!", mensaje)

    def limpiar_campos(self):
        self.entrada_usuario.clear()
        self.entrada_pass.clear()
        self.entrada_usuario.setFocus()
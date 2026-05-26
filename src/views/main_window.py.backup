"""
Ventana principal de ChatDoc
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QLineEdit, QPushButton, QFileDialog,
    QScrollArea, QFrame, QMessageBox, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction


class MainWindow(QWidget):
    """Ventana principal con chat, carga de archivos y exportación"""

    file_loaded = pyqtSignal(str)
    message_sent = pyqtSignal(str)
    export_json = pyqtSignal()
    export_xml = pyqtSignal()
    clear_chat = pyqtSignal()
    toggle_ia = pyqtSignal()
    logout = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle(f"ChatDoc - {self.user.nombre}")
        self.setGeometry(100, 100, 1200, 800)

        # ESTILO GLOBAL - TODO EN NEGRO
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #000;
            }
            QLabel {
                color: #000;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                color: #000;
            }
            QPushButton#primary {
                background-color: #4CAF50;
                color: #fff;
            }
            QPushButton#primary:hover {
                background-color: #45a049;
            }
            QPushButton#secondary {
                background-color: #2196F3;
                color: #fff;
            }
            QPushButton#secondary:hover {
                background-color: #0b7dda;
            }
            QPushButton#danger {
                background-color: #f44336;
                color: #fff;
            }
            QPushButton#danger:hover {
                background-color: #da190b;
            }
            QPushButton#toggle {
                background-color: #FF9800;
                color: #fff;
            }
            QPushButton#toggle:hover {
                background-color: #e68900;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #fff;
                font-size: 15px;
                color: #000;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: #fff;
                padding: 10px;
                font-size: 14px;
                color: #000;
            }
            QFrame#chat_container {
                background-color: #fff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: #fff;
                padding: 5px;
                font-size: 14px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #fff;
                padding: 8px 15px;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: #fff;
                color: #000;
                border: 2px solid #2c3e50;
                font-size: 14px;
            }
            QMenu::item {
                padding: 10px 30px;
                color: #000;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
                color: #000;
            }
            QMessageBox {
                background-color: #fff;
            }
            QMessageBox QLabel {
                color: #000;
                font-size: 15px;
            }
            QMessageBox QPushButton {
                color: #000;
                background-color: #e0e0e0;
                padding: 8px 20px;
                font-size: 14px;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Menú superior
        menu_bar = self.create_menu_bar()
        main_layout.addWidget(menu_bar)

        # Contenedor con padding
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Header
        header = self.create_header()
        content_layout.addWidget(header)

        # Toolbar
        toolbar = self.create_toolbar()
        content_layout.addWidget(toolbar)

        # Chat area
        chat_frame = QFrame()
        chat_frame.setObjectName("chat_container")
        chat_layout = QVBoxLayout(chat_frame)

        # Scroll area para mensajes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.chat_display = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_display)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)

        scroll.setWidget(self.chat_display)
        chat_layout.addWidget(scroll)

        content_layout.addWidget(chat_frame, stretch=1)

        # Input area
        input_area = self.create_input_area()
        content_layout.addWidget(input_area)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        # Mensaje de bienvenida
        self.add_message("Sistema", f"¡Bienvenido {self.user.nombre}! 👋\n\nCarga un archivo para comenzar.")

    def create_menu_bar(self):
        """Crear barra de menú"""
        menu_bar = QMenuBar()

        # Menú Sesión
        session_menu = QMenu("Sesión", self)

        logout_action = QAction("🚪 Cerrar Sesión", self)
        logout_action.triggered.connect(self.on_logout)
        session_menu.addAction(logout_action)

        change_user_action = QAction("👤 Cambiar Usuario", self)
        change_user_action.triggered.connect(self.on_change_user)
        session_menu.addAction(change_user_action)

        menu_bar.addMenu(session_menu)

        return menu_bar

    def create_header(self):
        """Crear header con título y usuario"""
        header = QFrame()
        header_layout = QHBoxLayout(header)

        title = QLabel("ChatDoc")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; font-size: 28px;")

        user_info = QLabel(f"👤 {self.user.nombre} ({self.user.codigo})")
        user_info.setStyleSheet("color: #000; font-size: 15px; font-weight: bold;")
        user_info.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)

        return header

    def create_toolbar(self):
        """Crear toolbar con botones de acción"""
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(10)

        # Botón cargar archivo
        btn_load = QPushButton("📁 Cargar Archivo")
        btn_load.setObjectName("primary")
        btn_load.clicked.connect(self.load_file)
        toolbar_layout.addWidget(btn_load)

        # Botón toggle IA
        self.btn_toggle_ia = QPushButton("🤖 Modo: Mock")
        self.btn_toggle_ia.setObjectName("toggle")
        self.btn_toggle_ia.clicked.connect(self.on_toggle_ia)
        toolbar_layout.addWidget(self.btn_toggle_ia)

        toolbar_layout.addStretch()

        # Botón exportar JSON
        btn_json = QPushButton("💾 Exportar JSON")
        btn_json.setObjectName("secondary")
        btn_json.clicked.connect(self.export_json.emit)
        toolbar_layout.addWidget(btn_json)

        # Botón exportar XML
        btn_xml = QPushButton("💾 Exportar XML")
        btn_xml.setObjectName("secondary")
        btn_xml.clicked.connect(self.export_xml.emit)
        toolbar_layout.addWidget(btn_xml)

        # Botón limpiar chat
        btn_clear = QPushButton("🗑️ Limpiar Chat")
        btn_clear.setObjectName("danger")
        btn_clear.clicked.connect(self.on_clear_chat)
        toolbar_layout.addWidget(btn_clear)

        return toolbar

    def create_input_area(self):
        """Crear área de entrada de mensajes"""
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe tu pregunta aquí...")
        self.input_field.returnPressed.connect(self.send_message)

        btn_send = QPushButton("Enviar ➤")
        btn_send.setObjectName("primary")
        btn_send.clicked.connect(self.send_message)
        btn_send.setFixedWidth(120)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(btn_send)

        return input_frame

    def load_file(self):
        """Abrir diálogo para cargar archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            "",
            "Archivos soportados (*.txt *.pdf *.json *.xml);;Todos los archivos (*.*)"
        )

        if file_path:
            self.file_loaded.emit(file_path)

    def send_message(self):
        """Enviar mensaje"""
        message = self.input_field.text().strip()

        if not message:
            return

        self.add_message("Tú", message)
        self.message_sent.emit(message)
        self.input_field.clear()

    def add_message(self, sender: str, message: str):
        """Agregar mensaje al chat - TEXTO NEGRO SIEMPRE"""
        msg_frame = QFrame()

        if sender == "Tú":
            msg_frame.setStyleSheet("""
                QFrame {
                    background-color: #E3F2FD;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 5px 50px 5px 5px;
                }
            """)
        elif sender == "Sistema":
            msg_frame.setStyleSheet("""
                QFrame {
                    background-color: #FFF9C4;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 5px;
                }
            """)
        else:
            msg_frame.setStyleSheet("""
                QFrame {
                    background-color: #F1F8E9;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 5px 5px 5px 50px;
                }
            """)

        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setSpacing(5)

        # Sender label - NEGRO
        sender_label = QLabel(f"<b>{sender}</b>")
        sender_label.setStyleSheet("color: #000; font-size: 13px;")
        msg_layout.addWidget(sender_label)

        # Message content - NEGRO GRANDE
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        content_label.setStyleSheet("color: #000; font-size: 15px; line-height: 1.6;")
        msg_layout.addWidget(content_label)

        self.chat_layout.addWidget(msg_frame)

        # Auto-scroll
        QTimer.singleShot(100, lambda: self.scroll_to_bottom())

    def scroll_to_bottom(self):
        """Scroll automático al final"""
        scroll_area = self.chat_display.parent().parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )

    def on_toggle_ia(self):
        """Manejar toggle de IA"""
        self.toggle_ia.emit()

    def update_ia_mode(self, mode: str):
        """Actualizar botón de modo IA"""
        self.btn_toggle_ia.setText(f"🤖 Modo: {mode}")

    def on_clear_chat(self):
        """Confirmar y limpiar chat - DIÁLOGO EN NEGRO"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar")
        msg_box.setText("¿Estás seguro de que quieres limpiar el chat?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # FORZAR TEXTO NEGRO EN MESSAGEBOX
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

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar widgets del chat
            while self.chat_layout.count():
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.clear_chat.emit()
            self.add_message("Sistema", "Chat limpiado. Carga un archivo para comenzar.")

    def on_logout(self):
        """Cerrar sesión - DIÁLOGO EN NEGRO"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cerrar Sesión")
        msg_box.setText("¿Estás seguro de que quieres cerrar sesión?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

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

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.logout.emit()
            self.close()

    def on_change_user(self):
        """Cambiar de usuario - DIÁLOGO EN NEGRO"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cambiar Usuario")
        msg_box.setText("¿Quieres cambiar de usuario? Se cerrará la sesión actual.")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

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

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.logout.emit()
            self.close()

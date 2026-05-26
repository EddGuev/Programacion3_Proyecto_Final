"""
Vista Principal de ChatDoc
Ventana de chat con historial colapsable y botón limpiar
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QListWidget, QFileDialog,
                             QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class MainWindow(QWidget):
    """
    Ventana principal de la aplicación ChatDoc

    Señales:
        file_loaded: Emitida cuando se carga un archivo (envía ruta)
        message_sent: Emitida cuando se envía un mensaje (envía texto)
        export_json: Emitida cuando se solicita exportar a JSON
        export_xml: Emitida cuando se solicita exportar a XML
        clear_chat: Emitida cuando se solicita limpiar el chat
    """
    file_loaded = pyqtSignal(str)
    message_sent = pyqtSignal(str)
    export_json = pyqtSignal()
    export_xml = pyqtSignal()
    clear_chat = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.history_visible = False
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz gráfica"""
        self.setWindowTitle(f"ChatDoc - {self.user.nombre}")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton#btnPrimary {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#btnPrimary:hover {
                background-color: #45a049;
            }
            QPushButton#btnSecondary {
                background-color: #2196F3;
                color: white;
            }
            QPushButton#btnSecondary:hover {
                background-color: #0b7dda;
            }
            QPushButton#btnDanger {
                background-color: #f44336;
                color: white;
            }
            QPushButton#btnDanger:hover {
                background-color: #da190b;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 13px;
            }
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
        """)

        # Layout principal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Panel lateral (historial) - inicialmente oculto
        self.history_panel = QWidget()
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(0, 0, 0, 0)

        history_title = QLabel("📚 Historial de Conversaciones")
        history_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 10px;")
        history_layout.addWidget(history_title)

        self.history_list = QListWidget()
        self.history_list.setMaximumWidth(250)
        history_layout.addWidget(self.history_list)

        self.history_panel.setLayout(history_layout)
        self.history_panel.hide()  # Oculto por defecto

        # Panel central (chat)
        chat_panel = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(15)

        # Barra superior
        top_bar = QHBoxLayout()

        # Botón para mostrar/ocultar historial
        self.btn_toggle_history = QPushButton("📚 Mostrar Historial")
        self.btn_toggle_history.setObjectName("btnSecondary")
        self.btn_toggle_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_history.clicked.connect(self.toggle_history)
        top_bar.addWidget(self.btn_toggle_history)

        # Botón limpiar chat
        btn_clear = QPushButton("🗑️ Limpiar Chat")
        btn_clear.setObjectName("btnDanger")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.confirm_clear_chat)
        top_bar.addWidget(btn_clear)

        top_bar.addStretch()

        # Etiqueta de usuario
        user_label = QLabel(f"👤 {self.user.nombre} ({self.user.codigo})")
        user_label.setStyleSheet("color: #666; font-size: 13px; padding: 5px;")
        top_bar.addWidget(user_label)

        chat_layout.addLayout(top_bar)

        # Área de chat
        chat_label = QLabel("💬 Conversación")
        chat_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        chat_layout.addWidget(chat_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Aquí aparecerán los mensajes...")
        chat_layout.addWidget(self.chat_display)

        # Área de entrada
        input_label = QLabel("✍️ Tu mensaje")
        input_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        chat_layout.addWidget(input_label)

        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Escribe tu pregunta aquí...")
        chat_layout.addWidget(self.message_input)

        # Botones de acción
        action_layout = QHBoxLayout()

        btn_load_file = QPushButton("📂 Cargar Archivo")
        btn_load_file.setObjectName("btnSecondary")
        btn_load_file.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_load_file.clicked.connect(self.load_file)
        action_layout.addWidget(btn_load_file)

        btn_send = QPushButton("📤 Enviar Mensaje")
        btn_send.setObjectName("btnPrimary")
        btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send.clicked.connect(self.send_message)
        action_layout.addWidget(btn_send)

        btn_export_json = QPushButton("📄 Exportar JSON")
        btn_export_json.setObjectName("btnSecondary")
        btn_export_json.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export_json.clicked.connect(self.export_json.emit)
        action_layout.addWidget(btn_export_json)

        btn_export_xml = QPushButton("📄 Exportar XML")
        btn_export_xml.setObjectName("btnSecondary")
        btn_export_xml.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export_xml.clicked.connect(self.export_xml.emit)
        action_layout.addWidget(btn_export_xml)

        chat_layout.addLayout(action_layout)

        chat_panel.setLayout(chat_layout)

        # Agregar paneles al layout principal
        main_layout.addWidget(self.history_panel)
        main_layout.addWidget(chat_panel)

        self.setLayout(main_layout)

    def toggle_history(self):
        """Muestra u oculta el panel de historial"""
        self.history_visible = not self.history_visible

        if self.history_visible:
            self.history_panel.show()
            self.btn_toggle_history.setText("📚 Ocultar Historial")
        else:
            self.history_panel.hide()
            self.btn_toggle_history.setText("📚 Mostrar Historial")

    def load_file(self):
        """Abre diálogo para cargar archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo",
            "",
            "Archivos Soportados (*.txt *.pdf *.json *.xml);;Todos los archivos (*.*)"
        )

        if file_path:
            self.file_loaded.emit(file_path)
            self.add_message("Sistema", f"Archivo cargado: {file_path}")

    def send_message(self):
        """Envía el mensaje escrito por el usuario"""
        message = self.message_input.toPlainText().strip()

        if not message:
            QMessageBox.warning(self, "Error", "Por favor escribe un mensaje")
            return

        self.add_message("Tú", message)
        self.message_sent.emit(message)
        self.message_input.clear()

    def add_message(self, sender: str, message: str):
        """
        Agrega un mensaje al área de chat

        Args:
            sender (str): Nombre del remitente
            message (str): Contenido del mensaje
        """
        formatted_message = f"<b>{sender}:</b> {message}<br>"
        self.chat_display.append(formatted_message)

    def confirm_clear_chat(self):
        """Confirma antes de limpiar el chat"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Estás seguro de que deseas limpiar el chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            self.clear_chat.emit()
            QMessageBox.information(self, "Éxito", "Chat limpiado correctamente")

    def update_history(self, conversations: list):
        """
        Actualiza la lista de historial

        Args:
            conversations (list): Lista de conversaciones
        """
        self.history_list.clear()
        for conv in conversations:
            self.history_list.addItem(f"Conversación {conv['id']} - {conv['date']}")

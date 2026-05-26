# src/views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog, 
    QFrame, QMessageBox, QMenuBar, QListWidget, QListWidgetItem,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

class VentanaPrincipal(QMainWindow):
    enviar_pregunta = pyqtSignal(str)
    solicitar_archivo = pyqtSignal()
    cambiar_modo_ia = pyqtSignal(str)
    export_json_requested = pyqtSignal()
    export_xml_requested = pyqtSignal()
    
    # NUEVAS SEÑALES
    nueva_conversacion_requested = pyqtSignal()
    cargar_conversacion_requested = pyqtSignal(int)
    cerrar_sesion_requested = pyqtSignal()
    salir_requested = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.modo_ia_actual = "simulacion"
        self.conversacion_actual_id = None
        self._configurar_ui()

    def _configurar_ui(self):
        self.setWindowTitle(f"ChatDoc - Sesion de {self.usuario}")
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI';")

        # MENU SUPERIOR
        self._crear_menu()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        # PANEL LATERAL IZQUIERDO (Historial)
        self.setup_historial_panel()

        # CONTENIDO CENTRAL (Chat)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #24273a; border-bottom: 1px solid #313244;")
        layout_h = QHBoxLayout(header)
        layout_h.setContentsMargins(10, 8, 10, 8)

        lbl_titulo = QLabel(f"Usuario: {self.usuario}")
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #89b4fa;")
        layout_h.addWidget(lbl_titulo)

        layout_h.addStretch()

        self.btn_archivo = QPushButton("📂 Cargar Archivo")
        self.btn_archivo.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px 15px; border-radius: 5px; font-weight: bold; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_archivo.clicked.connect(lambda: self.solicitar_archivo.emit())
        layout_h.addWidget(self.btn_archivo)

        content_layout.addWidget(header)

        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            background-color: #181825;
            border: none;
            padding: 20px;
            font-size: 14px;
            line-height: 1.5;
        """)
        content_layout.addWidget(self.chat_area)

        # Input area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.entrada_pregunta = QLineEdit()
        self.entrada_pregunta.setPlaceholderText("Escribe tu pregunta sobre el documento...")
        self.entrada_pregunta.setStyleSheet("""
            background-color: #313244; border: 1px solid #45475a;
            border-radius: 10px; padding: 12px; color: #cdd6f4;
        """)
        self.entrada_pregunta.returnPressed.connect(self._manejar_envio)
        input_layout.addWidget(self.entrada_pregunta)

        self.btn_enviar = QPushButton("Enviar")
        self.btn_enviar.setFixedSize(80, 42)
        self.btn_enviar.setStyleSheet("background-color: #89b4fa; border-radius: 10px; font-size: 14px; font-weight: bold;")
        self.btn_enviar.clicked.connect(self._manejar_envio)
        input_layout.addWidget(self.btn_enviar)

        content_layout.addWidget(input_frame)

        self.chat_widget = content_widget

        # PANEL LATERAL DERECHO (Opciones)
        self.setup_side_panel()

        # Layout principal
        main_layout.addWidget(self.historial_panel, 0)
        main_layout.addWidget(self.chat_widget, 1)
        main_layout.addWidget(self.side_panel, 0)

    def _crear_menu(self):
        """Crea el menu superior"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar { background-color: #24273a; color: #cdd6f4; padding: 5px; }
            QMenuBar::item:selected { background-color: #45475a; }
            QMenu { background-color: #24273a; color: #cdd6f4; }
            QMenu::item:selected { background-color: #45475a; }
        """)

        # Menu Conversacion
        menu_conv = menubar.addMenu("Conversacion")
        
        accion_nueva = QAction("Nueva Conversacion", self)
        accion_nueva.triggered.connect(lambda: self.nueva_conversacion_requested.emit())
        menu_conv.addAction(accion_nueva)

        menu_conv.addSeparator()

        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self._confirmar_salir)
        menu_conv.addAction(accion_salir)

        # Menu Sesion
        menu_sesion = menubar.addMenu("Sesion")
        
        accion_cerrar = QAction("Cerrar Sesion", self)
        accion_cerrar.triggered.connect(lambda: self.cerrar_sesion_requested.emit())
        menu_sesion.addAction(accion_cerrar)

    def setup_historial_panel(self):
        """Panel izquierdo con historial de conversaciones"""
        self.historial_panel = QWidget()
        self.historial_panel.setFixedWidth(250)
        self.historial_panel.setStyleSheet("background-color: #191a21; border: 1px solid #2a2b33;")
        
        layout = QVBoxLayout(self.historial_panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        lbl_titulo = QLabel("📜 Historial")
        lbl_titulo.setStyleSheet("color: #89b4fa; font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_titulo)

        self.lista_conversaciones = QListWidget()
        self.lista_conversaciones.setStyleSheet("""
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 5px;
                padding: 5px;
                color: #cdd6f4;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #45475a;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
        """)
        self.lista_conversaciones.itemClicked.connect(self._on_conversacion_seleccionada)
        layout.addWidget(self.lista_conversaciones)

    def setup_side_panel(self):
        """Panel derecho con opciones del sistema"""
        self.side_panel = QWidget()
        self.side_panel.setFixedWidth(220)
        self.side_panel.setStyleSheet("background-color: #191a21; border: 1px solid #2a2b33; padding: 10px;")
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(8, 8, 8, 8)
        self.side_layout.setSpacing(10)

        lbl_opciones = QLabel("⚙️ Opciones")
        lbl_opciones.setStyleSheet("color: #89b4fa; font-size: 14px; font-weight: bold;")
        self.side_layout.addWidget(lbl_opciones)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        self.side_layout.addWidget(sep)

        self.lbl_archivo = QLabel("Archivo: Ninguno")
        self.lbl_archivo.setStyleSheet("color: #cdd6f4; font-size: 12px;")
        self.side_layout.addWidget(self.lbl_archivo)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #313244;")
        self.side_layout.addWidget(sep2)

        self.lbl_modo_ia = QLabel("Modo IA: Simulacion")
        self.lbl_modo_ia.setStyleSheet("color: #f9e2af; font-size: 12px; font-weight: bold;")
        self.side_layout.addWidget(self.lbl_modo_ia)

        self.btn_cambiar_modo = QPushButton("Cambiar a REAL")
        self.btn_cambiar_modo.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; padding: 8px; border-radius: 6px; color: #1e1e2e; font-weight: bold; }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        self.btn_cambiar_modo.clicked.connect(self._toggle_modo_ia)
        self.side_layout.addWidget(self.btn_cambiar_modo)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.HLine)
        sep3.setStyleSheet("color: #313244;")
        self.side_layout.addWidget(sep3)

        self.btn_export_json = QPushButton("📄 Exportar JSON")
        self.btn_export_json.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px; border-radius: 6px; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_export_json.clicked.connect(lambda: self.export_json_requested.emit())
        self.side_layout.addWidget(self.btn_export_json)

        self.btn_export_xml = QPushButton("📄 Exportar XML")
        self.btn_export_xml.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px; border-radius: 6px; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_export_xml.clicked.connect(lambda: self.export_xml_requested.emit())
        self.side_layout.addWidget(self.btn_export_xml)

        self.side_layout.addStretch()

    def _toggle_modo_ia(self):
        if self.modo_ia_actual == "simulacion":
            self.modo_ia_actual = "real"
            self.lbl_modo_ia.setText("Modo IA: REAL")
            self.btn_cambiar_modo.setText("Cambiar a Simulacion")
            self.btn_cambiar_modo.setStyleSheet("""
                QPushButton { background-color: #f38ba8; padding: 8px; border-radius: 6px; color: #1e1e2e; font-weight: bold; }
                QPushButton:hover { background-color: #eba0ac; }
            """)
        else:
            self.modo_ia_actual = "simulacion"
            self.lbl_modo_ia.setText("Modo IA: Simulacion")
            self.btn_cambiar_modo.setText("Cambiar a REAL")
            self.btn_cambiar_modo.setStyleSheet("""
                QPushButton { background-color: #a6e3a1; padding: 8px; border-radius: 6px; color: #1e1e2e; font-weight: bold; }
                QPushButton:hover { background-color: #94e2d5; }
            """)
        
        self.cambiar_modo_ia.emit(self.modo_ia_actual)

    def _manejar_envio(self):
        texto = self.entrada_pregunta.text().strip()
        if texto:
            self.agregar_mensaje("Tu", texto, "#b4befe")
            self.entrada_pregunta.clear()
            self.enviar_pregunta.emit(texto)

    def _on_conversacion_seleccionada(self, item):
        """Cuando se selecciona una conversacion del historial"""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        if conv_id:
            self.cargar_conversacion_requested.emit(conv_id)

    def _confirmar_salir(self):
        """Confirmar antes de salir"""
        respuesta = QMessageBox.question(
            self, 
            "Salir", 
            "¿Estas seguro de que deseas salir de la aplicacion?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self.salir_requested.emit()

    def agregar_mensaje(self, autor, mensaje, color):
        self.chat_area.append(f"<b style='color: {color}'>{autor}:</b> {mensaje}<br>")

    def limpiar_chat(self):
        """Limpia el area de chat"""
        self.chat_area.clear()
        self.conversacion_actual_id = None

    def actualizar_historial(self, conversaciones: list):
        """Actualiza la lista de conversaciones
        conversaciones: lista de tuplas (id, fecha, archivo, num_mensajes)
        """
        self.lista_conversaciones.clear()
        for conv_id, fecha, archivo, num_msgs in conversaciones:
            archivo_corto = archivo.split("\\")[-1] if archivo else "Sin archivo"
            texto = f"{fecha[:16]} - {archivo_corto}\n{num_msgs} mensajes"
            
            item = QListWidgetItem(texto)
            item.setData(Qt.ItemDataRole.UserRole, conv_id)
            self.lista_conversaciones.addItem(item)

    def cargar_mensajes_conversacion(self, mensajes: list):
        """Carga mensajes de una conversacion anterior
        mensajes: lista de tuplas (emisor, texto, fecha_hora)
        """
        self.limpiar_chat()
        for emisor, texto, fecha_hora in mensajes:
            color = "#b4befe" if emisor == "usuario" else "#a6e3a1"
            autor = "Tu" if emisor == "usuario" else "A"
            self.agregar_mensaje(autor, texto, color)

    def seleccionar_archivo(self):
        file_filter = "Documentos (*.txt *.pdf *.json *.xml)"
        fname, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', file_filter)
        return fname

    def set_loaded_file(self, filename: str):
        if hasattr(self, "lbl_archivo"):
            display = filename if filename else "Ninguno"
            try:
                short = filename.split("\\")[-1]
            except Exception:
                short = filename
            self.lbl_archivo.setText(f"Archivo: {short}")

    def get_save_path(self, typ: str) -> str:
        if typ.lower() == "json":
            path, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", "", "JSON Files (*.json)")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar XML", "", "XML Files (*.xml)")
        return path or ""

    def mostrar_error(self, mensaje: str):
        QMessageBox.critical(self, "Error", mensaje)

    def mostrar_info(self, mensaje: str):
        QMessageBox.information(self, "Informacion", mensaje)

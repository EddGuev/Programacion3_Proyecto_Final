# src/controllers/main_controller.py
from PyQt6.QtCore import QObject
from views.main_window import VentanaPrincipal
from models.chat_model import ModeloChat
from datetime import datetime

class ControladorPrincipal(QObject):
    def __init__(self, usuario: str):
        super().__init__()
        self.usuario = usuario
        self.modelo = ModeloChat(usuario)
        self.vista = VentanaPrincipal(usuario)
        
        # Conectar señales existentes
        self.vista.enviar_pregunta.connect(self.procesar_pregunta)
        self.vista.solicitar_archivo.connect(self.cargar_archivo)
        self.vista.cambiar_modo_ia.connect(self.cambiar_modo_ia)
        self.vista.export_json_requested.connect(self.exportar_json)
        self.vista.export_xml_requested.connect(self.exportar_xml)
        
        # Conectar NUEVAS señales
        self.vista.nueva_conversacion_requested.connect(self.nueva_conversacion)
        self.vista.cargar_conversacion_requested.connect(self.cargar_conversacion)
        self.vista.cerrar_sesion_requested.connect(self.cerrar_sesion)
        self.vista.salir_requested.connect(self.salir_aplicacion)
        
        # Cargar historial al iniciar
        self.actualizar_historial()

    def mostrar(self):
        """Muestra la ventana principal"""
        self.vista.show()

    def procesar_pregunta(self, pregunta: str):
        """Procesa la pregunta del usuario"""
        try:
            respuesta = self.modelo.procesar_pregunta(pregunta)
            self.vista.agregar_mensaje("A", respuesta, "#a6e3a1")
            
            # Actualizar historial después de cada interacción
            self.actualizar_historial()
            
        except Exception as e:
            self.vista.mostrar_error(f"Error al procesar pregunta: {str(e)}")

    def cargar_archivo(self):
        """Carga un archivo seleccionado por el usuario"""
        try:
            ruta = self.vista.seleccionar_archivo()
            if ruta:
                self.modelo.cargar_archivo(ruta)
                self.vista.set_loaded_file(ruta)
                
                nombre_archivo = ruta.split("\\")[-1] if "\\" in ruta else ruta.split("/")[-1]
                self.vista.agregar_mensaje(
                    "Sistema", 
                    f"✅ Archivo '{nombre_archivo}' cargado correctamente ({len(self.modelo.contenido_archivo)} caracteres)",
                    "#f9e2af"
                )
                
                # Actualizar historial
                self.actualizar_historial()
                
        except Exception as e:
            self.vista.mostrar_error(f"Error al cargar archivo: {str(e)}")

    def cambiar_modo_ia(self, modo: str):
        """Cambia el modo de IA (simulacion/real)"""
        self.modelo.set_modo_ia(modo)
        modo_texto = "IA Real (Gemini)" if modo == "real" else "Simulación IA"
        self.vista.agregar_mensaje("Sistema", f"🔄 Modo de IA cambiado a: {modo_texto}", "#f9e2af")

    def exportar_json(self):
        """Exporta la conversación actual a JSON"""
        try:
            if not self.modelo.conversacion_id:
                self.vista.mostrar_error("No hay conversación activa para exportar")
                return
            
            ruta = self.vista.get_save_path("json")
            if ruta:
                self.modelo.exportar_json(ruta)
                self.vista.mostrar_info(f"Conversación exportada a:\n{ruta}")
        except Exception as e:
            self.vista.mostrar_error(f"Error al exportar JSON: {str(e)}")

    def exportar_xml(self):
        """Exporta la conversación actual a XML"""
        try:
            if not self.modelo.conversacion_id:
                self.vista.mostrar_error("No hay conversación activa para exportar")
                return
            
            ruta = self.vista.get_save_path("xml")
            if ruta:
                self.modelo.exportar_xml(ruta)
                self.vista.mostrar_info(f"Conversación exportada a:\n{ruta}")
        except Exception as e:
            self.vista.mostrar_error(f"Error al exportar XML: {str(e)}")

    # ========== NUEVAS FUNCIONALIDADES ==========

    def nueva_conversacion(self):
        """Inicia una nueva conversación"""
        try:
            # Limpiar chat
            self.vista.limpiar_chat()
            
            # Crear nueva conversación en el modelo
            self.modelo.nueva_conversacion()
            
            # Mensaje de bienvenida
            self.vista.agregar_mensaje(
                "Sistema",
                "✨ Nueva conversación iniciada. Carga un archivo para comenzar.",
                "#f9e2af"
            )
            
            # Actualizar historial
            self.actualizar_historial()
            
        except Exception as e:
            self.vista.mostrar_error(f"Error al crear nueva conversación: {str(e)}")

    def cargar_conversacion(self, conv_id: int):
        """Carga una conversación anterior del historial"""
        try:
            # Obtener mensajes de la conversación
            mensajes = self.modelo.obtener_mensajes_conversacion(conv_id)
            
            if not mensajes:
                self.vista.mostrar_error("No se encontraron mensajes en esta conversación")
                return
            
            # Cargar mensajes en la vista
            self.vista.cargar_mensajes_conversacion(mensajes)
            
            # Actualizar ID de conversación actual
            self.modelo.conversacion_id = conv_id
            self.vista.conversacion_actual_id = conv_id
            
            # Obtener info del archivo asociado
            archivo = self.modelo.obtener_archivo_conversacion(conv_id)
            if archivo:
                self.vista.set_loaded_file(archivo)
            
            self.vista.agregar_mensaje(
                "Sistema",
                f"📜 Conversación #{conv_id} cargada",
                "#f9e2af"
            )
            
        except Exception as e:
            self.vista.mostrar_error(f"Error al cargar conversación: {str(e)}")

    def actualizar_historial(self):
        """Actualiza el panel de historial con las conversaciones del usuario"""
        try:
            conversaciones = self.modelo.obtener_historial_conversaciones()
            self.vista.actualizar_historial(conversaciones)
        except Exception as e:
            print(f"Error al actualizar historial: {e}")

    def cerrar_sesion(self):
        """Cierra la sesión actual y vuelve al login"""
        from PyQt6.QtWidgets import QMessageBox
        
        respuesta = QMessageBox.question(
            self.vista,
            "Cerrar Sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            self.vista.close()
            
            # Importar y mostrar ventana de login
            from controllers.login_controller import ControladorLogin
            self.login_controller = ControladorLogin()
            self.login_controller.mostrar()

    def salir_aplicacion(self):
        """Cierra completamente la aplicación"""
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

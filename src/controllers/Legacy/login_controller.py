from views.login_window import VentanaLogin
import models.auth_model as auth_model
from controllers.main_controller import ControladorPrincipal

class ControladorLogin:
    def __init__(self):
        auth_model.inicializar_bd()
        self.vista = VentanaLogin()
        self.vista.btn_login.clicked.connect(self._manejar_login)
        self.vista.btn_registro.clicked.connect(self._manejar_registro)

    def mostrar(self):
        self.vista.show()

    def _manejar_login(self):
        usuario, clave = self.vista.obtener_credenciales()
        exito, mensaje = auth_model.validar_login(usuario, clave)
        if exito:
            self.vista.mostrar_exito(f"¡Bienvenido, {usuario}!")
            self._abrir_ventana_principal(usuario)
        else:
            self.vista.mostrar_error(mensaje)

    def _manejar_registro(self):
        usuario, clave = self.vista.obtener_credenciales()
        exito, mensaje = auth_model.registrar_usuario(usuario, clave)
        if exito:
            self.vista.mostrar_exito(mensaje + "\nYa puedes iniciar sesión.")
            self.vista.limpiar_campos()
        else:
            self.vista.mostrar_error(mensaje)

    def _abrir_ventana_principal(self, usuario: str):
        self.vista.close()
        self.main_ctrl = ControladorPrincipal(usuario)
        self.main_ctrl.mostrar()
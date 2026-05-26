"""
Controlador de Login para ChatDoc
Maneja la lógica de autenticación entre la vista y el servicio
"""
from ..services.auth_service import AuthService


class LoginController:
    """
    Controlador de autenticación
    Actúa como intermediario entre LoginWindow y AuthService
    """

    @staticmethod
    def login(id_usuario: str, password: str):
        """
        Procesa un intento de login

        Args:
            id_usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano

        Returns:
            tuple: (éxito, mensaje, usuario)
        """
        return AuthService.login_user(id_usuario, password)

    @staticmethod
    def register(nombre: str, codigo: str, id_usuario: str, password: str):
        """
        Procesa un intento de registro

        Args:
            nombre (str): Nombre completo
            codigo (str): Código de estudiante
            id_usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano

        Returns:
            tuple: (éxito, mensaje)
        """
        return AuthService.register_user(nombre, codigo, id_usuario, password)

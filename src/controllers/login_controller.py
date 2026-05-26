"""
Controlador de autenticación
"""
from services.auth_service import AuthService


class LoginController:
    """Controlador para login y registro"""

    @staticmethod
    def login(id_usuario: str, password: str):
        """Login con id_usuario"""
        try:
            user = AuthService.authenticate(id_usuario, password)
            if user:
                return True, "Login exitoso", user
            else:
                return False, "Usuario o contraseña incorrectos", None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    @staticmethod
    def register(nombre: str, codigo: str, id_usuario: str, password: str):
        """Registro completo"""
        try:
            if len(nombre) < 3:
                return False, "El nombre debe tener al menos 3 caracteres"

            if len(codigo) < 3:
                return False, "El código debe tener al menos 3 caracteres"

            if len(id_usuario) < 3:
                return False, "El ID de usuario debe tener al menos 3 caracteres"

            if len(password) < 6:
                return False, "La contraseña debe tener al menos 6 caracteres"

            user = AuthService.create_user(nombre, codigo, id_usuario, password)
            if user:
                return True, "Usuario registrado exitosamente"
            else:
                return False, "El código o ID de usuario ya existe"
        except Exception as e:
            return False, f"Error: {str(e)}"

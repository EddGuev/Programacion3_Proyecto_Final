"""
Servicio de Autenticación para ChatDoc
Maneja registro, login y hash de contraseñas
"""
import hashlib
from sqlalchemy.exc import IntegrityError
from ..db.orm import SessionLocal
from ..db.user_model import User


class AuthService:
    """
    Servicio de autenticación con métodos estáticos
    No requiere instanciación
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando SHA-256

        Args:
            password (str): Contraseña en texto plano

        Returns:
            str: Hash SHA-256 de 64 caracteres
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def register_user(nombre: str, codigo: str, id_usuario: str, password: str) -> tuple[bool, str]:
        """
        Registra un nuevo usuario en la base de datos

        Args:
            nombre (str): Nombre completo
            codigo (str): Código de estudiante
            id_usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano

        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        session = SessionLocal()
        try:
            # Validaciones básicas
            if not all([nombre, codigo, id_usuario, password]):
                return False, "Todos los campos son obligatorios"

            if len(password) < 6:
                return False, "La contraseña debe tener al menos 6 caracteres"

            # Crear usuario
            password_hash = AuthService.hash_password(password)
            new_user = User(
                nombre=nombre,
                codigo=codigo,
                id_usuario=id_usuario,
                password_hash=password_hash
            )

            session.add(new_user)
            session.commit()

            return True, f"Usuario '{id_usuario}' registrado exitosamente"

        except IntegrityError as e:
            session.rollback()
            if 'codigo' in str(e):
                return False, f"El código '{codigo}' ya está registrado"
            elif 'id_usuario' in str(e):
                return False, f"El usuario '{id_usuario}' ya existe"
            else:
                return False, "Error al registrar usuario"
        except Exception as e:
            session.rollback()
            return False, f"Error inesperado: {str(e)}"
        finally:
            session.close()

    @staticmethod
    def login_user(id_usuario: str, password: str) -> tuple[bool, str, User | None]:
        """
        Autentica un usuario

        Args:
            id_usuario (str): Nombre de usuario
            password (str): Contraseña en texto plano

        Returns:
            tuple[bool, str, User | None]: (éxito, mensaje, objeto_usuario)
        """
        session = SessionLocal()
        try:
            # Buscar usuario
            user = session.query(User).filter_by(id_usuario=id_usuario).first()

            if not user:
                return False, "Usuario no encontrado", None

            # Verificar contraseña
            password_hash = AuthService.hash_password(password)
            if user.password_hash != password_hash:
                return False, "Contraseña incorrecta", None

            return True, f"Bienvenido, {user.nombre}", user

        except Exception as e:
            return False, f"Error al iniciar sesión: {str(e)}", None
        finally:
            session.close()

    @staticmethod
    def user_exists(id_usuario: str) -> bool:
        """
        Verifica si un usuario existe

        Args:
            id_usuario (str): Nombre de usuario

        Returns:
            bool: True si existe, False si no
        """
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(id_usuario=id_usuario).first()
            return user is not None
        finally:
            session.close()

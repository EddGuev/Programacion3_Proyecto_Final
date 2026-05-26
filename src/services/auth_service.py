"""
Servicio de autenticación
"""
import hashlib
from datetime import datetime
from db.orm import SessionLocal
from db.user_model import User


class AuthService:
    """Servicio para autenticación"""

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate(id_usuario: str, password: str):
        """Autenticar usuario por id_usuario"""
        session = SessionLocal()
        try:
            hashed_password = AuthService.hash_password(password)
            user = session.query(User).filter(
                User.id_usuario == id_usuario,
                User.password_hash == hashed_password
            ).first()
            return user
        finally:
            session.close()

    @staticmethod
    def create_user(nombre: str, codigo: str, id_usuario: str, password: str):
        """Crear nuevo usuario completo"""
        session = SessionLocal()
        try:
            # Verificar si ya existe
            existing = session.query(User).filter(
                (User.codigo == codigo) | (User.id_usuario == id_usuario)
            ).first()
            if existing:
                return None

            hashed_password = AuthService.hash_password(password)
            new_user = User(
                nombre=nombre,
                codigo=codigo,
                id_usuario=id_usuario,
                password_hash=hashed_password,
                created_at=datetime.now()
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

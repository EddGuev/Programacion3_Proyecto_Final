"""
Modelo de Usuario para ChatDoc
Representa la tabla 'users' en la base de datos SQLite
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .orm import Base


class User(Base):
    """
    Modelo de Usuario con campos completos para registro

    Atributos:
        id (int): Identificador único autoincrementable
        nombre (str): Nombre completo del usuario
        codigo (str): Código de estudiante (único)
        id_usuario (str): Nombre de usuario para login (único)
        password_hash (str): Contraseña hasheada con SHA-256
    """
    __tablename__ = 'users'

    # Campos de la tabla
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    id_usuario = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)  # SHA-256 = 64 caracteres

    # Relación con conversaciones (preparado para futuro)
    # conversations = relationship("Conversation", back_populates="user")

    def __repr__(self):
        """Representación en string del usuario"""
        return f"<User(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo}', usuario='{self.id_usuario}')>"

    def to_dict(self):
        """Convierte el usuario a diccionario (útil para JSON)"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'id_usuario': self.id_usuario
            # NO incluimos password_hash por seguridad
        }

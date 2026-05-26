"""
Modelo de Usuario para ChatDoc
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.orm import Base


class User(Base):
    """Modelo de Usuario completo"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False)
    id_usuario = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'id_usuario': self.id_usuario,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

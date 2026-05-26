"""
Modelos actualizados para ChatDoc con sesiones de chat
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.orm import Base


class ChatSession(Base):
    """Sesión de chat (agrupa múltiples mensajes)"""
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)  # "Chat 26/05/2026 12:30"
    created_at = Column(DateTime, default=datetime.now)

    # Relación con mensajes
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'message_count': len(self.messages)
        }


class Message(Base):
    """Mensaje individual dentro de una sesión"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    sender = Column(String(50), nullable=False)  # "Usuario", "ChatDoc", "Sistema"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    # Relación con sesión
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender='{self.sender}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


# MANTENER Conversation para compatibilidad (migración gradual)
class Conversation(Base):
    """Modelo antiguo de conversación (DEPRECATED - usar ChatSession + Message)"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"

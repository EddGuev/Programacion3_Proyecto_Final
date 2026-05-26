"""
Modelo de Mensaje para SQLite
Almacena mensajes individuales de cada conversaciÃ³n
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from db.orm import Base


class Message(Base):
    """Modelo de mensaje individual"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

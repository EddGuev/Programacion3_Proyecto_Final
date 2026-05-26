"""
Modelo de Conversación para SQLite
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from db.orm import Base


class Conversation(Base):
    """Modelo de conversación"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"

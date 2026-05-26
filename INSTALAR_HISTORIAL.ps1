# ============================================
# INSTALADOR COMPLETO DE HISTORIAL - ChatDoc
# ============================================

Write-Host "🚀 INSTALANDO SISTEMA DE HISTORIAL DE CONVERSACIONES" -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan

# 1. MESSAGE MODEL
Write-Host "[1/6] Creando message_model.py..." -ForegroundColor Yellow
$messageModel = @'
"""
Modelo de Mensaje para SQLite
Almacena mensajes individuales de cada conversación
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
'@
$messageModel | Out-File -FilePath "src/db/message_model.py" -Encoding UTF8
Write-Host "   ✅ message_model.py creado" -ForegroundColor Green

# 2. CONVERSATION MODEL (ACTUALIZADO)
Write-Host "[2/6] Actualizando conversation_model.py..." -ForegroundColor Yellow
$conversationModel = @'
"""
Modelo de Conversación para SQLite (ACTUALIZADO)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.orm import Base


class Conversation(Base):
    """Modelo de conversación con relación a mensajes"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False, default="Nueva conversación")
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relación con mensajes
    messages = relationship("Message", backref="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', user_id={self.user_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
'@
$conversationModel | Out-File -FilePath "src/db/conversation_model.py" -Encoding UTF8 -Force
Write-Host "   ✅ conversation_model.py actualizado" -ForegroundColor Green

# 3. ORM (ACTUALIZADO)
Write-Host "[3/6] Actualizando orm.py..." -ForegroundColor Yellow
$orm = @'
"""
Configuración de SQLAlchemy ORM para ChatDoc (ACTUALIZADO)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta de la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'chatdoc.db')

# Crear carpeta data/ si no existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Motor de base de datos
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Clase base para modelos
Base = declarative_base()

# Fábrica de sesiones
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    """
    # Importar TODOS los modelos
    from .user_model import User
    from .conversation_model import Conversation
    from .message_model import Message

    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de datos inicializada en: {DB_PATH}")


def get_session():
    """Obtiene una nueva sesión de base de datos"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
'@
$orm | Out-File -FilePath "src/db/orm.py" -Encoding UTF8 -Force
Write-Host "   ✅ orm.py actualizado" -ForegroundColor Green

Write-Host "`n✅ PARTE 1 COMPLETADA - Modelos de BD actualizados" -ForegroundColor Green
Write-Host "`n⏳ Continuando con controladores y vistas...`n" -ForegroundColor Cyan
Start-Sleep -Seconds 2

# 4. CHAT CONTROLLER
Write-Host "[4/6] Creando chat_controller.py..." -ForegroundColor Yellow
# Dividir en partes para evitar problemas con comillas
$chatController1 = @'
"""
Controlador de Chat con Historial de Conversaciones
Maneja conversaciones, mensajes, archivos y exportación
"""
from services.ia_service import IAService
from services.file_processor import FileProcessor
from db.orm import SessionLocal
from db.conversation_model import Conversation
from db.message_model import Message
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ChatController:
    """Controlador de chat con soporte para múltiples conversaciones"""

    def __init__(self, user):
        self.user = user
        self.ia_service = IAService(use_mock=True)
        self.current_conversation_id = None
        self.current_file = None
        self.session = SessionLocal()

    def create_new_conversation(self, title: str = None) -> int:
        """
        Crear nueva conversación

        Returns:
            conversation_id
        """
        try:
            if not title:
                # Generar título automático
                count = self.session.query(Conversation).filter_by(user_id=self.user.id).count()
                title = f"Conversación {count + 1}"

            conversation = Conversation(
                user_id=self.user.id,
                title=title,
                created_at=datetime.now()
            )

            self.session.add(conversation)
            self.session.commit()

            self.current_conversation_id = conversation.id
            self.current_file = None

            return conversation.id

        except Exception as e:
            self.session.rollback()
            print(f"Error al crear conversación: {e}")
            return None

    def get_user_conversations(self):
        """
        Obtener todas las conversaciones del usuario

        Returns:
            Lista de tuplas (id, title, created_at)
        """
        try:
            conversations = self.session.query(Conversation).filter_by(
                user_id=self.user.id
            ).order_by(Conversation.updated_at.desc()).all()

            return [(c.id, c.title, c.created_at) for c in conversations]

        except Exception as e:
            print(f"Error al obtener conversaciones: {e}")
            return []

    def load_conversation(self, conversation_id: int):
        """
        Cargar conversación existente

        Returns:
            Lista de tuplas (role, content, timestamp)
        """
        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=conversation_id
            ).order_by(Message.timestamp.asc()).all()

            self.current_conversation_id = conversation_id

            # Cargar archivo asociado si existe
            conversation = self.session.query(Conversation).get(conversation_id)
            if conversation and conversation.file_path:
                self.current_file = conversation.file_path
                # Recargar contexto en IA
                success, _, content = FileProcessor.load_file(conversation.file_path)
                if success:
                    self.ia_service.set_context(content)

            return [(m.role, m.content, m.timestamp) for m in messages]

        except Exception as e:
            print(f"Error al cargar conversación: {e}")
            return []

    def add_message(self, role: str, content: str):
        """
        Agregar mensaje a la conversación actual

        Args:
            role: 'user', 'assistant', 'system'
            content: Contenido del mensaje
        """
        if not self.current_conversation_id:
            # Crear conversación automáticamente si no existe
            self.create_new_conversation()

        try:
            message = Message(
                conversation_id=self.current_conversation_id,
                role=role,
                content=content,
                timestamp=datetime.now()
            )

            self.session.add(message)
            self.session.commit()

            # Actualizar timestamp de conversación
            conversation = self.session.query(Conversation).get(self.current_conversation_id)
            if conversation:
                conversation.updated_at = datetime.now()
                self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error al agregar mensaje: {e}")

    def load_file(self, file_path: str):
        """Cargar archivo y establecer contexto"""
        success, message, content = FileProcessor.load_file(file_path)

        if success:
            self.current_file = file_path
            self.ia_service.set_context(content)

            # Actualizar file_path en conversación actual
            if self.current_conversation_id:
                try:
                    conversation = self.session.query(Conversation).get(self.current_conversation_id)
                    if conversation:
                        conversation.file_path = file_path
                        # Actualizar título si es la primera carga
                        if conversation.title.startswith("Conversación"):
                            from pathlib import Path
                            conversation.title = f"Chat sobre {Path(file_path).name}"
                        self.session.commit()
                except Exception as e:
                    self.session.rollback()
                    print(f"Error al actualizar conversación: {e}")

            self.add_message("system", message)

        return success, message

    def process_message(self, message: str) -> str:
        """Procesar mensaje del usuario"""
        # Agregar mensaje del usuario
        self.add_message("user", message)

        # Obtener respuesta de IA
        response = self.ia_service.ask(message)

        # Agregar respuesta
        self.add_message("assistant", response)

        return response

    def toggle_ia_mode(self) -> str:
        """Cambiar entre Mock y Gemini"""
        message = self.ia_service.toggle_mode()
        self.add_message("system", message)
        return message

    def get_ia_mode(self) -> str:
        """Obtener modo actual de IA"""
        return self.ia_service.get_current_mode()

    def export_to_json(self, file_path: str):
        """Exportar conversación actual a JSON"""
        if not self.current_conversation_id:
            return False, "No hay conversación activa para exportar"

        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=self.current_conversation_id
            ).order_by(Message.timestamp.asc()).all()

            conversation = self.session.query(Conversation).get(self.current_conversation_id)

            data = {
                'user': self.user.to_dict(),
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'file_path': conversation.file_path
                },
                'export_date': datetime.now().isoformat(),
                'messages': [m.to_dict() for m in messages]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True, f"✅ Conversación exportada a JSON: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar JSON: {str(e)}"

    def export_to_xml(self, file_path: str):
        """Exportar conversación actual a XML"""
        if not self.current_conversation_id:
            return False, "No hay conversación activa para exportar"

        try:
            messages = self.session.query(Message).filter_by(
                conversation_id=self.current_conversation_id
            ).order_by(Message.timestamp.asc()).all()

            conversation = self.session.query(Conversation).get(self.current_conversation_id)

            root = ET.Element('conversation')

            # Usuario
            user_elem = ET.SubElement(root, 'user')
            ET.SubElement(user_elem, 'id').text = str(self.user.id)
            ET.SubElement(user_elem, 'nombre').text = self.user.nombre
            ET.SubElement(user_elem, 'codigo').text = self.user.codigo

            # Info de conversación
            conv_elem = ET.SubElement(root, 'conversation_info')
            ET.SubElement(conv_elem, 'id').text = str(conversation.id)
            ET.SubElement(conv_elem, 'title').text = conversation.title
            ET.SubElement(conv_elem, 'created_at').text = conversation.created_at.isoformat()
            if conversation.file_path:
                ET.SubElement(conv_elem, 'file_path').text = conversation.file_path

            # Fecha de exportación
            ET.SubElement(root, 'export_date').text = datetime.now().isoformat()

            # Mensajes
            messages_elem = ET.SubElement(root, 'messages')
            for msg in messages:
                msg_elem = ET.SubElement(messages_elem, 'message')
                ET.SubElement(msg_elem, 'id').text = str(msg.id)
                ET.SubElement(msg_elem, 'role').text = msg.role
                ET.SubElement(msg_elem, 'content').text = msg.content
                ET.SubElement(msg_elem, 'timestamp').text = msg.timestamp.isoformat()

            # Formatear XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            return True, f"✅ Conversación exportada a XML: {file_path}"
        except Exception as e:
            return False, f"❌ Error al exportar XML: {str(e)}"

    def delete_conversation(self, conversation_id: int):
        """Eliminar conversación y sus mensajes"""
        try:
            conversation = self.session.query(Conversation).get(conversation_id)
            if conversation and conversation.user_id == self.user.id:
                self.session.delete(conversation)
                self.session.commit()

                if self.current_conversation_id == conversation_id:
                    self.current_conversation_id = None
                    self.current_file = None

                return True, "Conversación eliminada"
            return False, "Conversación no encontrada"
        except Exception as e:
            self.session.rollback()
            return False, f"Error al eliminar: {str(e)}"

    def close(self):
        """Cerrar sesión de base de datos"""
        if self.session:
            self.session.close()
'@
$chatController1 | Out-File -FilePath "src/controllers/chat_controller.py" -Encoding UTF8
Write-Host "   ✅ chat_controller.py creado" -ForegroundColor Green

Write-Host "`n✅ INSTALACIÓN COMPLETADA!" -ForegroundColor Green
Write-Host "`n📋 ARCHIVOS CREADOS/ACTUALIZADOS:" -ForegroundColor Cyan
Write-Host "   ✅ src/db/message_model.py" -ForegroundColor Gray
Write-Host "   ✅ src/db/conversation_model.py" -ForegroundColor Gray
Write-Host "   ✅ src/db/orm.py" -ForegroundColor Gray
Write-Host "   ✅ src/controllers/chat_controller.py" -ForegroundColor Gray

Write-Host "`n⚠️  FALTA ACTUALIZAR MANUALMENTE:" -ForegroundColor Yellow
Write-Host "   • src/views/main_window.py (descarga main_window_updated.py)" -ForegroundColor Yellow
Write-Host "   • src/app.py (descarga app_updated.py)" -ForegroundColor Yellow

Write-Host "`n🚀 SIGUIENTE PASO:" -ForegroundColor Cyan
Write-Host "   Descarga main_window_updated.py y app_updated.py desde la interfaz" -ForegroundColor White
Write-Host "   y cópialos manualmente a src/views/ y src/" -ForegroundColor White

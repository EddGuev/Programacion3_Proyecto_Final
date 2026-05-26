"""
Configuración de SQLAlchemy ORM para ChatDoc
Maneja la conexión a la base de datos SQLite
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
    Debe llamarse al inicio de la aplicación
    """
    from .user_model import User  # Importar modelos aquí para evitar imports circulares
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de datos inicializada en: {DB_PATH}")


def get_session():
    """
    Obtiene una nueva sesión de base de datos
    Usar con context manager: with get_session() as session:
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

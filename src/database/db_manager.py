# src/database/db_manager.py
import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="chatdoc.db"):
        self.db_path = db_path
        self.inicializar_db()

    def inicializar_db(self):
        """Crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                fecha_inicio TEXT DEFAULT CURRENT_TIMESTAMP,
                archivo TEXT,
                FOREIGN KEY (usuario) REFERENCES usuarios(username)
            )
        ''')
        
        # Tabla de mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversacion_id INTEGER NOT NULL,
                emisor TEXT NOT NULL,
                texto TEXT NOT NULL,
                fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Base de datos inicializada")

    def crear_usuario(self, username: str, password: str) -> bool:
        """Crea un nuevo usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def validar_usuario(self, username: str, password: str) -> bool:
        """Valida las credenciales de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        )
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None

    def crear_conversacion(self, usuario: str) -> int:
        """Crea una nueva conversación y retorna su ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversaciones (usuario) VALUES (?)",
            (usuario,)
        )
        conv_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conv_id

    def actualizar_archivo_conversacion(self, conv_id: int, archivo: str):
        """Actualiza el archivo asociado a una conversación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversaciones SET archivo = ? WHERE id = ?",
            (archivo, conv_id)
        )
        conn.commit()
        conn.close()

    def guardar_mensaje(self, conversacion_id: int, emisor: str, texto: str):
        """Guarda un mensaje en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensajes (conversacion_id, emisor, texto) VALUES (?, ?, ?)",
            (conversacion_id, emisor, texto)
        )
        conn.commit()
        conn.close()

    def obtener_mensajes(self, conversacion_id: int) -> list:
        """Obtiene todos los mensajes de una conversación
        Retorna: lista de tuplas (emisor, texto, fecha_hora)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emisor, texto, fecha_hora FROM mensajes WHERE conversacion_id = ? ORDER BY id ASC",
            (conversacion_id,)
        )
        mensajes = cursor.fetchall()
        conn.close()
        return mensajes

    def obtener_conversaciones_usuario(self, usuario: str) -> list:
        """Obtiene todas las conversaciones de un usuario
        Retorna: lista de tuplas (id, fecha_inicio, archivo, num_mensajes)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.id,
                c.fecha_inicio,
                c.archivo,
                COUNT(m.id) as num_mensajes
            FROM conversaciones c
            LEFT JOIN mensajes m ON c.id = m.conversacion_id
            WHERE c.usuario = ?
            GROUP BY c.id
            ORDER BY c.fecha_inicio DESC
        ''', (usuario,))
        conversaciones = cursor.fetchall()
        conn.close()
        return conversaciones

    def obtener_archivo_conversacion(self, conv_id: int) -> str:
        """Obtiene el archivo asociado a una conversación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT archivo FROM conversaciones WHERE id = ?",
            (conv_id,)
        )
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None

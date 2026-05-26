# src/db/api.py
from .orm import _conn, DEFAULT_DB, init_db
from datetime import datetime
import json
import xml.etree.ElementTree as ET

init_db()


def create_conversation(file_name: str = None) -> int:
    """Crea una nueva conversación y retorna su ID."""
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO conversations (file_name, created_at) VALUES (?, ?)",
            (file_name, datetime.utcnow())
        )
        conn.commit()
        return cur.lastrowid


def add_message(conversation_id: int, sender: str, text: str, timestamp: datetime = None) -> int:
    """Agrega un mensaje a una conversación."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO messages (conversation_id, sender, content, created_at) VALUES (?, ?, ?, ?)",
            (conversation_id, sender, text, timestamp)
        )
        conn.commit()
        return cur.lastrowid


def get_conversation(conversation_id: int) -> dict:
    """Obtiene una conversación con todos sus mensajes."""
    with _conn() as conn:
        # Obtener conversación
        conv_row = conn.execute(
            "SELECT id, file_name FROM conversations WHERE id = ?",
            (conversation_id,)
        ).fetchone()
        
        if not conv_row:
            return None
        
        # Obtener mensajes
        msg_rows = conn.execute(
            "SELECT sender, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,)
        ).fetchall()
        
        data = {
            "conversacion_id": conv_row["id"],
            "archivo": conv_row["file_name"],
            "mensajes": [
                {
                    "emisor": m["sender"],
                    "texto": m["content"],
                    "fecha_hora": str(m["created_at"]) if m["created_at"] else ""
                }
                for m in msg_rows
            ]
        }
        return data


def export_conversation_json(conversation_id: int, out_path: str):
    """Exporta una conversación a JSON."""
    data = get_conversation(conversation_id)
    if data is None:
        raise ValueError("Conversación no encontrada")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_conversation_xml(conversation_id: int, out_path: str):
    """Exporta una conversación a XML."""
    data = get_conversation(conversation_id)
    if data is None:
        raise ValueError("Conversación no encontrada")
    
    root = ET.Element("conversacion", attrib={"id": str(data["conversacion_id"])})
    
    archivo_el = ET.SubElement(root, "archivo")
    archivo_el.text = data["archivo"] or ""
    
    mensajes_el = ET.SubElement(root, "mensajes")
    
    for m in data["mensajes"]:
        msg_el = ET.SubElement(mensajes_el, "mensaje", attrib={"emisor": m["emisor"]})
        texto_el = ET.SubElement(msg_el, "texto")
        texto_el.text = m["texto"]
        fecha_el = ET.SubElement(msg_el, "fecha_hora")
        fecha_el.text = m["fecha_hora"]
    
    tree = ET.ElementTree(root)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)

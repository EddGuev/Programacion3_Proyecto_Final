from .orm import SessionLocal, init_db
from .models import Conversation, Message
from datetime import datetime
import json
import xml.etree.ElementTree as ET

init_db()


def create_conversation(file_name: str = None) -> int:
    db = SessionLocal()
    conv = Conversation(file_name=file_name)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    conv_id = conv.id
    db.close()
    return conv_id


def add_message(conversation_id: int, sender: str, text: str, timestamp: datetime = None) -> int:
    db = SessionLocal()
    if timestamp is None:
        timestamp = datetime.utcnow()

    msg = Message(
        conversation_id=conversation_id,
        sender=sender,
        text=text,
        timestamp=timestamp
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    msg_id = msg.id
    db.close()
    return msg_id


def get_conversation(conversation_id: int) -> dict:
    db = SessionLocal()
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if not conv:
        db.close()
        return None

    data = {
        "conversacion_id": conv.id,
        "archivo": conv.file_name,
        "mensajes": [
            {
                "emisor": m.sender,
                "texto": m.text,
                "fecha_hora": m.timestamp.isoformat()
            }
            for m in sorted(conv.messages, key=lambda m: m.timestamp)
        ]
    }
    db.close()
    return data


def export_conversation_json(conversation_id: int, out_path: str):
    data = get_conversation(conversation_id)
    if data is None:
        raise ValueError("Conversación no encontrada")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_conversation_xml(conversation_id: int, out_path: str):
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
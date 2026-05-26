import sys
sys.path.insert(0, 'src')
from db.orm import SessionLocal
from db.conversation_model import Message, ChatSession

session = SessionLocal()

# Ver sesiones
sessions = session.query(ChatSession).all()
print(f'📊 Sesiones creadas: {len(sessions)}')
for s in sessions:
    print(f'   - ID {s.id}: {s.title}')

# Ver mensajes
messages = session.query(Message).all()
print(f'\n💬 Mensajes guardados: {len(messages)}')
for m in messages:
    print(f'   - {m.sender}: {m.content[:60]}...')

session.close()

# src/models/auth_model.py
from db.orm import _conn
import hashlib
import secrets


def inicializar_bd():
    """Ya se inicializa desde orm.py, esta función es por compatibilidad."""
    from db.orm import init_db
    init_db()


def _hashear_password(password: str, salt: str = None) -> tuple[str, str]:
    """Encripta la contraseña con salt para seguridad."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    
    return password_hash, salt


def registrar_usuario(usuario: str, password: str) -> tuple[bool, str]:
    """Registra un nuevo usuario en la BD."""
    if not usuario or not password:
        return False, "Usuario y contraseña son obligatorios."
    
    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres."

    try:
        password_hash, salt = _hashear_password(password)
        
        with _conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (usuario, password_hash, salt)
            )
            conn.commit()
        
        return True, "Registro exitoso."
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return False, f"El nombre de usuario '{usuario}' ya está en uso."
        return False, f"Error al registrar: {str(e)}"


def validar_login(usuario: str, password: str) -> tuple[bool, str]:
    """Comprueba si las credenciales son correctas."""
    if not usuario or not password:
        return False, "Usuario y contraseña son obligatorios."
    
    with _conn() as conn:
        row = conn.execute(
            "SELECT password_hash, salt FROM users WHERE username = ?",
            (usuario,)
        ).fetchone()
    
    if not row:
        return False, "Usuario o contraseña incorrectos."
    
    stored_hash = row["password_hash"]
    salt = row["salt"]
    
    # Verificar contraseña
    password_hash, _ = _hashear_password(password, salt)
    
    if password_hash == stored_hash:
        return True, "Acceso correcto."
    
    return False, "Usuario o contraseña incorrectos."

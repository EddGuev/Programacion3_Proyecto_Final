from src.database import db_api

class LoginController:
    def __init__(self, db_path=None):
        self.db_path = db_path
        db_api.init_db(self.db_path) if self.db_path else db_api.init_db()

    def handle_login(self, username, password):
        if not username or not password: return False, "Campos incompletos."
        user = db_api.authenticate_user(username, password, self.db_path)
        return (True, user) if user else (False, "Credenciales inválidas.")

    def handle_register(self, username, password):
        try:
            db_api.create_user(username, password, self.db_path)
            return True, "Registro exitoso."
        except:
            return False, "El usuario ya existe."

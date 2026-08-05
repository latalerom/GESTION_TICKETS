from models import Usuario
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from services.mail_service import MailService
from services.ticket_event_broker import ticket_event_broker


class AuthService:
    PROFILE_FIELDS = ("nombre", "telefono", "cargo", "bio", "foto_perfil")
    TEMPORARY_PASSWORD = "Soporte1234"

    def __init__(self, mail_service=None):
        self.mail_service = mail_service or MailService()

    def authenticate(self, email, password):
        if not email or not password:
            return None

        user = Usuario.query.filter_by(email=email).first()

        if user is None or not user.activo:
            return None

        if self.password_matches(user.password, password):
            return user

        return None

    def get_user_by_id(self, user_id):
        if user_id is None:
            return None

        return Usuario.query.get(user_id)

    def password_matches(self, stored_password, plain_password):
        if stored_password.startswith("scrypt:") or stored_password.startswith("pbkdf2:"):
            return check_password_hash(stored_password, plain_password)

        return stored_password == plain_password

    def update_profile(self, user, data):
        if user is None:
            raise ValueError("Usuario invalido")

        # Solo se aceptan campos de perfil; rol, correo y estado activo quedan protegidos.
        for field in self.PROFILE_FIELDS:
            if field in data:
                setattr(user, field, data.get(field))

        return user

    def list_users(self, current_user):
        if current_user is None or not current_user.is_admin():
            raise PermissionError("Solo administradores pueden ver usuarios")

        return Usuario.query.order_by(Usuario.rol.asc(), Usuario.nombre.asc(), Usuario.email.asc()).all()

    def reset_password(self, current_user, user_id):
        if current_user is None or not current_user.is_admin():
            raise PermissionError("Solo administradores pueden restablecer contrasenas")

        user = Usuario.query.get(user_id)

        if user is None:
            raise ValueError("Usuario no encontrado")

        if not user.activo:
            raise ValueError("No puedes restablecer la contrasena de un usuario inactivo")

        user.password = generate_password_hash(self.TEMPORARY_PASSWORD)
        sent = self.mail_service.send_password_reset(user.email, self.TEMPORARY_PASSWORD)

        ticket_event_broker.publish("activity", {
            "action": "user_password_reset",
            "message": f"{current_user.nombre} restablecio la contrasena de {user.email}",
            "user": current_user.to_dict(),
            "target_user": user.to_dict(),
            "visibility": "admins",
        })

        return user, sent, self.TEMPORARY_PASSWORD

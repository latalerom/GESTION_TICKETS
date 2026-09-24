from secrets import token_urlsafe
import re

from models import Usuario
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from services.mail_service import MailService
from services.ticket_event_broker import ticket_event_broker


class AuthService:
    PROFILE_FIELDS = ("nombre", "telefono", "cargo", "bio", "foto_perfil")
    PROFILE_MAX_LENGTHS = {
        "nombre": 100,
        "telefono": 30,
        "cargo": 100,
        "bio": 1000,
        "foto_perfil": 1300000,
    }
    IMAGE_DATA_RE = re.compile(r"^data:image/(png|jpe?g|webp|gif);base64,[A-Za-z0-9+/=\s]+$")

    def __init__(self, mail_service=None):
        self.mail_service = mail_service or MailService()

    def authenticate(self, email, password):
        if not email or not password:
            return None

        email = self.normalize_email(email)
        user = Usuario.query.filter_by(email=email).first()

        if user is None or not user.activo:
            return None

        if self.password_matches(user.password, password):
            return user

        return None

    def get_user_by_id(self, user_id):
        if user_id is None:
            return None

        user = Usuario.query.get(user_id)

        if user is None or not user.activo:
            return None

        return user

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
                value = self.clean_text(data.get(field))
                self.validate_profile_length(field, value)
                setattr(user, field, value)

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

        temporary_password = self.generate_temporary_password()
        user.password = generate_password_hash(temporary_password)
        sent = self.mail_service.send_password_reset(user.email, temporary_password)

        if not sent:
            return user, False

        ticket_event_broker.publish("activity", {
            "action": "user_password_reset",
            "message": f"{current_user.nombre} restablecio la contrasena de {user.email}",
            "user": current_user.to_dict(),
            "target_user": user.to_dict(),
            "visibility": "admins",
        })

        return user, sent

    def set_user_active(self, current_user, user_id, active):
        if current_user is None or not current_user.is_admin():
            raise PermissionError("Solo administradores pueden cambiar el acceso de usuarios")

        user = Usuario.query.get(user_id)

        if user is None:
            raise ValueError("Usuario no encontrado")

        if user.id == current_user.id and not active:
            raise ValueError("No puedes revocar tu propio acceso")

        if not active and user.is_admin():
            active_admins = Usuario.query.filter_by(rol="admin", activo=True).count()
            if active_admins <= 1:
                raise ValueError("Debe permanecer al menos un administrador activo")

        if user.activo == active:
            return user, False

        user.activo = active
        action = "reactivo" if active else "revoco el acceso de"
        ticket_event_broker.publish("activity", {
            "action": "user_access_updated",
            "message": f"{current_user.nombre} {action} {user.email}",
            "user": current_user.to_dict(),
            "target_user": user.to_dict(),
            "visibility": "admins",
        })

        return user, True

    def generate_temporary_password(self):
        return f"Soporte-{token_urlsafe(9)}"

    def normalize_email(self, value):
        return str(value).strip().lower()

    def clean_text(self, value):
        if value is None:
            return None

        return str(value).strip()

    def validate_profile_length(self, field, value):
        max_length = self.PROFILE_MAX_LENGTHS.get(field)

        if max_length is not None and value is not None and len(value) > max_length:
            raise ValueError(f"{field} no puede superar {max_length} caracteres")

        if field == "foto_perfil" and value is not None and not self.IMAGE_DATA_RE.match(value):
            raise ValueError("La foto de perfil debe ser una imagen valida")

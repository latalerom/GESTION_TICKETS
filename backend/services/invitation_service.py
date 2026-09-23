from datetime import datetime, timedelta
import re
from secrets import token_urlsafe

from flask import current_app
from werkzeug.security import generate_password_hash

from models import InvitacionUsuario, Usuario, db
from services.mail_service import MailService
from services.ticket_event_broker import ticket_event_broker


class InvitationService:
    VALID_ROLES = {"admin", "cliente"}
    EMAIL_MAX_LENGTH = 254
    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, mail_service=None):
        self.mail_service = mail_service or MailService()

    def create_invitation(self, email, rol, invited_by, created_ip=None):
        if not invited_by.is_admin():
            raise PermissionError("Solo un administrador puede invitar usuarios")

        email = self.normalize_email(email)
        rol = self.clean_text(rol)

        if not email:
            raise ValueError("El correo es obligatorio")

        self.validate_email(email)

        if rol not in self.VALID_ROLES:
            raise ValueError("Rol invalido")

        existing_user = Usuario.query.filter_by(email=email).first()
        if existing_user is not None:
            raise ValueError("Ya existe un usuario con este correo")

        now = datetime.utcnow()
        invitation = InvitacionUsuario(
            email=email,
            rol=rol,
            token=token_urlsafe(32),
            invitado_por_id=invited_by.id,
            creada_en=now,
            expira_en=now + timedelta(hours=24),
            creada_ip=created_ip,
        )

        db.session.add(invitation)
        db.session.commit()

        link = f"{current_app.config['APP_URL']}/register.html?token={invitation.token}"
        sent = self.mail_service.send_invitation(email, link)
        email_error = self.mail_service.last_error

        payload = {
            "action": "user_invited",
            "message": f"{invited_by.nombre} invito a {email}",
            "user": invited_by.to_dict(),
            "invitation": invitation.to_dict(),
            "visibility": "admins",
        }
        ticket_event_broker.publish("activity", payload)

        return invitation, link, sent, email_error

    def get_invitation(self, token):
        invitation = InvitacionUsuario.query.filter_by(token=token).first()

        if invitation is None or not invitation.is_available(datetime.utcnow()):
            return None

        return invitation

    def register_user(
        self,
        token,
        nombre,
        password,
        telefono=None,
        cargo=None,
        bio=None,
        privacy_accepted=False,
        terms_accepted=False,
    ):
        invitation = self.get_invitation(token)

        if invitation is None:
            raise ValueError("La invitacion no existe o ya expiro")

        nombre = self.clean_text(nombre)
        telefono = self.clean_text(telefono)
        cargo = self.clean_text(cargo)
        bio = self.clean_text(bio)

        if not nombre or not password:
            raise ValueError("Nombre y contrasena son obligatorios")

        if privacy_accepted is not True or terms_accepted is not True:
            raise ValueError("Debes aceptar la politica de privacidad y los terminos de uso")

        self.validate_length("nombre", nombre, 100)
        self.validate_length("telefono", telefono, 30)
        self.validate_length("cargo", cargo, 100)
        self.validate_length("bio", bio, 1000)
        self.validate_password(password)

        existing_user = Usuario.query.filter_by(email=invitation.email).first()
        if existing_user is not None:
            raise ValueError("Ya existe un usuario con este correo")

        user = Usuario(
            nombre=nombre,
            email=invitation.email,
            password=generate_password_hash(password),
            rol=invitation.rol,
            telefono=telefono,
            cargo=cargo,
            bio=bio,
        )

        invitation.usada = True
        invitation.usada_en = datetime.utcnow()

        db.session.add(user)
        db.session.commit()

        payload = {
            "action": "user_registered",
            "message": f"{user.nombre} completo su registro",
            "user": user.to_dict(),
            "visibility": "admins",
        }
        ticket_event_broker.publish("activity", payload)

        return user

    def normalize_email(self, value):
        return self.clean_text(value).lower() if value is not None else None

    def clean_text(self, value):
        if value is None:
            return None

        return str(value).strip()

    def validate_email(self, email):
        if len(email) > self.EMAIL_MAX_LENGTH:
            raise ValueError(f"El correo no puede superar {self.EMAIL_MAX_LENGTH} caracteres")

        if not self.EMAIL_RE.match(email):
            raise ValueError("Correo invalido")

    def validate_length(self, field, value, max_length):
        if value is not None and len(value) > max_length:
            raise ValueError(f"{field} no puede superar {max_length} caracteres")

    def validate_password(self, password):
        password = str(password)

        if len(password) < 8:
            raise ValueError("La contrasena debe tener al menos 8 caracteres")

        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValueError("La contrasena debe incluir letras y numeros")

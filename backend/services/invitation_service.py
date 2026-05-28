from datetime import datetime, timedelta
from secrets import token_urlsafe

from flask import current_app
from werkzeug.security import generate_password_hash

from models import InvitacionUsuario, Usuario, db
from services.mail_service import MailService
from services.ticket_event_broker import ticket_event_broker


class InvitationService:
    VALID_ROLES = {"admin", "cliente"}

    def __init__(self, mail_service=None):
        self.mail_service = mail_service or MailService()

    def create_invitation(self, email, rol, invited_by):
        if not invited_by.is_admin():
            raise PermissionError("Solo un administrador puede invitar usuarios")

        if not email:
            raise ValueError("El correo es obligatorio")

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
            creada_en=now,
            expira_en=now + timedelta(hours=24),
        )

        db.session.add(invitation)
        db.session.commit()

        link = f"{current_app.config['APP_URL']}/register.html?token={invitation.token}"
        sent = self.mail_service.send_invitation(email, link)

        payload = {
            "action": "user_invited",
            "message": f"{invited_by.nombre} invito a {email}",
            "user": invited_by.to_dict(),
            "invitation": invitation.to_dict(),
            "visibility": "admins",
        }
        ticket_event_broker.publish("activity", payload)

        return invitation, link, sent

    def get_invitation(self, token):
        invitation = InvitacionUsuario.query.filter_by(token=token).first()

        if invitation is None or not invitation.is_available(datetime.utcnow()):
            return None

        return invitation

    def register_user(self, token, nombre, password):
        invitation = self.get_invitation(token)

        if invitation is None:
            raise ValueError("La invitacion no existe o ya expiro")

        if not nombre or not password:
            raise ValueError("Nombre y contrasena son obligatorios")

        existing_user = Usuario.query.filter_by(email=invitation.email).first()
        if existing_user is not None:
            raise ValueError("Ya existe un usuario con este correo")

        user = Usuario(
            nombre=nombre,
            email=invitation.email,
            password=generate_password_hash(password),
            rol=invitation.rol,
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

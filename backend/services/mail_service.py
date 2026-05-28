import smtplib
from email.message import EmailMessage

from flask import current_app


class MailService:
    def send_invitation(self, email, link):
        subject = "Invitacion al Sistema de Soporte"
        body = (
            "Hola,\n\n"
            "Has sido invitado al Sistema de Soporte.\n"
            f"Completa tu registro desde este enlace:\n{link}\n\n"
            "Si no esperabas esta invitacion, puedes ignorar este mensaje."
        )

        return self.send(email, subject, body)

    def send(self, recipient, subject, body):
        server = current_app.config.get("MAIL_SERVER")

        if not server:
            print("Correo no enviado porque MAIL_SERVER no esta configurado.")
            print(f"Para: {recipient}")
            print(f"Asunto: {subject}")
            print(body)
            return False

        message = EmailMessage()
        message["From"] = current_app.config["MAIL_SENDER"]
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(server, current_app.config["MAIL_PORT"]) as smtp:
            if current_app.config["MAIL_USE_TLS"]:
                smtp.starttls()

            username = current_app.config.get("MAIL_USERNAME")
            password = current_app.config.get("MAIL_PASSWORD")

            if username and password:
                smtp.login(username, password)

            smtp.send_message(message)

        return True

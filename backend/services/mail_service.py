import smtplib
from email.message import EmailMessage
from html import escape

from flask import current_app


class MailService:
    def __init__(self):
        self.last_error = None

    def send_invitation(self, email, link):
        subject = "Invitacion al Sistema de Soporte"
        body = self.invitation_text(link)
        html = self.invitation_html(link)

        return self.send(email, subject, body, html)

    def invitation_text(self, link):
        return (
            "Hola,\n\n"
            "Has sido invitado al Sistema de Soporte.\n"
            f"Completa tu registro desde este enlace:\n{link}\n\n"
            "Este enlace vence en 24 horas.\n\n"
            "Si no esperabas esta invitacion, puedes ignorar este mensaje."
        )

    def invitation_html(self, link):
        safe_link = escape(link, quote=True)

        return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invitacion al Sistema de Soporte</title>
</head>
<body style="margin:0; padding:0; background:#F8FAFC; color:#1F2937; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F8FAFC; margin:0; padding:32px 14px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:590px; background:#FFFFFF; border:1px solid #E5E7EB; border-radius:10px; overflow:hidden; box-shadow:0 16px 34px rgba(15, 23, 42, 0.08);">
                    <tr>
                        <td style="background:#007C7A; padding:24px 26px; color:#FFFFFF;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td style="width:46px;">
                                        <span style="display:inline-block; width:42px; height:42px; line-height:42px; border-radius:8px; background:#FFFFFF; color:#00B8B4; font-weight:800; text-align:center;">TF</span>
                                    </td>
                                    <td>
                                        <strong style="display:block; font-size:18px;">TicketFlow</strong>
                                        <span style="display:block; margin-top:3px; color:#E6F7F7; font-size:13px;">Mesa de ayuda laboral</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:32px 26px 8px;">
                            <p style="margin:0 0 8px; color:#00B8B4; font-size:12px; font-weight:800; letter-spacing:.04em; text-transform:uppercase;">Invitacion de acceso</p>
                            <h1 style="margin:0 0 12px; color:#1F2937; font-size:27px; line-height:1.2; font-weight:800;">Completa tu registro</h1>
                            <p style="margin:0; color:#6B7280; font-size:15px; line-height:1.55;">Te invitaron a crear una cuenta para registrar, consultar y hacer seguimiento a solicitudes internas de oficina.</p>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="padding:22px 26px 18px;">
                            <a href="{safe_link}" style="display:inline-block; border-radius:8px; background:#00B8B4; color:#FFFFFF; font-size:15px; font-weight:800; padding:14px 22px; text-decoration:none;">Crear mi cuenta</a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:0 26px 28px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #E5E7EB; border-radius:8px; background:#E6F7F7;">
                                <tr>
                                    <td style="padding:15px 16px;">
                                        <strong style="display:block; margin-bottom:5px; color:#1F2937; font-size:14px;">Enlace valido por 24 horas</strong>
                                        <p style="margin:0; color:#6B7280; font-size:13px; line-height:1.45;">Si el boton no abre, copia este enlace en tu navegador:</p>
                                        <p style="margin:10px 0 0; color:#005F73; font-size:12px; line-height:1.5; word-break:break-all;">{safe_link}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="border-top:1px solid #E5E7EB; padding:16px 26px; color:#6B7280; font-size:12px; line-height:1.45;">
                            Si no esperabas esta invitacion, puedes ignorar este mensaje.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def send_password_reset(self, email, temporary_password):
        subject = "Contrasena temporal del Sistema de Soporte"
        body = (
            "Hola,\n\n"
            "Un administrador restablecio tu contrasena en el Sistema de Soporte.\n"
            f"Tu contrasena temporal es: {temporary_password}\n\n"
            "Usala para ingresar temporalmente al sistema.\n"
            "Por seguridad, comunicate con el administrador si necesitas cambiarla despues del ingreso.\n"
            "Si no esperabas este cambio, comunicate con el administrador."
        )
        html = self.password_reset_html(temporary_password)

        return self.send(email, subject, body, html)

    def password_reset_html(self, temporary_password):
        safe_password = escape(temporary_password)

        return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrasena temporal</title>
</head>
<body style="margin:0; padding:0; background:#F8FAFC; color:#1F2937; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F8FAFC; margin:0; padding:32px 14px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:590px; background:#FFFFFF; border:1px solid #E5E7EB; border-radius:10px; overflow:hidden; box-shadow:0 16px 34px rgba(15, 23, 42, 0.08);">
                    <tr>
                        <td style="background:#005F73; padding:24px 26px; color:#FFFFFF;">
                            <strong style="display:block; font-size:18px;">TicketFlow</strong>
                            <span style="display:block; margin-top:3px; color:#E6F7F7; font-size:13px;">Seguridad de cuenta</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:32px 26px 12px;">
                            <p style="margin:0 0 8px; color:#FF4D4F; font-size:12px; font-weight:800; letter-spacing:.04em; text-transform:uppercase;">Restablecimiento de contrasena</p>
                            <h1 style="margin:0 0 12px; color:#1F2937; font-size:27px; line-height:1.2; font-weight:800;">Tu acceso temporal esta listo</h1>
                            <p style="margin:0; color:#6B7280; font-size:15px; line-height:1.55;">Un administrador restablecio tu contrasena. Usa la clave temporal de abajo para ingresar al sistema.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:10px 26px 28px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #E5E7EB; border-radius:8px; background:#F8FAFC;">
                                <tr>
                                    <td style="padding:18px 18px; text-align:center;">
                                        <span style="display:block; margin-bottom:8px; color:#6B7280; font-size:12px; font-weight:800; text-transform:uppercase;">Contrasena temporal</span>
                                        <strong style="display:inline-block; border-radius:8px; background:#E6F7F7; color:#005F73; font-size:24px; letter-spacing:.08em; padding:12px 18px;">{safe_password}</strong>
                                        <p style="margin:14px 0 0; color:#6B7280; font-size:13px; line-height:1.45;">Si no solicitaste este cambio, comunicate con el administrador antes de usarla.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="border-top:1px solid #E5E7EB; padding:16px 26px; color:#6B7280; font-size:12px; line-height:1.45;">
                            Por seguridad, no compartas esta contrasena por chats o canales no autorizados.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def send_ticket_status_change(self, email, ticket, previous_estado):
        subject = f"Actualizacion del caso #{ticket.id}"
        closed_text = ""

        if ticket.estado == "resuelto":
            closed_text = (
                "\n\n"
                "El caso fue cerrado con esta solucion:\n"
                f"{ticket.solucion_cierre or 'Sin detalle registrado'}"
            )

        body = (
            "Hola,\n\n"
            f"Tu caso #{ticket.id} cambio de estado: {previous_estado} -> {ticket.estado}.\n"
            f"Area: {ticket.area}\n"
            f"Descripcion: {ticket.descripcion}"
            f"{closed_text}\n\n"
            "Puedes ingresar al sistema para revisar el detalle."
        )

        html_solution = ""
        if ticket.estado == "resuelto":
            html_solution = f"""
                    <tr>
                        <td style="padding:0 24px 24px;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #d9dee5; border-radius:6px; background:#f8fafc;">
                                <tr>
                                    <td style="padding:14px 16px;">
                                        <strong style="display:block; margin-bottom:6px; color:#222831; font-size:14px;">Solucion registrada</strong>
                                        <p style="margin:0; color:#6b7280; font-size:14px; line-height:1.5;">{escape(ticket.solucion_cierre or 'Sin detalle registrado')}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
"""

        html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actualizacion del caso</title>
</head>
<body style="margin:0; padding:0; background:#f4f6f8; color:#222831; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8; margin:0; padding:28px 14px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px; background:#ffffff; border:1px solid #d9dee5; border-radius:8px; overflow:hidden;">
                    <tr>
                        <td style="background:#202832; padding:22px 24px; color:#ffffff;">
                            <strong style="display:block; font-size:17px;">TicketFlow</strong>
                            <span style="display:block; margin-top:3px; color:#b6c3cf; font-size:13px;">Mesa de ayuda</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:30px 24px 16px;">
                            <p style="margin:0 0 8px; color:#2f5d62; font-size:12px; font-weight:800; text-transform:uppercase;">Cambio de estado</p>
                            <h1 style="margin:0 0 12px; color:#222831; font-size:24px; line-height:1.2;">Caso #{ticket.id}: {escape(previous_estado)} -> {escape(ticket.estado)}</h1>
                            <p style="margin:0; color:#6b7280; font-size:15px; line-height:1.55;">Tu solicitud en el area {escape(ticket.area or '-')} fue actualizada.</p>
                        </td>
                    </tr>
                    {html_solution}
                    <tr>
                        <td style="border-top:1px solid #d9dee5; padding:16px 24px; color:#6b7280; font-size:12px; line-height:1.45;">
                            Ingresa al sistema para consultar el historial completo del caso.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        return self.send(email, subject, body, html)

    def send(self, recipient, subject, body, html=None):
        self.last_error = None
        server = current_app.config.get("MAIL_SERVER")
        sender = current_app.config.get("MAIL_SENDER")

        if not server:
            self.last_error = "MAIL_SERVER no esta configurado"
            current_app.logger.warning(
                "Correo no enviado a %s porque MAIL_SERVER no esta configurado.",
                recipient,
            )
            return False

        if not sender:
            self.last_error = "MAIL_SENDER no esta configurado"
            current_app.logger.warning(
                "Correo no enviado a %s porque MAIL_SENDER no esta configurado.",
                recipient,
            )
            return False

        try:
            message = EmailMessage()
            message["From"] = sender
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)

            if html:
                message.add_alternative(html, subtype="html")

            port = current_app.config["MAIL_PORT"]
            timeout = current_app.config["MAIL_TIMEOUT"]
            use_ssl = current_app.config["MAIL_USE_SSL"]
            use_tls = current_app.config["MAIL_USE_TLS"]

            if use_ssl and use_tls:
                raise ValueError("MAIL_USE_SSL y MAIL_USE_TLS no pueden estar activos al mismo tiempo")

            smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP

            with smtp_class(server, port, timeout=timeout) as smtp:
                smtp.ehlo()

                if use_tls:
                    smtp.starttls()
                    smtp.ehlo()

                username = current_app.config.get("MAIL_USERNAME")
                password = current_app.config.get("MAIL_PASSWORD")

                if username and password:
                    smtp.login(username, password)

                smtp.send_message(message)
        except (OSError, smtplib.SMTPException, ValueError) as exc:
            self.last_error = str(exc)
            current_app.logger.exception(
                "Correo no enviado a %s por error SMTP: %s",
                recipient,
                exc,
            )
            return False

        return True

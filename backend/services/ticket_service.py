from datetime import datetime

from models import Ticket, TicketHistorial, Usuario, db
from services.mail_service import MailService
from services.ticket_event_broker import ticket_event_broker


class TicketService:
    VALID_ESTADOS = {"pendiente", "proceso", "resuelto"}
    VALID_PRIORIDADES = {"baja", "media", "alta", "critica"}

    def __init__(self, mail_service=None):
        self.mail_service = mail_service or MailService()

    def list_for_user(self, user):
        query = Ticket.query

        if not user.is_admin():
            query = query.filter_by(usuario_id=user.id)

        return query.order_by(Ticket.id.desc()).all()

    def get_for_user(self, ticket_id, user):
        ticket = Ticket.query.get_or_404(ticket_id)

        if not self.can_access(ticket, user):
            return None

        return ticket

    def list_history_for_user(self, ticket_id, user):
        ticket = self.get_for_user(ticket_id, user)

        if ticket is None:
            return None

        return (
            TicketHistorial.query
            .filter_by(ticket_id=ticket.id)
            .order_by(TicketHistorial.id.desc())
            .all()
        )

    def create(
        self,
        user,
        titulo,
        descripcion,
        tipo_ticket=None,
        reportado_por=None,
        area=None,
        departamento=None,
        observacion=None,
    ):
        titulo = self.clean_text(titulo)
        descripcion = self.clean_text(descripcion)
        tipo_ticket = self.clean_text(tipo_ticket)
        reportado_por = self.clean_text(reportado_por)
        area = self.clean_text(area)
        departamento = self.clean_text(departamento)
        observacion = self.clean_text(observacion)

        if not titulo or not descripcion or not tipo_ticket or not area or not departamento:
            raise ValueError("Titulo, descripcion, tipo, area y departamento son obligatorios")

        ticket = Ticket(
            titulo=titulo,
            descripcion=descripcion,
            tipo_ticket=tipo_ticket,
            observacion=observacion,
            reportado_por=reportado_por or user.nombre,
            area=area,
            departamento=departamento,
            usuario_id=user.id,
        )

        db.session.add(ticket)
        db.session.flush()
        self.add_history(
            ticket=ticket,
            user=user,
            action="creado",
            detail={"titulo": ticket.titulo, "estado": ticket.estado, "prioridad": ticket.prioridad},
        )
        db.session.commit()
        payload = self.activity_payload(
            action="ticket_created",
            message=f"{user.nombre} creo el ticket #{ticket.id}",
            ticket=ticket,
            user=user,
        )
        ticket_event_broker.publish("ticket_created", payload)
        ticket_event_broker.publish("activity", payload)

        return ticket

    def update(
        self,
        ticket,
        user,
        titulo=None,
        descripcion=None,
        estado=None,
        prioridad=None,
        observacion=None,
        tipo_ticket=None,
        reportado_por=None,
        area=None,
        departamento=None,
        asignado_a_id=None,
        solucion_cierre=None,
    ):
        if ticket.estado == "resuelto":
            raise PermissionError("El ticket ya esta resuelto y no puede modificarse")

        titulo = self.clean_text(titulo)
        descripcion = self.clean_text(descripcion)
        observacion = self.clean_text(observacion)
        tipo_ticket = self.clean_text(tipo_ticket)
        reportado_por = self.clean_text(reportado_por)
        area = self.clean_text(area)
        departamento = self.clean_text(departamento)
        solucion_cierre = self.clean_text(solucion_cierre)

        previous_estado = ticket.estado
        changes = {}
        if titulo is not None:
            if not titulo:
                raise ValueError("El titulo no puede quedar vacio")
            self.track_change(changes, "titulo", ticket.titulo, titulo)
            ticket.titulo = titulo

        if descripcion is not None:
            if not descripcion:
                raise ValueError("La descripcion no puede quedar vacia")
            self.track_change(changes, "descripcion", ticket.descripcion, descripcion)
            ticket.descripcion = descripcion

        if observacion is not None:
            self.track_change(changes, "observacion", ticket.observacion, observacion)
            ticket.observacion = observacion

        if tipo_ticket is not None:
            if not tipo_ticket:
                raise ValueError("El tipo de ticket no puede quedar vacio")
            self.track_change(changes, "tipo_ticket", ticket.tipo_ticket, tipo_ticket)
            ticket.tipo_ticket = tipo_ticket

        if reportado_por is not None:
            self.track_change(changes, "reportado_por", ticket.reportado_por, reportado_por)
            ticket.reportado_por = reportado_por

        if area is not None:
            if not area:
                raise ValueError("El area no puede quedar vacia")
            self.track_change(changes, "area", ticket.area, area)
            ticket.area = area

        if departamento is not None:
            if not departamento:
                raise ValueError("El departamento no puede quedar vacio")
            self.track_change(changes, "departamento", ticket.departamento, departamento)
            ticket.departamento = departamento

        if asignado_a_id is not None:
            if not user.is_admin():
                raise PermissionError("Solo un administrador puede asignar responsables")

            assignee = Usuario.query.get(asignado_a_id)
            if assignee is None or not assignee.activo:
                raise ValueError("Responsable invalido")

            self.track_change(changes, "asignado_a_id", ticket.asignado_a_id, assignee.id)
            ticket.asignado_a_id = assignee.id

        if estado is not None:
            if not user.is_admin():
                raise PermissionError("No tienes permisos para cambiar el estado")

            if estado not in self.VALID_ESTADOS:
                raise ValueError("Estado invalido")

            if estado == "resuelto" and not solucion_cierre:
                raise ValueError("Debes escribir como termino el caso y que solucion se dio")

            self.track_change(changes, "estado", ticket.estado, estado)
            ticket.estado = estado
            closed_at = datetime.utcnow() if estado == "resuelto" else None
            self.track_change(changes, "cerrado_en", ticket.cerrado_en, closed_at)
            ticket.cerrado_en = closed_at
            self.track_change(changes, "cerrado_por_id", ticket.cerrado_por_id, user.id if estado == "resuelto" else None)
            ticket.cerrado_por_id = user.id if estado == "resuelto" else None

            if estado == "resuelto":
                self.track_change(changes, "solucion_cierre", ticket.solucion_cierre, solucion_cierre)
                ticket.solucion_cierre = solucion_cierre
            elif previous_estado == "resuelto":
                self.track_change(changes, "solucion_cierre", ticket.solucion_cierre, None)
                ticket.solucion_cierre = None

        if prioridad is not None:
            if not user.is_admin():
                raise PermissionError("Solo un administrador puede definir la prioridad")

            if prioridad not in self.VALID_PRIORIDADES:
                raise ValueError("Prioridad invalida")

            self.track_change(changes, "prioridad", ticket.prioridad, prioridad)
            ticket.prioridad = prioridad

        for field, values in changes.items():
            self.add_history(
                ticket=ticket,
                user=user,
                action="actualizado",
                field=field,
                previous_value=values["previous"],
                new_value=values["new"],
            )
        db.session.commit()
        action = "ticket_status_changed" if estado is not None and estado != previous_estado else "ticket_updated"
        message = self.update_message(action, user, ticket)
        payload = self.activity_payload(action=action, message=message, ticket=ticket, user=user)
        ticket_event_broker.publish("ticket_updated", payload)
        if action == "ticket_status_changed":
            ticket_event_broker.publish("ticket_status_changed", payload)
            self.notify_status_change(ticket, user, previous_estado)
        ticket_event_broker.publish("activity", payload)
        return ticket

    def delete(self, ticket, user=None):
        if ticket.estado == "resuelto":
            raise PermissionError("El ticket ya esta resuelto y no puede eliminarse")

        payload = ticket.to_dict()
        self.add_history(
            ticket=ticket,
            user=user,
            action="eliminado",
            detail={"ticket": payload},
        )
        db.session.delete(ticket)
        db.session.commit()
        event_payload = {
            "action": "ticket_deleted",
            "message": f"Se elimino el ticket #{payload['id']}",
            "ticket": payload,
            "visibility": "ticket",
        }
        ticket_event_broker.publish("ticket_deleted", event_payload)
        ticket_event_broker.publish("activity", event_payload)

    def can_access(self, ticket, user):
        return user.is_admin() or ticket.belongs_to(user)

    def activity_payload(self, action, message, ticket, user):
        return {
            "action": action,
            "message": message,
            "ticket": ticket.to_dict(),
            "user": user.to_dict(),
            "visibility": "ticket",
        }

    def update_message(self, action, user, ticket):
        if action == "ticket_status_changed":
            return f"{user.nombre} cambio el estado del ticket #{ticket.id} a {ticket.estado}"

        return f"{user.nombre} actualizo el ticket #{ticket.id}"

    def notify_status_change(self, ticket, user, previous_estado):
        if not ticket.usuario or not ticket.usuario.email:
            return

        sent = self.mail_service.send_ticket_status_change(ticket.usuario.email, ticket, previous_estado)
        payload = self.activity_payload(
            action="ticket_owner_notified",
            message=(
                f"Se notifico a {ticket.usuario.email} sobre el ticket #{ticket.id}"
                if sent
                else f"No se pudo enviar correo de notificacion para el ticket #{ticket.id}"
            ),
            ticket=ticket,
            user=user,
        )
        payload["visibility"] = "admins"
        payload["email_sent"] = sent
        payload["email_error"] = self.mail_service.last_error
        ticket_event_broker.publish("activity", payload)

    def track_change(self, changes, field, previous_value, new_value):
        if previous_value != new_value:
            changes[field] = {
                "previous": self.history_value(previous_value),
                "new": self.history_value(new_value),
            }

    def add_history(self, ticket, user, action, field=None, previous_value=None, new_value=None, detail=None):
        db.session.add(TicketHistorial(
            ticket_id=ticket.id,
            usuario_id=user.id if user else None,
            accion=action,
            campo=field,
            valor_anterior=previous_value,
            valor_nuevo=new_value,
            detalle=detail,
        ))

    def history_value(self, value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        return str(value)

    def clean_text(self, value):
        if value is None:
            return None

        return str(value).strip()

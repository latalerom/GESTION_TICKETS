from models import Ticket, db
from services.ticket_event_broker import ticket_event_broker


class TicketService:
    VALID_ESTADOS = {"pendiente", "proceso", "resuelto"}
    VALID_PRIORIDADES = {"baja", "media", "alta", "critica"}

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
    ):
        previous_estado = ticket.estado
        if titulo is not None:
            ticket.titulo = titulo

        if descripcion is not None:
            ticket.descripcion = descripcion

        if observacion is not None:
            ticket.observacion = observacion

        if tipo_ticket is not None:
            ticket.tipo_ticket = tipo_ticket

        if reportado_por is not None:
            ticket.reportado_por = reportado_por

        if area is not None:
            ticket.area = area

        if departamento is not None:
            ticket.departamento = departamento

        if estado is not None:
            if not user.is_admin():
                raise PermissionError("No tienes permisos para cambiar el estado")

            if estado not in self.VALID_ESTADOS:
                raise ValueError("Estado invalido")

            ticket.estado = estado

        if prioridad is not None:
            if not user.is_admin():
                raise PermissionError("Solo un administrador puede definir la prioridad")

            if prioridad not in self.VALID_PRIORIDADES:
                raise ValueError("Prioridad invalida")

            ticket.prioridad = prioridad

        db.session.commit()
        action = "ticket_status_changed" if estado is not None and estado != previous_estado else "ticket_updated"
        message = self.update_message(action, user, ticket)
        payload = self.activity_payload(action=action, message=message, ticket=ticket, user=user)
        ticket_event_broker.publish("ticket_updated", payload)
        ticket_event_broker.publish("activity", payload)
        return ticket

    def delete(self, ticket):
        payload = ticket.to_dict()
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

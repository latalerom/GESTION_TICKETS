from flask import Blueprint, Response, jsonify, request, session

from services.auth_service import AuthService
from services.ticket_event_broker import ticket_event_broker
from services.ticket_service import TicketService


class TicketController:
    def __init__(self, ticket_service=None, auth_service=None):
        self.ticket_service = ticket_service or TicketService()
        self.auth_service = auth_service or AuthService()
        self.blueprint = Blueprint("tickets", __name__, url_prefix="/api")
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule("/tickets", view_func=self.list_tickets, methods=["GET"])
        self.blueprint.add_url_rule("/tickets/stream", view_func=self.stream_tickets, methods=["GET"])
        self.blueprint.add_url_rule("/tickets/<int:id>", view_func=self.get_ticket, methods=["GET"])
        self.blueprint.add_url_rule("/tickets", view_func=self.create_ticket, methods=["POST"])
        self.blueprint.add_url_rule("/tickets/<int:id>", view_func=self.update_ticket, methods=["PUT"])
        self.blueprint.add_url_rule("/tickets/<int:id>", view_func=self.delete_ticket, methods=["DELETE"])

    def current_user(self):
        return self.auth_service.get_user_by_id(session.get("user_id"))

    def require_user(self):
        user = self.current_user()

        if user is None:
            return None, (jsonify({"error": "Debes iniciar sesion"}), 401)

        return user, None

    def forbidden(self):
        return jsonify({"error": "No tienes permisos para esta accion"}), 403

    def list_tickets(self):
        """
        Listar tickets
        ---
        tags:
          - Tickets
        responses:
          200:
            description: Lista de tickets visibles para el usuario autenticado.
            schema:
              type: array
              items:
                $ref: '#/definitions/Ticket'
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
        """
        user, error = self.require_user()
        if error is not None:
            return error

        tickets = self.ticket_service.list_for_user(user)
        return jsonify([ticket.to_dict() for ticket in tickets])

    def stream_tickets(self):
        """
        Escuchar cambios de tickets en tiempo real
        ---
        tags:
          - Tickets
        produces:
          - text/event-stream
        responses:
          200:
            description: Stream SSE con eventos ticket_created, ticket_updated, ticket_deleted y activity.
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
        """
        user, error = self.require_user()
        if error is not None:
            return error

        listener = ticket_event_broker.subscribe()
        response = Response(
            ticket_event_broker.stream(listener, user.to_dict()),
            mimetype="text/event-stream",
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"
        return response

    def get_ticket(self, id):
        """
        Obtener ticket por ID
        ---
        tags:
          - Tickets
        parameters:
          - in: path
            name: id
            type: integer
            required: true
            description: ID del ticket.
        responses:
          200:
            description: Ticket encontrado.
            schema:
              $ref: '#/definitions/Ticket'
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
          403:
            description: El usuario no tiene permisos sobre este ticket.
            schema:
              $ref: '#/definitions/Error'
          404:
            description: Ticket no encontrado.
        """
        user, error = self.require_user()
        if error is not None:
            return error

        ticket = self.ticket_service.get_for_user(id, user)

        if ticket is None:
            return self.forbidden()

        return jsonify(ticket.to_dict())

    def create_ticket(self):
        """
        Crear ticket
        ---
        tags:
          - Tickets
        consumes:
          - application/json
        parameters:
          - in: body
            name: ticket
            required: true
            schema:
              $ref: '#/definitions/TicketCreateRequest'
        responses:
          201:
            description: Ticket creado correctamente.
            schema:
              $ref: '#/definitions/Ticket'
          400:
            description: Faltan campos obligatorios.
            schema:
              $ref: '#/definitions/Error'
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
        """
        user, error = self.require_user()
        if error is not None:
            return error

        data = request.get_json(silent=True) or {}

        try:
            ticket = self.ticket_service.create(
                user=user,
                titulo=data.get("titulo"),
                descripcion=data.get("descripcion"),
                tipo_ticket=data.get("tipo_ticket"),
                reportado_por=data.get("reportado_por"),
                area=data.get("area"),
                departamento=data.get("departamento"),
                observacion=data.get("observacion"),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(ticket.to_dict()), 201

    def update_ticket(self, id):
        """
        Actualizar ticket
        ---
        tags:
          - Tickets
        consumes:
          - application/json
        parameters:
          - in: path
            name: id
            type: integer
            required: true
            description: ID del ticket.
          - in: body
            name: ticket
            required: true
            schema:
              $ref: '#/definitions/TicketUpdateRequest'
        responses:
          200:
            description: Ticket actualizado correctamente.
            schema:
              $ref: '#/definitions/Ticket'
          400:
            description: Datos invalidos.
            schema:
              $ref: '#/definitions/Error'
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
          403:
            description: El usuario no tiene permisos para esta accion.
            schema:
              $ref: '#/definitions/Error'
          404:
            description: Ticket no encontrado.
        """
        user, error = self.require_user()
        if error is not None:
            return error

        ticket = self.ticket_service.get_for_user(id, user)

        if ticket is None:
            return self.forbidden()

        data = request.get_json(silent=True) or {}

        try:
            ticket = self.ticket_service.update(
                ticket=ticket,
                user=user,
                titulo=data.get("titulo"),
                descripcion=data.get("descripcion"),
                estado=data.get("estado"),
                prioridad=data.get("prioridad"),
                observacion=data.get("observacion"),
                tipo_ticket=data.get("tipo_ticket"),
                reportado_por=data.get("reportado_por"),
                area=data.get("area"),
                departamento=data.get("departamento"),
            )
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(ticket.to_dict())

    def delete_ticket(self, id):
        """
        Eliminar ticket
        ---
        tags:
          - Tickets
        parameters:
          - in: path
            name: id
            type: integer
            required: true
            description: ID del ticket.
        responses:
          200:
            description: Ticket eliminado correctamente.
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Ticket eliminado
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
          403:
            description: El usuario no tiene permisos sobre este ticket.
            schema:
              $ref: '#/definitions/Error'
          404:
            description: Ticket no encontrado.
        """
        user, error = self.require_user()
        if error is not None:
            return error

        ticket = self.ticket_service.get_for_user(id, user)

        if ticket is None:
            return self.forbidden()

        self.ticket_service.delete(ticket)
        return jsonify({"message": "Ticket eliminado"})


ticket_bp = TicketController().blueprint

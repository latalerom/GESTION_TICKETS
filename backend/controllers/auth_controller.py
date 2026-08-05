from flask import Blueprint, jsonify, request, session

from services.auth_service import AuthService
from services.invitation_service import InvitationService
from services.ticket_event_broker import ticket_event_broker
from models import db


class AuthController:
    def __init__(self, auth_service=None, invitation_service=None):
        self.auth_service = auth_service or AuthService()
        self.invitation_service = invitation_service or InvitationService()
        self.blueprint = Blueprint("auth", __name__, url_prefix="/api")
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule("/login", view_func=self.login, methods=["POST"])
        self.blueprint.add_url_rule("/session", view_func=self.session_status, methods=["GET"])
        self.blueprint.add_url_rule("/logout", view_func=self.logout, methods=["POST"])
        self.blueprint.add_url_rule("/profile", view_func=self.update_profile, methods=["PUT"])
        self.blueprint.add_url_rule("/users", view_func=self.list_users, methods=["GET"])
        self.blueprint.add_url_rule("/users/<int:user_id>/reset-password", view_func=self.reset_user_password, methods=["POST"])
        self.blueprint.add_url_rule("/invitations", view_func=self.create_invitation, methods=["POST"])
        self.blueprint.add_url_rule("/invitations/<token>", view_func=self.get_invitation, methods=["GET"])
        self.blueprint.add_url_rule("/register", view_func=self.register_user, methods=["POST"])

    def current_user(self):
        user = self.auth_service.get_user_by_id(session.get("user_id"))

        if user is None:
            session.clear()

        return user

    def user_summary(self, user, include_photo=False):
        data = user.to_dict()

        if not include_photo:
            data.pop("foto_perfil", None)

        return data

    def login(self):
        """
        Iniciar sesion
        ---
        tags:
          - Autenticacion
        consumes:
          - application/json
        parameters:
          - in: body
            name: credenciales
            required: true
            schema:
              $ref: '#/definitions/LoginRequest'
        responses:
          200:
            description: Inicio de sesion exitoso.
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Inicio de sesion exitoso
                user:
                  $ref: '#/definitions/User'
          400:
            description: Faltan campos obligatorios.
            schema:
              $ref: '#/definitions/Error'
          401:
            description: Credenciales invalidas.
            schema:
              $ref: '#/definitions/Error'
        """
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Correo y contrasena son obligatorios"}), 400

        user = self.auth_service.authenticate(email, password)

        if user is None:
            return jsonify({"error": "Correo o contrasena incorrectos"}), 401

        session["user_id"] = user.id
        ticket_event_broker.publish("activity", {
            "action": "user_login",
            "message": f"{user.nombre} inicio sesion",
            "user": user.to_dict(),
            "visibility": "user",
        })

        return jsonify({
            "message": "Inicio de sesion exitoso",
            "user": user.to_dict(),
        })

    def session_status(self):
        """
        Consultar sesion activa
        ---
        tags:
          - Autenticacion
        responses:
          200:
            description: Hay una sesion activa.
            schema:
              type: object
              properties:
                authenticated:
                  type: boolean
                  example: true
                user:
                  $ref: '#/definitions/User'
          401:
            description: No hay sesion activa.
            schema:
              type: object
              properties:
                authenticated:
                  type: boolean
                  example: false
        """
        user = self.current_user()

        if user is None:
            return jsonify({"authenticated": False}), 401

        return jsonify({
            "authenticated": True,
            "user": user.to_dict(),
        })

    def logout(self):
        """
        Cerrar sesion
        ---
        tags:
          - Autenticacion
        responses:
          200:
            description: Sesion cerrada correctamente.
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Sesion cerrada
        """
        user = self.current_user()

        if user is not None:
            ticket_event_broker.publish("activity", {
                "action": "user_logout",
                "message": f"{user.nombre} cerro sesion",
                "user": user.to_dict(),
                "visibility": "admins",
            })

        session.clear()
        return jsonify({"message": "Sesion cerrada"})

    def update_profile(self):
        """
        Actualizar perfil del usuario autenticado
        ---
        tags:
          - Autenticacion
        consumes:
          - application/json
        responses:
          200:
            description: Perfil actualizado correctamente.
          401:
            description: El usuario no ha iniciado sesion.
        """
        user = self.current_user()

        if user is None:
            return jsonify({"error": "Debes iniciar sesion"}), 401

        data = request.get_json(silent=True) or {}
        user = self.auth_service.update_profile(user, data)

        db.session.commit()

        return jsonify({
            "message": "Perfil actualizado correctamente",
            "user": user.to_dict(),
        })

    def list_users(self):
        user = self.current_user()

        if user is None:
            return jsonify({"error": "Debes iniciar sesion"}), 401

        try:
            users = self.auth_service.list_users(user)
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403

        return jsonify({
            "users": [self.user_summary(item, include_photo=True) for item in users],
        })

    def reset_user_password(self, user_id):
        user = self.current_user()

        if user is None:
            return jsonify({"error": "Debes iniciar sesion"}), 401

        try:
            target_user, sent, temporary_password = self.auth_service.reset_password(user, user_id)
            db.session.commit()
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except ValueError as exc:
            db.session.rollback()
            return jsonify({"error": str(exc)}), 400

        return jsonify({
            "message": "Contrasena restablecida correctamente",
            "user": self.user_summary(target_user),
            "email_sent": sent,
            "temporary_password": temporary_password,
        })

    def create_invitation(self):
        """
        Crear invitacion de usuario
        ---
        tags:
          - Autenticacion
        consumes:
          - application/json
        parameters:
          - in: body
            name: invitacion
            required: true
            schema:
              $ref: '#/definitions/InvitationCreateRequest'
        responses:
          201:
            description: Invitacion creada correctamente.
          400:
            description: Datos invalidos.
            schema:
              $ref: '#/definitions/Error'
          401:
            description: El usuario no ha iniciado sesion.
            schema:
              $ref: '#/definitions/Error'
          403:
            description: Solo administradores pueden invitar usuarios.
            schema:
              $ref: '#/definitions/Error'
        """
        user = self.current_user()

        if user is None:
            return jsonify({"error": "Debes iniciar sesion"}), 401

        data = request.get_json(silent=True) or {}

        try:
            invitation, link, sent, email_error = self.invitation_service.create_invitation(
                email=data.get("email"),
                rol=data.get("rol", "cliente"),
                invited_by=user,
                created_ip=request.remote_addr,
            )
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify({
            "message": "Invitacion creada correctamente",
            "invitation": invitation.to_dict(),
            "registration_link": link,
            "email_sent": sent,
            "email_error": email_error,
        }), 201

    def get_invitation(self, token):
        """
        Consultar invitacion por token
        ---
        tags:
          - Autenticacion
        parameters:
          - in: path
            name: token
            type: string
            required: true
            description: Token de invitacion.
        responses:
          200:
            description: Invitacion valida.
          404:
            description: Invitacion inexistente o expirada.
            schema:
              $ref: '#/definitions/Error'
        """
        invitation = self.invitation_service.get_invitation(token)

        if invitation is None:
            return jsonify({"error": "La invitacion no existe o ya expiro"}), 404

        return jsonify({
            "email": invitation.email,
            "rol": invitation.rol,
        })

    def register_user(self):
        """
        Registrar usuario invitado
        ---
        tags:
          - Autenticacion
        consumes:
          - application/json
        parameters:
          - in: body
            name: registro
            required: true
            schema:
              $ref: '#/definitions/RegisterRequest'
        responses:
          201:
            description: Registro completado correctamente.
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Registro completado correctamente
                user:
                  $ref: '#/definitions/User'
          400:
            description: Invitacion invalida o datos incompletos.
            schema:
              $ref: '#/definitions/Error'
        """
        data = request.get_json(silent=True) or {}

        try:
            user = self.invitation_service.register_user(
                token=data.get("token"),
                nombre=data.get("nombre"),
                password=data.get("password"),
                telefono=data.get("telefono"),
                cargo=data.get("cargo"),
                bio=data.get("bio"),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        session["user_id"] = user.id

        return jsonify({
            "message": "Registro completado correctamente",
            "user": user.to_dict(),
        }), 201


auth_bp = AuthController().blueprint

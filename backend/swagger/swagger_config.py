from flasgger import Swagger


class SwaggerConfig:
    TEMPLATE = {
        "swagger": "2.0",
        "info": {
            "title": "Sistema de Soporte API",
            "description": "Documentacion y pruebas manuales para la API del sistema de tickets.",
            "version": "1.0.0",
        },
        "basePath": "/",
        "schemes": ["http"],
        "tags": [
            {
                "name": "Autenticacion",
                "description": "Endpoints para login, sesion, logout, invitaciones y registro.",
            },
            {
                "name": "Tickets",
                "description": "Endpoints para gestion de tickets.",
            },
        ],
        "definitions": {
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "admin@gmail.com",
                    },
                    "password": {
                        "type": "string",
                        "example": "1234",
                    },
                },
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "nombre": {"type": "string", "example": "Admin"},
                    "email": {"type": "string", "example": "admin@gmail.com"},
                    "rol": {"type": "string", "example": "admin"},
                    "activo": {"type": "boolean", "example": True},
                    "telefono": {"type": "string", "example": "3001234567"},
                    "cargo": {"type": "string", "example": "Soporte"},
                    "bio": {"type": "string", "example": "Responsable de mesa de ayuda."},
                    "foto_perfil": {"type": "string", "example": "data:image/png;base64,..."},
                },
            },
            "ProfileUpdateRequest": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "example": "Luisa Romero"},
                    "telefono": {"type": "string", "example": "3001234567"},
                    "cargo": {"type": "string", "example": "Analista de soporte"},
                    "bio": {"type": "string", "example": "Gestiono solicitudes de soporte."},
                    "foto_perfil": {"type": "string", "example": "data:image/png;base64,..."},
                },
            },
            "Ticket": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "titulo": {"type": "string", "example": "Error de acceso"},
                    "tipo_ticket": {"type": "string", "example": "Acceso a sistemas"},
                    "descripcion": {
                        "type": "string",
                        "example": "No puedo ingresar al sistema.",
                    },
                    "observacion": {
                        "type": "string",
                        "example": "El usuario reporta bloqueo desde la manana.",
                    },
                    "reportado_por": {"type": "string", "example": "Luisa Romero"},
                    "area": {"type": "string", "example": "Soporte tecnico"},
                    "departamento": {"type": "string", "example": "Tecnologia"},
                    "prioridad": {"type": "string", "example": "media"},
                    "estado": {"type": "string", "example": "pendiente"},
                    "solucion_cierre": {"type": "string", "example": "Se corrigio el acceso y se notifico al usuario."},
                    "cerrado_por_id": {"type": "integer", "example": 1},
                    "cerrado_por": {"type": "string", "example": "Admin"},
                    "usuario_id": {"type": "integer", "example": 1},
                    "usuario": {"type": "string", "example": "Admin"},
                    "asignado_a_id": {"type": "integer", "example": 1},
                    "asignado_a": {"type": "string", "example": "Admin"},
                    "creado_en": {"type": "string", "example": "2026-06-04T12:00:00"},
                    "actualizado_en": {"type": "string", "example": "2026-06-04T12:30:00"},
                    "cerrado_en": {"type": "string", "example": "2026-06-04T13:00:00"},
                },
            },
            "TicketHistory": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "ticket_id": {"type": "integer", "example": 10},
                    "usuario_id": {"type": "integer", "example": 1},
                    "usuario": {"type": "string", "example": "Admin"},
                    "accion": {"type": "string", "example": "actualizado"},
                    "campo": {"type": "string", "example": "estado"},
                    "valor_anterior": {"type": "string", "example": "pendiente"},
                    "valor_nuevo": {"type": "string", "example": "proceso"},
                    "detalle": {"type": "object"},
                    "creado_en": {"type": "string", "example": "2026-06-04T12:45:00"},
                },
            },
            "TicketCreateRequest": {
                "type": "object",
                "required": ["titulo", "descripcion", "tipo_ticket", "area", "departamento"],
                "properties": {
                    "titulo": {"type": "string", "example": "Error de acceso"},
                    "tipo_ticket": {"type": "string", "example": "Acceso a sistemas"},
                    "descripcion": {
                        "type": "string",
                        "example": "No puedo ingresar al sistema.",
                    },
                    "observacion": {
                        "type": "string",
                        "example": "Caso reportado con urgencia moderada.",
                    },
                    "reportado_por": {"type": "string", "example": "Luisa Romero"},
                    "area": {"type": "string", "example": "Soporte tecnico"},
                    "departamento": {"type": "string", "example": "Tecnologia"},
                },
            },
            "TicketUpdateRequest": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "example": "Error actualizado"},
                    "tipo_ticket": {"type": "string", "example": "Acceso a sistemas"},
                    "descripcion": {
                        "type": "string",
                        "example": "Descripcion actualizada del problema.",
                    },
                    "observacion": {
                        "type": "string",
                        "example": "El caso fue escalado al area correspondiente.",
                    },
                    "reportado_por": {"type": "string", "example": "Luisa Romero"},
                    "area": {"type": "string", "example": "Soporte tecnico"},
                    "departamento": {"type": "string", "example": "Tecnologia"},
                    "asignado_a_id": {"type": "integer", "example": 1},
                    "prioridad": {
                        "type": "string",
                        "enum": ["baja", "media", "alta", "critica"],
                        "example": "alta",
                    },
                    "estado": {
                        "type": "string",
                        "enum": ["pendiente", "proceso", "resuelto"],
                        "example": "proceso",
                    },
                    "solucion_cierre": {
                        "type": "string",
                        "example": "Se valido el caso, se aplico la solucion y el usuario quedo notificado.",
                    },
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Mensaje de error"},
                },
            },
            "InvitationCreateRequest": {
                "type": "object",
                "required": ["email", "rol"],
                "properties": {
                    "email": {"type": "string", "example": "nuevo@gmail.com"},
                    "rol": {
                        "type": "string",
                        "enum": ["admin", "cliente"],
                        "example": "cliente",
                    },
                },
            },
            "RegisterRequest": {
                "type": "object",
                "required": ["token", "nombre", "password"],
                "properties": {
                    "token": {"type": "string", "example": "token-de-invitacion"},
                    "nombre": {"type": "string", "example": "Nuevo Usuario"},
                    "password": {"type": "string", "example": "1234"},
                },
            },
        },
    }

    CONFIG = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }

    @classmethod
    def init_app(cls, app):
        return Swagger(app, template=cls.TEMPLATE, config=cls.CONFIG)

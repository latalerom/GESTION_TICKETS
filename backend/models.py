from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    rol = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
        }

    def is_admin(self):
        return self.rol == "admin"


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    tipo_ticket = db.Column(db.String(100), default="General")
    observacion = db.Column(db.Text)
    reportado_por = db.Column(db.String(100))
    area = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    prioridad = db.Column(db.String(50), default="media")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    usuario = db.relationship("Usuario")
    estado = db.Column(db.String(50), default="pendiente")
    creado_en = db.Column(db.DateTime, nullable=False, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "tipo_ticket": self.tipo_ticket,
            "observacion": self.observacion,
            "reportado_por": self.reportado_por,
            "area": self.area,
            "departamento": self.departamento,
            "prioridad": self.prioridad,
            "estado": self.estado,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.nombre if self.usuario else None,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }

    def belongs_to(self, user):
        return user is not None and self.usuario_id == user.id


class InvitacionUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default="cliente")
    token = db.Column(db.String(120), unique=True, nullable=False)
    usada = db.Column(db.Boolean, default=False)
    creada_en = db.Column(db.DateTime, nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    usada_en = db.Column(db.DateTime)

    def is_available(self, now):
        return not self.usada and self.expira_en >= now

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "rol": self.rol,
            "usada": self.usada,
            "creada_en": self.creada_en.isoformat(),
            "expira_en": self.expira_en.isoformat(),
        }

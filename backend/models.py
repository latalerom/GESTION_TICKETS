from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default="cliente", index=True)
    activo = db.Column(db.Boolean, nullable=False, default=True, index=True)
    telefono = db.Column(db.String(30))
    cargo = db.Column(db.String(100))
    bio = db.Column(db.Text)
    foto_perfil = db.Column(LONGTEXT)
    creado_en = db.Column(db.DateTime, nullable=False, server_default=func.now())
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo,
            "telefono": self.telefono,
            "cargo": self.cargo,
            "bio": self.bio,
            "foto_perfil": self.foto_perfil,
        }

    def is_admin(self):
        return self.rol == "admin"


class Ticket(db.Model):
    __table_args__ = (
        db.Index("ix_ticket_usuario_estado", "usuario_id", "estado"),
    )

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_ticket = db.Column(db.String(100), nullable=False, default="General")
    observacion = db.Column(db.Text)
    reportado_por = db.Column(db.String(100))
    area = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.String(50), nullable=False, default="media", index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, index=True)
    usuario = db.relationship("Usuario", foreign_keys=[usuario_id])
    asignado_a_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), index=True)
    asignado_a = db.relationship("Usuario", foreign_keys=[asignado_a_id])
    estado = db.Column(db.String(50), nullable=False, default="pendiente", index=True)
    solucion_cierre = db.Column(db.Text)
    cerrado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), index=True)
    cerrado_por = db.relationship("Usuario", foreign_keys=[cerrado_por_id])
    creado_en = db.Column(db.DateTime, nullable=False, server_default=func.now(), index=True)
    actualizado_en = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    cerrado_en = db.Column(db.DateTime)

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
            "solucion_cierre": self.solucion_cierre,
            "cerrado_por_id": self.cerrado_por_id,
            "cerrado_por": self.cerrado_por.nombre if self.cerrado_por else None,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.nombre if self.usuario else None,
            "asignado_a_id": self.asignado_a_id,
            "asignado_a": self.asignado_a.nombre if self.asignado_a else None,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
            "cerrado_en": self.cerrado_en.isoformat() if self.cerrado_en else None,
        }

    def belongs_to(self, user):
        return user is not None and self.usuario_id == user.id


class TicketHistorial(db.Model):
    __tablename__ = "ticket_historial"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id", ondelete="SET NULL"), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id", ondelete="SET NULL"), index=True)
    accion = db.Column(db.String(50), nullable=False, index=True)
    campo = db.Column(db.String(100))
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    detalle = db.Column(db.JSON)
    creado_en = db.Column(db.DateTime, nullable=False, server_default=func.now(), index=True)

    ticket = db.relationship("Ticket")
    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.nombre if self.usuario else None,
            "accion": self.accion,
            "campo": self.campo,
            "valor_anterior": self.valor_anterior,
            "valor_nuevo": self.valor_nuevo,
            "detalle": self.detalle,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }


class InvitacionUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    rol = db.Column(db.String(50), nullable=False, default="cliente")
    token = db.Column(db.String(120), unique=True, nullable=False)
    usada = db.Column(db.Boolean, nullable=False, default=False)
    invitado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), index=True)
    invitado_por = db.relationship("Usuario")
    creada_en = db.Column(db.DateTime, nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False, index=True)
    usada_en = db.Column(db.DateTime)
    creada_ip = db.Column(db.String(45))

    def is_available(self, now):
        return not self.usada and self.expira_en >= now

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "rol": self.rol,
            "usada": self.usada,
            "invitado_por_id": self.invitado_por_id,
            "creada_en": self.creada_en.isoformat(),
            "expira_en": self.expira_en.isoformat(),
        }

from sqlalchemy import inspect, text

from models import db


class SchemaService:
    USER_COLUMNS = {
        "activo": "BOOLEAN NOT NULL DEFAULT true",
        "telefono": "VARCHAR(30) NULL",
        "cargo": "VARCHAR(100) NULL",
        "bio": "TEXT NULL",
        "foto_perfil": "LONGTEXT NULL",
        "creado_en": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "actualizado_en": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    }

    TICKET_COLUMNS = {
        "tipo_ticket": "VARCHAR(100) DEFAULT 'General'",
        "observacion": "TEXT NULL",
        "reportado_por": "VARCHAR(100) NULL",
        "area": "VARCHAR(100) NULL",
        "departamento": "VARCHAR(100) NULL",
        "prioridad": "VARCHAR(50) DEFAULT 'media'",
        "asignado_a_id": "INT NULL",
        "solucion_cierre": "TEXT NULL",
        "cerrado_por_id": "INT NULL",
        "creado_en": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "actualizado_en": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        "cerrado_en": "DATETIME NULL",
    }

    INVITATION_COLUMNS = {
        "invitado_por_id": "INT NULL",
        "creada_ip": "VARCHAR(45) NULL",
    }

    INDEXES = {
        "usuario": {
            "ix_usuario_rol": "CREATE INDEX ix_usuario_rol ON usuario (rol)",
            "ix_usuario_activo": "CREATE INDEX ix_usuario_activo ON usuario (activo)",
        },
        "ticket": {
            "ix_ticket_usuario_id": "CREATE INDEX ix_ticket_usuario_id ON ticket (usuario_id)",
            "ix_ticket_estado": "CREATE INDEX ix_ticket_estado ON ticket (estado)",
            "ix_ticket_prioridad": "CREATE INDEX ix_ticket_prioridad ON ticket (prioridad)",
            "ix_ticket_creado_en": "CREATE INDEX ix_ticket_creado_en ON ticket (creado_en)",
            "ix_ticket_asignado_a_id": "CREATE INDEX ix_ticket_asignado_a_id ON ticket (asignado_a_id)",
            "ix_ticket_cerrado_por_id": "CREATE INDEX ix_ticket_cerrado_por_id ON ticket (cerrado_por_id)",
            "ix_ticket_usuario_estado": "CREATE INDEX ix_ticket_usuario_estado ON ticket (usuario_id, estado)",
        },
        "invitacion_usuario": {
            "ix_invitacion_usuario_email": "CREATE INDEX ix_invitacion_usuario_email ON invitacion_usuario (email)",
            "ix_invitacion_usuario_expira_en": "CREATE INDEX ix_invitacion_usuario_expira_en ON invitacion_usuario (expira_en)",
            "ix_invitacion_usuario_invitado_por_id": "CREATE INDEX ix_invitacion_usuario_invitado_por_id ON invitacion_usuario (invitado_por_id)",
        },
    }

    def sync(self):
        inspector = inspect(db.engine)

        self.sync_columns(inspector, "usuario", self.USER_COLUMNS)
        self.sync_columns(inspector, "ticket", self.TICKET_COLUMNS)
        self.sync_columns(inspector, "invitacion_usuario", self.INVITATION_COLUMNS)
        self.sync_indexes(inspector)

        db.session.commit()

    def sync_columns(self, inspector, table_name, columns):
        if not inspector.has_table(table_name):
            return

        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}

        for column_name, column_definition in columns.items():
            if column_name not in existing_columns:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))

    def sync_indexes(self, inspector):
        for table_name, indexes in self.INDEXES.items():
            if not inspector.has_table(table_name):
                continue

            existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}

            for index_name, statement in indexes.items():
                if index_name not in existing_indexes:
                    db.session.execute(text(statement))

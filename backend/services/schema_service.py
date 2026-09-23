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
        "tipo_ticket": "VARCHAR(100) NOT NULL DEFAULT 'General'",
        "observacion": "TEXT NULL",
        "reportado_por": "VARCHAR(100) NULL",
        "area": "VARCHAR(100) NOT NULL DEFAULT 'Sin area'",
        "departamento": "VARCHAR(100) NOT NULL DEFAULT 'Sin departamento'",
        "prioridad": "ENUM('baja', 'media', 'alta', 'critica') NOT NULL DEFAULT 'media'",
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

    COLUMN_DEFINITIONS = {
        "usuario": {
            "email": "VARCHAR(254) NOT NULL",
            "password": "VARCHAR(255) NOT NULL",
            "rol": "ENUM('admin', 'cliente') NOT NULL DEFAULT 'cliente'",
        },
        "ticket": {
            "tipo_ticket": "VARCHAR(100) NOT NULL DEFAULT 'General'",
            "area": "VARCHAR(100) NOT NULL DEFAULT 'Sin area'",
            "departamento": "VARCHAR(100) NOT NULL DEFAULT 'Sin departamento'",
            "prioridad": "ENUM('baja', 'media', 'alta', 'critica') NOT NULL DEFAULT 'media'",
            "estado": "ENUM('pendiente', 'proceso', 'resuelto') NOT NULL DEFAULT 'pendiente'",
        },
        "ticket_historial": {
            "accion": "ENUM('creado', 'actualizado', 'eliminado') NOT NULL",
        },
        "invitacion_usuario": {
            "email": "VARCHAR(254) NOT NULL",
            "rol": "ENUM('admin', 'cliente') NOT NULL DEFAULT 'cliente'",
            "token": "VARCHAR(128) NOT NULL",
        },
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
            "ix_ticket_estado_prioridad_creado": "CREATE INDEX ix_ticket_estado_prioridad_creado ON ticket (estado, prioridad, creado_en)",
            "ix_ticket_asignado_estado": "CREATE INDEX ix_ticket_asignado_estado ON ticket (asignado_a_id, estado)",
        },
        "invitacion_usuario": {
            "ix_invitacion_usuario_email": "CREATE INDEX ix_invitacion_usuario_email ON invitacion_usuario (email)",
            "ix_invitacion_usuario_expira_en": "CREATE INDEX ix_invitacion_usuario_expira_en ON invitacion_usuario (expira_en)",
            "ix_invitacion_usuario_invitado_por_id": "CREATE INDEX ix_invitacion_usuario_invitado_por_id ON invitacion_usuario (invitado_por_id)",
            "ix_invitacion_usuario_email_usada_expira": "CREATE INDEX ix_invitacion_usuario_email_usada_expira ON invitacion_usuario (email, usada, expira_en)",
        },
    }

    FOREIGN_KEYS = {
        "ticket": {
            "fk_ticket_usuario": (
                "ALTER TABLE ticket ADD CONSTRAINT fk_ticket_usuario "
                "FOREIGN KEY (usuario_id) REFERENCES usuario (id) "
                "ON UPDATE CASCADE ON DELETE RESTRICT"
            ),
            "fk_ticket_asignado_a": (
                "ALTER TABLE ticket ADD CONSTRAINT fk_ticket_asignado_a "
                "FOREIGN KEY (asignado_a_id) REFERENCES usuario (id) "
                "ON UPDATE CASCADE ON DELETE SET NULL"
            ),
            "fk_ticket_cerrado_por": (
                "ALTER TABLE ticket ADD CONSTRAINT fk_ticket_cerrado_por "
                "FOREIGN KEY (cerrado_por_id) REFERENCES usuario (id) "
                "ON UPDATE CASCADE ON DELETE SET NULL"
            ),
        },
        "ticket_historial": {
            "fk_ticket_historial_ticket": (
                "ALTER TABLE ticket_historial ADD CONSTRAINT fk_ticket_historial_ticket "
                "FOREIGN KEY (ticket_id) REFERENCES ticket (id) "
                "ON UPDATE CASCADE ON DELETE SET NULL"
            ),
            "fk_ticket_historial_usuario": (
                "ALTER TABLE ticket_historial ADD CONSTRAINT fk_ticket_historial_usuario "
                "FOREIGN KEY (usuario_id) REFERENCES usuario (id) "
                "ON UPDATE CASCADE ON DELETE SET NULL"
            ),
        },
        "invitacion_usuario": {
            "fk_invitacion_usuario_invitado_por": (
                "ALTER TABLE invitacion_usuario ADD CONSTRAINT fk_invitacion_usuario_invitado_por "
                "FOREIGN KEY (invitado_por_id) REFERENCES usuario (id) "
                "ON UPDATE CASCADE ON DELETE SET NULL"
            ),
        },
    }

    CHECK_CONSTRAINTS = {
        "usuario": {
            "chk_usuario_email_not_empty": "TRIM(email) <> ''",
            "chk_usuario_nombre_not_empty": "nombre IS NULL OR TRIM(nombre) <> ''",
            "chk_usuario_telefono_not_empty": "telefono IS NULL OR TRIM(telefono) <> ''",
            "chk_usuario_cargo_not_empty": "cargo IS NULL OR TRIM(cargo) <> ''",
            "chk_usuario_rol": "rol IN ('admin', 'cliente')",
        },
        "ticket": {
            "chk_ticket_titulo_not_empty": "TRIM(titulo) <> ''",
            "chk_ticket_descripcion_not_empty": "TRIM(descripcion) <> ''",
            "chk_ticket_tipo_not_empty": "TRIM(tipo_ticket) <> ''",
            "chk_ticket_area_not_empty": "TRIM(area) <> ''",
            "chk_ticket_departamento_not_empty": "TRIM(departamento) <> ''",
            "chk_ticket_estado": "estado IN ('pendiente', 'proceso', 'resuelto')",
            "chk_ticket_prioridad": "prioridad IN ('baja', 'media', 'alta', 'critica')",
            "chk_ticket_resuelto_con_cierre": (
                "estado <> 'resuelto' OR (cerrado_en IS NOT NULL "
                "AND solucion_cierre IS NOT NULL AND TRIM(solucion_cierre) <> '')"
            ),
        },
        "ticket_historial": {
            "chk_ticket_historial_accion": "accion IN ('creado', 'actualizado', 'eliminado')",
            "chk_ticket_historial_campo_not_empty": "campo IS NULL OR TRIM(campo) <> ''",
        },
        "invitacion_usuario": {
            "chk_invitacion_usuario_email_not_empty": "TRIM(email) <> ''",
            "chk_invitacion_usuario_rol": "rol IN ('admin', 'cliente')",
            "chk_invitacion_usuario_expira_despues_creada": "expira_en > creada_en",
            "chk_invitacion_usuario_usada_con_fecha": "usada = false OR usada_en IS NOT NULL",
        },
    }

    def sync(self):
        inspector = inspect(db.engine)

        self.sync_columns(inspector, "usuario", self.USER_COLUMNS)
        self.sync_columns(inspector, "ticket", self.TICKET_COLUMNS)
        self.sync_columns(inspector, "invitacion_usuario", self.INVITATION_COLUMNS)
        self.backfill_legacy_data(inspector)
        self.sync_column_definitions(inspector)
        self.sync_indexes(inspector)
        self.sync_foreign_keys(inspector)
        self.sync_check_constraints(inspector)

        db.session.commit()

    def sync_columns(self, inspector, table_name, columns):
        if not inspector.has_table(table_name):
            return

        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}

        for column_name, column_definition in columns.items():
            if column_name not in existing_columns:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))

    def sync_column_definitions(self, inspector):
        if db.engine.dialect.name != "mysql":
            return

        for table_name, columns in self.COLUMN_DEFINITIONS.items():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}

            for column_name, column_definition in columns.items():
                if column_name in existing_columns:
                    db.session.execute(text(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_definition}"))

    def sync_indexes(self, inspector):
        for table_name, indexes in self.INDEXES.items():
            if not inspector.has_table(table_name):
                continue

            existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}

            for index_name, statement in indexes.items():
                if index_name not in existing_indexes:
                    db.session.execute(text(statement))

    def sync_foreign_keys(self, inspector):
        for table_name, foreign_keys in self.FOREIGN_KEYS.items():
            if not inspector.has_table(table_name):
                continue

            existing_foreign_keys = {foreign_key["name"] for foreign_key in inspector.get_foreign_keys(table_name)}

            for foreign_key_name, statement in foreign_keys.items():
                if foreign_key_name not in existing_foreign_keys:
                    db.session.execute(text(statement))

    def sync_check_constraints(self, inspector):
        for table_name, constraints in self.CHECK_CONSTRAINTS.items():
            if not inspector.has_table(table_name):
                continue

            existing_constraints = {
                constraint["name"]
                for constraint in inspector.get_check_constraints(table_name)
            }

            for constraint_name, condition in constraints.items():
                if constraint_name not in existing_constraints:
                    db.session.execute(text(
                        f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK ({condition})"
                    ))

    def backfill_legacy_data(self, inspector):
        if inspector.has_table("usuario"):
            db.session.execute(text(
                "UPDATE usuario SET rol = 'cliente' WHERE rol IS NULL OR rol NOT IN ('admin', 'cliente')"
            ))

        if inspector.has_table("ticket"):
            db.session.execute(text(
                "UPDATE ticket SET tipo_ticket = 'General' WHERE tipo_ticket IS NULL OR TRIM(tipo_ticket) = ''"
            ))
            db.session.execute(text(
                "UPDATE ticket SET area = 'Sin area' WHERE area IS NULL OR TRIM(area) = ''"
            ))
            db.session.execute(text(
                "UPDATE ticket SET departamento = 'Sin departamento' WHERE departamento IS NULL OR TRIM(departamento) = ''"
            ))
            db.session.execute(text(
                "UPDATE ticket SET prioridad = 'media' WHERE prioridad IS NULL OR prioridad NOT IN ('baja', 'media', 'alta', 'critica')"
            ))
            db.session.execute(text(
                "UPDATE ticket SET estado = 'pendiente' WHERE estado IS NULL OR estado NOT IN ('pendiente', 'proceso', 'resuelto')"
            ))
            db.session.execute(text(
                "UPDATE ticket "
                "SET cerrado_en = COALESCE(cerrado_en, actualizado_en, creado_en, CURRENT_TIMESTAMP), "
                "cerrado_por_id = COALESCE(cerrado_por_id, asignado_a_id, usuario_id), "
                "solucion_cierre = COALESCE(NULLIF(TRIM(solucion_cierre), ''), 'Cierre migrado sin detalle registrado') "
                "WHERE estado = 'resuelto'"
            ))

        if inspector.has_table("ticket_historial"):
            db.session.execute(text(
                "UPDATE ticket_historial SET accion = 'actualizado' "
                "WHERE accion IS NULL OR accion NOT IN ('creado', 'actualizado', 'eliminado')"
            ))

        if inspector.has_table("invitacion_usuario"):
            db.session.execute(text(
                "UPDATE invitacion_usuario SET rol = 'cliente' WHERE rol IS NULL OR rol NOT IN ('admin', 'cliente')"
            ))
            db.session.execute(text(
                "UPDATE invitacion_usuario SET usada_en = CURRENT_TIMESTAMP WHERE usada = true AND usada_en IS NULL"
            ))

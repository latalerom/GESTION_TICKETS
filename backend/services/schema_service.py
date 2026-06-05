from sqlalchemy import inspect, text

from models import db


class SchemaService:
    TICKET_COLUMNS = {
        "tipo_ticket": "VARCHAR(100) DEFAULT 'General'",
        "observacion": "TEXT NULL",
        "reportado_por": "VARCHAR(100) NULL",
        "area": "VARCHAR(100) NULL",
        "departamento": "VARCHAR(100) NULL",
        "prioridad": "VARCHAR(50) DEFAULT 'media'",
        "creado_en": "DATETIME DEFAULT CURRENT_TIMESTAMP",
    }

    def sync(self):
        inspector = inspect(db.engine)

        if not inspector.has_table("ticket"):
            return

        existing_columns = {column["name"] for column in inspector.get_columns("ticket")}

        for column_name, column_definition in self.TICKET_COLUMNS.items():
            if column_name not in existing_columns:
                db.session.execute(text(f"ALTER TABLE ticket ADD COLUMN {column_name} {column_definition}"))

        db.session.commit()

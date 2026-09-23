import os
from secrets import token_urlsafe

from models import Usuario, db
from werkzeug.security import generate_password_hash


class DatabaseSeeder:
    INITIAL_USERS = (
        {
            "nombre": "Admin",
            "email": "admin@gmail.com",
            "rol": "admin",
        },
        {
            "nombre": "Cliente",
            "email": "cliente@gmail.com",
            "rol": "cliente",
        },
    )

    def seed(self):
        if os.environ.get("ENABLE_DEMO_USERS", "false").lower() != "true":
            return

        for user_data in self.INITIAL_USERS:
            existing_user = Usuario.query.filter_by(email=user_data["email"]).first()
            password = os.environ.get(
                f"DEMO_{user_data['rol'].upper()}_PASSWORD",
                f"Soporte-{token_urlsafe(10)}1",
            )

            if existing_user is None:
                db.session.add(Usuario(
                    nombre=user_data["nombre"],
                    email=user_data["email"],
                    password=generate_password_hash(password),
                    rol=user_data["rol"],
                ))

        db.session.commit()

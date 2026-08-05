from models import Usuario, db
from werkzeug.security import generate_password_hash


class DatabaseSeeder:
    INITIAL_USERS = (
        {
            "nombre": "Admin",
            "email": "admin@gmail.com",
            "password": "1234",
            "rol": "admin",
        },
        {
            "nombre": "Cliente",
            "email": "cliente@gmail.com",
            "password": "1234",
            "rol": "cliente",
        },
    )

    def seed(self):
        for user_data in self.INITIAL_USERS:
            existing_user = Usuario.query.filter_by(email=user_data["email"]).first()

            if existing_user is None:
                db.session.add(Usuario(
                    nombre=user_data["nombre"],
                    email=user_data["email"],
                    password=generate_password_hash(user_data["password"]),
                    rol=user_data["rol"],
                ))

        db.session.commit()

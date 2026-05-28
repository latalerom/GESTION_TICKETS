from models import Usuario
from werkzeug.security import check_password_hash


class AuthService:
    def authenticate(self, email, password):
        if not email or not password:
            return None

        user = Usuario.query.filter_by(email=email).first()

        if user is None:
            return None

        if self.password_matches(user.password, password):
            return user

        return None

    def get_user_by_id(self, user_id):
        if user_id is None:
            return None

        return Usuario.query.get(user_id)

    def password_matches(self, stored_password, plain_password):
        if stored_password.startswith("scrypt:") or stored_password.startswith("pbkdf2:"):
            return check_password_hash(stored_password, plain_password)

        return stored_password == plain_password

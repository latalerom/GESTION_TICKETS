from pathlib import Path

from flask import Flask, send_from_directory

from config import Config
from controllers.auth_controller import auth_bp
from controllers.ticket_controller import ticket_bp
from models import db
from services.database_seeder import DatabaseSeeder
from swagger.swagger_config import SwaggerConfig

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


class ApplicationFactory:
    def __init__(self, config_class=Config, frontend_dir=FRONTEND_DIR):
        self.config_class = config_class
        self.frontend_dir = frontend_dir

    def create(self):
        app = Flask(__name__)
        app.config.from_object(self.config_class)

        db.init_app(app)
        SwaggerConfig.init_app(app)

        self.register_blueprints(app)
        self.register_frontend_routes(app)
        self.initialize_database(app)

        return app

    def register_blueprints(self, app):
        app.register_blueprint(auth_bp)
        app.register_blueprint(ticket_bp)

    def register_frontend_routes(self, app):
        @app.route("/")
        def index():
            return send_from_directory(self.frontend_dir, "index.html")

        @app.route("/<path:filename>")
        def frontend(filename):
            return send_from_directory(self.frontend_dir, filename)

    def initialize_database(self, app):
        with app.app_context():
            db.create_all()
            DatabaseSeeder().seed()


def create_app():
    return ApplicationFactory().create()


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@mysql_db:3306/soporte_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret123")
    APP_URL = os.environ.get("APP_URL", "http://localhost:5001")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_SENDER = os.environ.get("MAIL_SENDER", MAIL_USERNAME or "no-reply@soporte.local")

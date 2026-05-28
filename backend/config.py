import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@mysql_db:3306/soporte_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
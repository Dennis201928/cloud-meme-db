from flask import Flask
from app.database.db_mysql import init_db
from decouple import config


def init_app():
    app = Flask(__name__)
    app.secret_key = config("PROJECT_KEY", default="MEME_CC")
    init_db(app)
    return app

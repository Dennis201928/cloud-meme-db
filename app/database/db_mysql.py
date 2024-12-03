from flask_sqlalchemy import SQLAlchemy
from decouple import config
import traceback

db = SQLAlchemy()

# Logger
from app.utils.Logger import Logger


def create_db_uri():
    try:
        host = config('AWS_MYSQL_URL')
        user = config('AWS_MYSQL_USER')
        password = config('AWS_MYSQL_PASSWORD')
        db_name = config('AWS_MYSQL_DB_NAME')
        port = config('AWS_MYSQL_PORT')
        print(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}')
        return f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}'
    except Exception as e:
        Logger.add_to_log("error", "Error al generar la URI de la base de datos")
        Logger.add_to_log("error", str(e))
        Logger.add_to_log("error", traceback.format_exc())
        raise


def check_db_connection(app):
    try:
        with app.app_context():
            db.session.execute('SELECT 1')
        return True
    except Exception as err:
        Logger.add_to_log("error", "La base de datos no está activa")
        Logger.add_to_log("error", str(err))
        Logger.add_to_log("error", traceback.format_exc())
        return False


def init_db(app):
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = create_db_uri()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

        db.init_app(app)
        #
        if not check_db_connection(app):
            Logger.add_to_log("critical", "No se pudo conectar a la base de datos. Verifique la configuración.")
            raise Exception("Conexión a la base de datos fallida")

        Logger.add_to_log("info", "Conexión a la base de datos establecida correctamente")
    except Exception as e:
        Logger.add_to_log("error", "Error al configurar la aplicación con SQLAlchemy")
        Logger.add_to_log("error", str(e))
        Logger.add_to_log("error", traceback.format_exc())
        raise

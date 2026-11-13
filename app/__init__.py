
from flask import Flask
from flask_cors import CORS
import logging

from app.routes.usuarios import usuarios_bp
from app.routes.publicaciones import publicaciones_bp


def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("contentflow.log", encoding="utf-8")
        ],
        force=True
    )


def create_app():
    configurar_logging()

    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(publicaciones_bp)

    @app.route("/", methods=["GET"])
    def home():
        return {
            "mensaje": "API ContentFlow funcionando correctamente",
            "estado": "OK"
        }, 200

    return app

from flask import Flask

from app.api.v1.notifications import router
from app.config import settings
from app.db.base import db
from app.db import models


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(router, url_prefix="/api/v1")

    @app.route("/", methods=["GET"])
    def root():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()

    return app

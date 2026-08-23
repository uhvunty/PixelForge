from flask import Flask

from config import Config

from extensions import (
    db,
    login_manager
)

from models import User

from routes.auth import auth_bp
from routes.main import main_bp
from routes.studio import studio_bp
from routes.multiplayer import multiplayer_bp

from flask_migrate import Migrate


def create_app():

    app = Flask(__name__)

    app.config.from_object(
        Config
    )

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    db.init_app(app)

    # -----------------------------------------
    # LOGIN
    # -----------------------------------------

    login_manager.init_app(
        app
    )

    login_manager.login_view = (
        "auth.login"
    )

    # -----------------------------------------
    # MIGRATIONS
    # -----------------------------------------

    Migrate(
        app,
        db
    )

    # -----------------------------------------
    # BLUEPRINTS
    # -----------------------------------------

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        main_bp
    )

    app.register_blueprint(
        studio_bp
    )

    app.register_blueprint(
        multiplayer_bp
    )

    # -----------------------------------------
    # CREATE NEW TABLES
    # -----------------------------------------

    with app.app_context():

        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):

    try:

        return db.session.get(
            User,
            int(user_id)
        )

    except (
        TypeError,
        ValueError
    ):

        return None


app = create_app()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
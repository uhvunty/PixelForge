from flask import Flask

from config import Config

from extensions import (
    db,
    login_manager,
    socketio
)

from models import User

from routes.auth import auth_bp
from routes.main import main_bp
from routes.studio import studio_bp
from routes.multiplayer import multiplayer_bp

from flask_migrate import Migrate


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*"
    )

    login_manager.login_view = "auth.login"

    Migrate(
        app,
        db
    )

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

    return app


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


app = create_app()


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )
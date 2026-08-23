from app import app
from extensions import db


def initialize_database():

    with app.app_context():

        db.create_all()

        print(
            "PixelForge database initialized successfully."
        )


if __name__ == "__main__":

    initialize_database()
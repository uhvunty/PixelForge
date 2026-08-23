from datetime import datetime

from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db


class User(
    db.Model,
    UserMixin
):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    artworks = db.relationship(
        "Artwork",
        backref="owner",
        lazy=True
    )

    # -------------------------
    # PASSWORD FUNCTIONS
    # -------------------------

    def set_password(self, password):

        self.password = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password,
            password
        )


class Artwork(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(100),
        default="Untitled"
    )

    width = db.Column(
        db.Integer,
        default=32
    )

    height = db.Column(
        db.Integer,
        default=32
    )

    pixel_data = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "user.id"
        ),
        nullable=False
    )


class Room(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(12),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100)
    )

    grid_size = db.Column(
        db.Integer,
        default=64
    )

    canvas = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
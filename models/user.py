from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from extensions import db


class User(
    UserMixin,
    db.Model
):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    artworks = db.relationship(
        "Artwork",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    rooms = db.relationship(
        "Room",
        back_populates="creator"
    )

    pixels = db.relationship(
        "Pixel",
        back_populates="user"
    )

    def set_password(
        self,
        password
    ):

        self.password_hash = (
            generate_password_hash(
                password
            )
        )

    def check_password(
        self,
        password
    ):

        return check_password_hash(
            self.password_hash,
            password
        )

    def to_dict(self):

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at":
                self.created_at.isoformat()
        }
from datetime import datetime

from extensions import db


class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    room_code = db.Column(
        db.String(12),
        unique=True,
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    width = db.Column(
        db.Integer,
        nullable=False,
        default=64
    )

    height = db.Column(
        db.Integer,
        nullable=False,
        default=64
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    creator = db.relationship(
        "User",
        back_populates="rooms"
    )

    pixels = db.relationship(
        "Pixel",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "room_code":
                self.room_code,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "created_by":
                self.created_by,
            "created_at":
                self.created_at.isoformat()
        }
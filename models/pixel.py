from datetime import datetime

from extensions import db


class Pixel(db.Model):

    __tablename__ = "pixels"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "rooms.id"
        ),
        nullable=False,
        index=True
    )

    x = db.Column(
        db.Integer,
        nullable=False
    )

    y = db.Column(
        db.Integer,
        nullable=False
    )

    color = db.Column(
        db.String(7),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    room = db.relationship(
        "Room",
        back_populates="pixels"
    )

    user = db.relationship(
        "User",
        back_populates="pixels"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "room_id",
            "x",
            "y",
            name="unique_room_pixel"
        ),
    )

    def to_dict(self):

        return {
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "user_id": self.user_id
        }
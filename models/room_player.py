from datetime import datetime

from extensions import db


class RoomPlayer(db.Model):

    __tablename__ = "room_players"

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

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False,
        index=True
    )

    last_seen = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    room = db.relationship(
        "Room",
        back_populates="players"
    )

    user = db.relationship(
        "User"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "room_id",
            "user_id",
            name="unique_room_player"
        ),
    )

    def to_dict(self):

        return {
            "user_id": self.user_id,
            "username": (
                self.user.username
                if self.user
                else None
            ),
            "last_seen": (
                self.last_seen.isoformat()
                if self.last_seen
                else None
            )
        }
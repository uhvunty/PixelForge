from datetime import datetime

from extensions import db


class Artwork(db.Model):

    __tablename__ = "artworks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    width = db.Column(
        db.Integer,
        nullable=False
    )

    height = db.Column(
        db.Integer,
        nullable=False
    )

    pixel_data = db.Column(
        db.Text,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="artworks"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "pixel_data":
                self.pixel_data,
            "user_id": self.user_id,
            "username":
                self.user.username
                if self.user
                else None,
            "created_at":
                self.created_at.isoformat()
        }
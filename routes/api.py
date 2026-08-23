import json

from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_login import (
    current_user,
    login_required
)

from app import db
from config import Config
from models.artwork import Artwork
from models.room import Room
from services.pixel_converter import (
    validate_pixel_data
)
from services.redis_manager import (
    get_player_state,
    get_room_pixels
)


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api_bp.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok",
        "application": "PixelForge"
    })


@api_bp.route(
    "/me",
    methods=["GET"]
)
@login_required
def current_user_api():

    return jsonify({
        "success": True,
        "user": current_user.to_dict()
    })


@api_bp.route(
    "/artworks",
    methods=["GET"]
)
@login_required
def get_artworks():

    artworks = db.session.scalars(
        db.select(Artwork)
        .where(
            Artwork.user_id ==
            current_user.id
        )
        .order_by(
            Artwork.created_at.desc()
        )
    ).all()

    return jsonify({
        "success": True,
        "artworks": [
            artwork.to_dict()
            for artwork in artworks
        ]
    })


@api_bp.route(
    "/artworks/<int:artwork_id>",
    methods=["GET"]
)
@login_required
def get_artwork(
    artwork_id
):

    artwork = db.session.scalar(
        db.select(Artwork).where(
            Artwork.id == artwork_id,
            Artwork.user_id ==
            current_user.id
        )
    )

    if artwork is None:

        return jsonify({
            "success": False,
            "error": "Artwork not found."
        }), 404

    return jsonify({
        "success": True,
        "artwork": artwork.to_dict()
    })


@api_bp.route(
    "/artworks",
    methods=["POST"]
)
@login_required
def create_artwork():

    data = request.get_json(
        silent=True
    )

    if not isinstance(
        data,
        dict
    ):

        return jsonify({
            "success": False,
            "error": "Invalid JSON body."
        }), 400

    title = str(
        data.get(
            "title",
            "Untitled Artwork"
        )
    ).strip()

    if not title:

        title = "Untitled Artwork"

    title = title[:100]

    pixel_data = data.get(
        "pixel_data"
    )

    if isinstance(
        pixel_data,
        str
    ):

        try:
            pixel_data = json.loads(
                pixel_data
            )
        except json.JSONDecodeError:

            return jsonify({
                "success": False,
                "error": "Invalid pixel data."
            }), 400

    if not validate_pixel_data(
        pixel_data,
        max_size=64
    ):

        return jsonify({
            "success": False,
            "error": "Invalid pixel data."
        }), 400

    artwork = Artwork(
        title=title,
        width=int(
            pixel_data["width"]
        ),
        height=int(
            pixel_data["height"]
        ),
        pixel_data=json.dumps(
            pixel_data,
            separators=(
                ",",
                ":"
            )
        ),
        user_id=current_user.id
    )

    db.session.add(
        artwork
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "artwork":
            artwork.to_dict()
    }), 201


@api_bp.route(
    "/artworks/<int:artwork_id>",
    methods=["DELETE"]
)
@login_required
def delete_artwork(
    artwork_id
):

    artwork = db.session.scalar(
        db.select(Artwork).where(
            Artwork.id == artwork_id,
            Artwork.user_id ==
            current_user.id
        )
    )

    if artwork is None:

        return jsonify({
            "success": False,
            "error": "Artwork not found."
        }), 404

    db.session.delete(
        artwork
    )

    db.session.commit()

    return jsonify({
        "success": True
    })


@api_bp.route(
    "/rooms/<room_code>/pixels",
    methods=["GET"]
)
@login_required
def room_pixels(
    room_code
):

    room_code = (
        room_code.strip().upper()
    )

    room = db.session.scalar(
        db.select(Room).where(
            Room.room_code ==
            room_code
        )
    )

    if room is None:

        return jsonify({
            "success": False,
            "error": "Room not found."
        }), 404

    pixels = get_room_pixels(
        room_code
    )

    return jsonify({
        "success": True,
        "room": room.to_dict(),
        "pixels": pixels
    })


@api_bp.route(
    "/rooms/<room_code>/player-state",
    methods=["GET"]
)
@login_required
def room_player_state(
    room_code
):

    room_code = (
        room_code.strip().upper()
    )

    room = db.session.scalar(
        db.select(Room).where(
            Room.room_code ==
            room_code
        )
    )

    if room is None:

        return jsonify({
            "success": False,
            "error": "Room not found."
        }), 404

    state = get_player_state(
        room_code,
        current_user.username
    )

    return jsonify({
        "success": True,
        "state": state
    })
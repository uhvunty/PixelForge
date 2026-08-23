import random
import string

from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db

from models import (
    Room,
    Pixel,
    RoomPlayer
)


multiplayer_bp = Blueprint(
    "multiplayer",
    __name__,
    url_prefix="/multiplayer"
)


DEFAULT_GRID_SIZE = 64

MAX_PLAYERS = 3

PLAYER_TIMEOUT_SECONDS = 15


def generate_room_code():

    characters = (
        string.ascii_uppercase
        + string.digits
    )

    while True:

        code = "".join(
            random.choice(characters)
            for _ in range(6)
        )

        existing = Room.query.filter_by(
            room_code=code
        ).first()

        if existing is None:

            return code


def cleanup_players(room):

    cutoff = (
        datetime.utcnow()
        - timedelta(
            seconds=PLAYER_TIMEOUT_SECONDS
        )
    )

    RoomPlayer.query.filter(
        RoomPlayer.room_id == room.id,
        RoomPlayer.last_seen < cutoff
    ).delete(
        synchronize_session=False
    )

    db.session.commit()


def get_player_count(room):

    cleanup_players(room)

    return RoomPlayer.query.filter_by(
        room_id=room.id
    ).count()


def get_current_player(room):

    return RoomPlayer.query.filter_by(
        room_id=room.id,
        user_id=current_user.id
    ).first()


def get_canvas(room):

    pixels = Pixel.query.filter_by(
        room_id=room.id
    ).all()

    return {
        "width": room.width,
        "height": room.height,
        "pixels": [
            pixel.to_dict()
            for pixel in pixels
        ]
    }


# =========================================================
# MULTIPLAYER HOME
# =========================================================

@multiplayer_bp.route("/")
@login_required
def multiplayer():

    return render_template(
        "join_room.html"
    )


# =========================================================
# CREATE ROOM
# =========================================================

@multiplayer_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create_room():

    if request.method == "GET":

        return render_template(
            "create_room.html"
        )

    room_name = request.form.get(
        "room_name",
        "Pixel Room"
    ).strip()

    if not room_name:

        room_name = "Pixel Room"

    room_name = room_name[:100]

    try:

        grid_size = int(
            request.form.get(
                "grid_size",
                DEFAULT_GRID_SIZE
            )
        )

    except (
        TypeError,
        ValueError
    ):

        grid_size = DEFAULT_GRID_SIZE

    if grid_size not in (
        32,
        64
    ):

        grid_size = DEFAULT_GRID_SIZE

    room = Room(
        room_code=generate_room_code(),
        name=room_name,
        width=grid_size,
        height=grid_size,
        created_by=current_user.id
    )

    db.session.add(room)

    db.session.commit()

    return redirect(
        url_for(
            "multiplayer.room",
            room_code=room.room_code
        )
    )


# =========================================================
# JOIN PAGE
# =========================================================

@multiplayer_bp.route(
    "/join",
    methods=["GET", "POST"]
)
@login_required
def join_room():

    if request.method == "GET":

        return render_template(
            "join_room.html"
        )

    code = request.form.get(
        "room_code",
        ""
    ).strip().upper()

    room = Room.query.filter_by(
        room_code=code
    ).first()

    if room is None:

        flash(
            "Room not found.",
            "error"
        )

        return redirect(
            url_for(
                "multiplayer.join_room"
            )
        )

    return redirect(
        url_for(
            "multiplayer.room",
            room_code=room.room_code
        )
    )


# =========================================================
# ROOM PAGE
# =========================================================

@multiplayer_bp.route(
    "/room/<room_code>"
)
@login_required
def room(room_code):

    room = Room.query.filter_by(
        room_code=room_code.upper()
    ).first_or_404()

    return render_template(
        "multiplayer.html",
        room_code=room.room_code,
        room_name=room.name,
        grid_size=room.width
    )


# =========================================================
# JOIN API
# =========================================================

@multiplayer_bp.route(
    "/api/<room_code>/join",
    methods=["POST"]
)
@login_required
def api_join_room(room_code):

    room = Room.query.filter_by(
        room_code=room_code.upper()
    ).first()

    if room is None:

        return jsonify({
            "success": False,
            "message": "Room does not exist."
        }), 404

    cleanup_players(room)

    existing_player = get_current_player(
        room
    )

    # Already in the room.
    if existing_player:

        existing_player.last_seen = (
            datetime.utcnow()
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "players": get_player_count(room),
            "max_players": MAX_PLAYERS,
            "canvas": get_canvas(room)
        })

    player_count = get_player_count(
        room
    )

    if player_count >= MAX_PLAYERS:

        return jsonify({
            "success": False,
            "message": (
                "This room is full. "
                "Maximum 3 players are allowed."
            )
        }), 409

    player = RoomPlayer(
        room_id=room.id,
        user_id=current_user.id,
        last_seen=datetime.utcnow()
    )

    db.session.add(player)

    db.session.commit()

    return jsonify({
        "success": True,
        "players": get_player_count(room),
        "max_players": MAX_PLAYERS,
        "canvas": get_canvas(room)
    })


# =========================================================
# ROOM STATE
# =========================================================

@multiplayer_bp.route(
    "/api/<room_code>/state"
)
@login_required
def api_room_state(room_code):

    room = Room.query.filter_by(
        room_code=room_code.upper()
    ).first()

    if room is None:

        return jsonify({
            "success": False,
            "message": "Room does not exist."
        }), 404

    player = get_current_player(
        room
    )

    if player is None:

        return jsonify({
            "success": False,
            "message": (
                "You are not currently "
                "in this room."
            )
        }), 403

    player.last_seen = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "players": get_player_count(room),
        "max_players": MAX_PLAYERS,
        "canvas": get_canvas(room)
    })


# =========================================================
# PAINT PIXEL
# =========================================================

@multiplayer_bp.route(
    "/api/<room_code>/paint",
    methods=["POST"]
)
@login_required
def api_paint_pixel(room_code):

    room = Room.query.filter_by(
        room_code=room_code.upper()
    ).first()

    if room is None:

        return jsonify({
            "success": False,
            "message": "Room does not exist."
        }), 404

    player = get_current_player(
        room
    )

    if player is None:

        return jsonify({
            "success": False,
            "message": (
                "You are not currently "
                "in this room."
            )
        }), 403

    player.last_seen = datetime.utcnow()

    data = request.get_json(
        silent=True
    ) or {}

    try:

        x = int(
            data.get("x")
        )

        y = int(
            data.get("y")
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid pixel position."
        }), 400

    color = str(
        data.get(
            "color",
            "#000000"
        )
    ).strip().lower()

    if (
        not color.startswith("#")
        or len(color) not in (
            4,
            7
        )
    ):

        return jsonify({
            "success": False,
            "message": "Invalid color."
        }), 400

    if not (
        0 <= x < room.width
        and
        0 <= y < room.height
    ):

        return jsonify({
            "success": False,
            "message": (
                "Pixel is outside "
                "the canvas."
            )
        }), 400

    pixel = Pixel.query.filter_by(
        room_id=room.id,
        x=x,
        y=y
    ).first()

    if pixel:

        pixel.color = color

        pixel.user_id = current_user.id

        pixel.updated_at = datetime.utcnow()

    else:

        pixel = Pixel(
            room_id=room.id,
            x=x,
            y=y,
            color=color,
            user_id=current_user.id
        )

        db.session.add(pixel)

    db.session.commit()

    return jsonify({
        "success": True,
        "x": x,
        "y": y,
        "color": color,
        "username": current_user.username
    })


# =========================================================
# LEAVE ROOM
# =========================================================

@multiplayer_bp.route(
    "/api/<room_code>/leave",
    methods=["POST"]
)
@login_required
def api_leave_room(room_code):

    room = Room.query.filter_by(
        room_code=room_code.upper()
    ).first()

    if room is None:

        return jsonify({
            "success": False
        }), 404

    player = get_current_player(
        room
    )

    if player:

        db.session.delete(player)

        db.session.commit()

    return jsonify({
        "success": True,
        "players": get_player_count(room),
        "max_players": MAX_PLAYERS
    })
import json
import random
import string
import time

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

from extensions import (
    db,
    socketio
)

from models import Room

from flask_socketio import (
    emit,
    join_room,
    leave_room
)


multiplayer_bp = Blueprint(
    "multiplayer",
    __name__,
    url_prefix="/multiplayer"
)


DEFAULT_GRID_SIZE = 64

PIXEL_LIMIT = 100

PIXEL_COOLDOWN = 1


active_players = {}

pixel_timestamps = {}



def generate_room_code():

    characters = (
        string.ascii_uppercase
        + string.digits
    )


    while True:

        code = "".join(
            random.choice(
                characters
            )
            for _ in range(6)
        )


        if not Room.query.filter_by(
            code=code
        ).first():

            return code



def create_empty_canvas(
    size
):

    pixels = []

    for y in range(size):

        for x in range(size):

            pixels.append({
                "x": x,
                "y": y,
                "color": "#ffffff"
            })


    return {
        "width": size,
        "height": size,
        "pixels": pixels
    }



def get_room_canvas(room):

    try:

        return json.loads(
            room.canvas
        )

    except (
        json.JSONDecodeError,
        TypeError
    ):

        return create_empty_canvas(
            room.grid_size
        )



@multiplayer_bp.route("/")
@login_required
def multiplayer():

    return render_template(
        "join_room.html"
    )



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

    except ValueError:

        grid_size = DEFAULT_GRID_SIZE


    if grid_size not in (
        32,
        64
    ):

        grid_size = DEFAULT_GRID_SIZE


    code = generate_room_code()


    canvas = create_empty_canvas(
        grid_size
    )


    room = Room(
        code=code,
        name=room_name,
        grid_size=grid_size,
        canvas=json.dumps(
            canvas
        )
    )


    db.session.add(
        room
    )

    db.session.commit()


    return redirect(
        url_for(
            "multiplayer.room",
            room_code=code
        )
    )



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
        code=code
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
            room_code=room.code
        )
    )



@multiplayer_bp.route(
    "/room/<room_code>"
)
@login_required
def room(room_code):

    room = Room.query.filter_by(
        code=room_code.upper()
    ).first_or_404()


    return render_template(
        "multiplayer.html",
        room_code=room.code,
        room_name=room.name,
        grid_size=room.grid_size
    )



@multiplayer_bp.route(
    "/api/<room_code>"
)
@login_required
def room_data(room_code):

    room = Room.query.filter_by(
        code=room_code.upper()
    ).first_or_404()


    canvas = get_room_canvas(
        room
    )


    return jsonify({
        "success": True,
        "room": {
            "code": room.code,
            "name": room.name,
            "grid_size": room.grid_size
        },
        "canvas": canvas
    })



@socketio.on("join_canvas")
def handle_join_canvas(data):

    if not current_user.is_authenticated:

        return


    room_code = str(
        data.get(
            "room_code",
            ""
        )
    ).upper()


    room = Room.query.filter_by(
        code=room_code
    ).first()


    if room is None:

        emit(
            "canvas_error",
            {
                "message": "Room does not exist."
            }
        )

        return


    join_room(
        room_code
    )


    active_players.setdefault(
        room_code,
        set()
    )


    active_players[
        room_code
    ].add(
        current_user.id
    )


    canvas = get_room_canvas(
        room
    )


    emit(
        "canvas_state",
        {
            "canvas": canvas
        }
    )


    emit(
        "player_count",
        {
            "count": len(
                active_players[
                    room_code
                ]
            )
        },
        to=room_code
    )


    emit(
        "player_joined",
        {
            "username":
                current_user.username
        },
        to=room_code,
        include_self=False
    )



@socketio.on("paint_pixel")
def handle_paint_pixel(data):

    if not current_user.is_authenticated:

        return


    room_code = str(
        data.get(
            "room_code",
            ""
        )
    ).upper()


    room = Room.query.filter_by(
        code=room_code
    ).first()


    if room is None:

        emit(
            "canvas_error",
            {
                "message": "Room does not exist."
            }
        )

        return


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

        emit(
            "canvas_error",
            {
                "message": "Invalid pixel position."
            }
        )

        return


    color = str(
        data.get(
            "color",
            "#000000"
        )
    )


    if (
        not color.startswith("#")
        or len(color) not in (
            4,
            7
        )
    ):

        emit(
            "canvas_error",
            {
                "message": "Invalid color."
            }
        )

        return


    if not (
        0 <= x < room.grid_size
        and 0 <= y < room.grid_size
    ):

        emit(
            "canvas_error",
            {
                "message": "Pixel is outside the canvas."
            }
        )

        return


    now = time.time()


    user_key = (
        room_code,
        current_user.id
    )


    last_timestamp = pixel_timestamps.get(
        user_key
    )


    if last_timestamp is not None:

        elapsed = (
            now - last_timestamp
        )


        if elapsed < PIXEL_COOLDOWN:

            remaining = int(
                PIXEL_COOLDOWN
                - elapsed
            ) + 1


            emit(
                "pixel_cooldown",
                {
                    "remaining":
                        remaining
                }
            )

            return


    pixel_timestamps[
        user_key
    ] = now


    canvas = get_room_canvas(
        room
    )


    found = False


    for pixel in canvas["pixels"]:

        if (
            pixel["x"] == x
            and pixel["y"] == y
        ):

            pixel["color"] = color
            found = True
            break


    if not found:

        canvas["pixels"].append({
            "x": x,
            "y": y,
            "color": color
        })


    room.canvas = json.dumps(
        canvas
    )


    db.session.commit()


    emit(
        "pixel_updated",
        {
            "x": x,
            "y": y,
            "color": color,
            "username":
                current_user.username
        },
        to=room_code
    )



@socketio.on("leave_canvas")
def handle_leave_canvas(data):

    if not current_user.is_authenticated:

        return


    room_code = str(
        data.get(
            "room_code",
            ""
        )
    ).upper()


    leave_room(
        room_code
    )


    if room_code in active_players:

        active_players[
            room_code
        ].discard(
            current_user.id
        )


        if not active_players[
            room_code
        ]:

            del active_players[
                room_code
            ]


    emit(
        "player_count",
        {
            "count": len(
                active_players.get(
                    room_code,
                    set()
                )
            )
        },
        to=room_code
    )
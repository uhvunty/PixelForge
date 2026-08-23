from extensions import socketio


class WebSocketManager:

    @staticmethod
    def join_room(
        socket_id,
        room_code
    ):
        from flask_socketio import join_room

        join_room(
            room_code,
            sid=socket_id
        )

    @staticmethod
    def leave_room(
        socket_id,
        room_code
    ):
        from flask_socketio import leave_room

        leave_room(
            room_code,
            sid=socket_id
        )

    @staticmethod
    def broadcast_pixel(
        room_code,
        x,
        y,
        color,
        username
    ):
        socketio.emit(
            "pixel_updated",
            {
                "x": x,
                "y": y,
                "color": color,
                "username": username
            },
            to=room_code
        )

    @staticmethod
    def broadcast_canvas(
        room_code,
        canvas
    ):
        socketio.emit(
            "canvas_state",
            {
                "canvas": canvas
            },
            to=room_code
        )

    @staticmethod
    def broadcast_player_count(
        room_code,
        count
    ):
        socketio.emit(
            "player_count",
            {
                "count": count
            },
            to=room_code
        )

    @staticmethod
    def broadcast_message(
        room_code,
        message
    ):
        socketio.emit(
            "room_message",
            {
                "message": message
            },
            to=room_code
        )

    @staticmethod
    def send_error(
        socket_id,
        message
    ):
        socketio.emit(
            "socket_error",
            {
                "message": message
            },
            to=socket_id
        )
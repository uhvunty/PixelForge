import secrets
import string


ROOM_ALPHABET = (
    string.ascii_uppercase +
    string.digits
)


def generate_room_code(length=6):

    return "".join(
        secrets.choice(
            ROOM_ALPHABET
        )
        for _ in range(length)
    )


def create_empty_canvas(
    width,
    height
):

    return {
        "width": width,
        "height": height,
        "pixels": [
            {
                "x": x,
                "y": y,
                "color": "#ffffff"
            }
            for y in range(height)
            for x in range(width)
        ]
    }


def update_canvas_pixel(
    canvas,
    x,
    y,
    color
):

    width = canvas["width"]
    height = canvas["height"]

    if not (
        0 <= x < width
        and
        0 <= y < height
    ):
        return False

    for pixel in canvas["pixels"]:

        if (
            pixel["x"] == x
            and
            pixel["y"] == y
        ):
            pixel["color"] = color
            return True

    return False
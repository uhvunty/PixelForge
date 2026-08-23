import json
import os
import uuid

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

from werkzeug.utils import secure_filename

from extensions import db

from models import Artwork

from services.pixel_converter import (
    convert_image_to_pixels
)


studio_bp = Blueprint(
    "studio",
    __name__,
    url_prefix="/studio"
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}



def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )



@studio_bp.route("/")
@login_required
def studio():

    return render_template(
        "studio.html"
    )



@studio_bp.route(
    "/convert",
    methods=["GET", "POST"]
)
@login_required
def convert():

    if request.method == "GET":

        return render_template(
            "convert.html"
        )


    uploaded_file = request.files.get(
        "image"
    )


    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):

        flash(
            "Please choose an image.",
            "error"
        )

        return redirect(
            url_for("studio.convert")
        )


    if not allowed_file(
        uploaded_file.filename
    ):

        flash(
            "Unsupported image format.",
            "error"
        )

        return redirect(
            url_for("studio.convert")
        )


    try:

        size = int(
            request.form.get(
                "size",
                32
            )
        )

    except ValueError:

        size = 32


    try:

        colors = int(
            request.form.get(
                "colors",
                16
            )
        )

    except ValueError:

        colors = 16


    size = max(
        8,
        min(
            size,
            128
        )
    )


    colors = max(
        2,
        min(
            colors,
            64
        )
    )


    try:

        pixel_data = convert_image_to_pixels(
            uploaded_file,
            size=size,
            colors=colors
        )

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

        return redirect(
            url_for("studio.convert")
        )

    except Exception:

        flash(
            "The image could not be processed.",
            "error"
        )

        return redirect(
            url_for("studio.convert")
        )


    return render_template(
        "pixel_result.html",
        pixel_data=pixel_data,
        title="My Pixel Art"
    )



@studio_bp.route(
    "/save",
    methods=["POST"]
)
@login_required
def save_artwork():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({
            "success": False,
            "message": "Invalid request."
        }), 400


    title = str(
        data.get(
            "title",
            "Untitled"
        )
    ).strip()


    if not title:

        title = "Untitled"


    title = title[:100]


    try:

        width = int(
            data.get(
                "width",
                32
            )
        )

        height = int(
            data.get(
                "height",
                width
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid canvas size."
        }), 400


    if (
        width < 1
        or width > 128
        or height < 1
        or height > 128
    ):

        return jsonify({
            "success": False,
            "message": "Canvas size is invalid."
        }), 400


    pixels = data.get(
        "pixels",
        []
    )


    if not isinstance(
        pixels,
        list
    ):

        return jsonify({
            "success": False,
            "message": "Invalid pixel data."
        }), 400


    cleaned_pixels = []


    for pixel in pixels:

        if not isinstance(
            pixel,
            dict
        ):

            continue


        try:

            x = int(
                pixel.get("x")
            )

            y = int(
                pixel.get("y")
            )

        except (
            TypeError,
            ValueError
        ):

            continue


        color = str(
            pixel.get(
                "color",
                "#ffffff"
            )
        )


        if (
            0 <= x < width
            and 0 <= y < height
        ):

            cleaned_pixels.append({
                "x": x,
                "y": y,
                "color": color
            })


    pixel_payload = {
        "width": width,
        "height": height,
        "pixels": cleaned_pixels
    }


    artwork = Artwork(
        title=title,
        width=width,
        height=height,
        pixel_data=json.dumps(
            pixel_payload
        ),
        user_id=current_user.id
    )


    db.session.add(
        artwork
    )

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Artwork saved successfully.",
        "artwork_id": artwork.id
    })



@studio_bp.route(
    "/artwork/<int:artwork_id>"
)
@login_required
def artwork(artwork_id):

    artwork = Artwork.query.filter_by(
        id=artwork_id,
        user_id=current_user.id
    ).first_or_404()


    try:

        pixel_data = json.loads(
            artwork.pixel_data
        )

    except (
        json.JSONDecodeError,
        TypeError
    ):

        pixel_data = {
            "width": artwork.width,
            "height": artwork.height,
            "pixels": []
        }


    return render_template(
        "pixel_result.html",
        pixel_data=pixel_data,
        title=artwork.title
    )
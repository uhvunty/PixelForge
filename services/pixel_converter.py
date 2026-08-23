import io
import math

import cv2
import numpy as np


ALLOWED_CHANNELS = {
    3,
    4
}


def _read_image(file):

    file.seek(0)

    raw = file.read()

    if not raw:
        raise ValueError(
            "The uploaded file is empty."
        )

    array = np.frombuffer(
        raw,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        array,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        raise ValueError(
            "The uploaded file is not a valid image."
        )

    return image



def _ensure_bgr(image):

    if image.ndim == 2:

        return cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2BGR
        )


    if image.shape[2] == 4:

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2BGR
        )


    return image



def _resize_pixel_image(
    image,
    size
):

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:

        raise ValueError(
            "Invalid image dimensions."
        )


    scale = min(
        size / width,
        size / height
    )


    new_width = max(
        1,
        int(width * scale)
    )


    new_height = max(
        1,
        int(height * scale)
    )


    resized = cv2.resize(
        image,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )


    canvas = np.full(
        (
            size,
            size,
            3
        ),
        255,
        dtype=np.uint8
    )


    x_offset = (
        size - new_width
    ) // 2

    y_offset = (
        size - new_height
    ) // 2


    canvas[
        y_offset:
        y_offset + new_height,
        x_offset:
        x_offset + new_width
    ] = resized


    return canvas



def _reduce_colors(
    image,
    colors
):

    pixels = image.reshape(
        -1,
        3
    ).astype(
        np.float32
    )


    criteria = (
        cv2.TERM_CRITERIA_EPS
        + cv2.TERM_CRITERIA_MAX_ITER,
        20,
        1.0
    )


    clusters = min(
        colors,
        len(pixels)
    )


    if clusters <= 1:

        return image


    compactness, labels, centers = cv2.kmeans(
        pixels,
        clusters,
        None,
        criteria,
        3,
        cv2.KMEANS_PP_CENTERS
    )


    centers = np.uint8(
        centers
    )


    result = centers[
        labels.flatten()
    ]


    return result.reshape(
        image.shape
    )



def _pixel_data_from_image(
    image
):

    height, width = image.shape[:2]

    pixels = []


    for y in range(height):

        for x in range(width):

            b, g, r = (
                image[y, x]
            )


            color = (
                f"#{int(r):02x}"
                f"{int(g):02x}"
                f"{int(b):02x}"
            )


            pixels.append({
                "x": x,
                "y": y,
                "color": color
            })


    return {
        "width": width,
        "height": height,
        "pixels": pixels
    }



def convert_image_to_pixels(
    file,
    size=32,
    colors=16
):

    try:

        size = int(size)

        colors = int(colors)

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid conversion settings."
        )


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


    image = _read_image(
        file
    )


    image = _ensure_bgr(
        image
    )


    image = _resize_pixel_image(
        image,
        size
    )


    image = _reduce_colors(
        image,
        colors
    )


    return _pixel_data_from_image(
        image
    )



def pixel_data_to_image(
    pixel_data
):

    if not isinstance(
        pixel_data,
        dict
    ):

        raise ValueError(
            "Invalid pixel data."
        )


    width = int(
        pixel_data.get(
            "width",
            32
        )
    )


    height = int(
        pixel_data.get(
            "height",
            width
        )
    )


    width = max(
        1,
        min(
            width,
            128
        )
    )


    height = max(
        1,
        min(
            height,
            128
        )
    )


    image = np.full(
        (
            height,
            width,
            3
        ),
        255,
        dtype=np.uint8
    )


    pixels = pixel_data.get(
        "pixels",
        []
    )


    if not isinstance(
        pixels,
        list
    ):

        return image


    for pixel in pixels:

        try:

            x = int(
                pixel["x"]
            )

            y = int(
                pixel["y"]
            )

            color = str(
                pixel["color"]
            )


            if (
                not color.startswith("#")
                or len(color) != 7
            ):

                continue


            color = color.lstrip(
                "#"
            )


            r = int(
                color[0:2],
                16
            )

            g = int(
                color[2:4],
                16
            )

            b = int(
                color[4:6],
                16
            )


            if (
                0 <= x < width
                and 0 <= y < height
            ):

                image[
                    y,
                    x
                ] = [
                    b,
                    g,
                    r
                ]

        except (
            KeyError,
            TypeError,
            ValueError,
            IndexError
        ):

            continue


    return image



def pixel_data_to_png(
    pixel_data
):

    image = pixel_data_to_image(
        pixel_data
    )


    success, encoded = cv2.imencode(
        ".png",
        image
    )


    if not success:

        raise ValueError(
            "Could not create PNG."
        )


    return io.BytesIO(
        encoded.tobytes()
    )
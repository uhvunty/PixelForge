from pathlib import Path

import cv2


class PixelArtProcessingError(Exception):
    """Raised when an image cannot be converted to pixel art."""


def _validate_dimensions(
    width: int,
    height: int
) -> None:

    if width not in {16, 32, 64}:
        raise ValueError(
            "Width must be 16, 32, or 64."
        )

    if height not in {16, 32, 64}:
        raise ValueError(
            "Height must be 16, 32, or 64."
        )


def _validate_colors(
    colors: int
) -> None:

    if colors not in {8, 16, 32}:
        raise ValueError(
            "Color count must be 8, 16, or 32."
        )


def convert_to_pixel_art(
    image_path: str,
    width: int = 32,
    height: int = 32,
    colors: int = 16
):
    """
    Convert an image into a small pixel-art image.

    OpenCV is used for:
    - image loading
    - resizing
    - color quantization
    - pixel-art reconstruction
    """

    _validate_dimensions(
        width,
        height
    )

    _validate_colors(
        colors
    )

    path = Path(image_path)

    if not path.exists():
        raise PixelArtProcessingError(
            "Image file does not exist."
        )

    image = cv2.imread(
        str(path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise PixelArtProcessingError(
            "The uploaded file is not a valid image."
        )

    try:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        image = _crop_to_square(
            image
        )

        small = cv2.resize(
            image,
            (width, height),
            interpolation=cv2.INTER_AREA
        )

        quantized = _quantize_colors(
            small,
            colors
        )

        pixel_art = cv2.resize(
            quantized,
            (
                width * 20,
                height * 20
            ),
            interpolation=cv2.INTER_NEAREST
        )

        return pixel_art

    except Exception as exc:

        raise PixelArtProcessingError(
            "Unable to process the image."
        ) from exc


def _crop_to_square(image):

    height, width = image.shape[:2]

    if width == height:
        return image

    size = min(
        width,
        height
    )

    start_x = (
        width - size
    ) // 2

    start_y = (
        height - size
    ) // 2

    return image[
        start_y:start_y + size,
        start_x:start_x + size
    ]


def _quantize_colors(
    image,
    color_count: int
):

    pixels = image.reshape(
        (-1, 3)
    )

    pixels = pixels.astype(
        "float32"
    )

    criteria = (
        cv2.TERM_CRITERIA_EPS
        + cv2.TERM_CRITERIA_MAX_ITER,
        20,
        1.0
    )

    _, labels, centers = cv2.kmeans(
        pixels,
        color_count,
        None,
        criteria,
        5,
        cv2.KMEANS_PP_CENTERS
    )

    centers = centers.astype(
        "uint8"
    )

    quantized = centers[
        labels.flatten()
    ]

    return quantized.reshape(
        image.shape
    )
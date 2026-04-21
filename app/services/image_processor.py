import io
import logging
from typing import Optional

from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

PILLOW_FORMAT_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
}


def process_image(
    image_bytes: bytes,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 85,
    output_format: str = "jpeg",
) -> tuple[bytes, str]:
    """
    Process an image: resize, compress, and/or convert format.

    Returns:
        Tuple of (processed image bytes, mime type string).
    """
    output_format = output_format.lower()
    if output_format not in settings.output_formats:
        raise ValueError(
            f"Unsupported output format '{output_format}'. "
            f"Allowed: {settings.output_formats}"
        )

    pillow_format = PILLOW_FORMAT_MAP[output_format]

    with Image.open(io.BytesIO(image_bytes)) as img:
        # Convert palette/transparency modes for JPEG compatibility
        if pillow_format == "JPEG" and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        original_size = img.size
        logger.info("Opened image: size=%s mode=%s", original_size, img.mode)

        if width or height:
            target_w = width or img.width
            target_h = height or img.height
            img = img.resize((target_w, target_h), Image.LANCZOS)
            logger.info("Resized image: %s → %s", original_size, img.size)

        buffer = io.BytesIO()
        save_kwargs: dict = {"format": pillow_format}

        if pillow_format in ("JPEG", "WEBP"):
            save_kwargs["quality"] = max(1, min(quality, 95))
            save_kwargs["optimize"] = True

        img.save(buffer, **save_kwargs)
        buffer.seek(0)

    mime_type = f"image/{output_format.replace('jpg', 'jpeg')}"
    return buffer.read(), mime_type
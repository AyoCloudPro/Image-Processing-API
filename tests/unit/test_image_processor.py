import io
import pytest
from PIL import Image

from app.services.image_processor import process_image


def make_jpeg(width=800, height=600) -> bytes:
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_resize():
    result, mime = process_image(make_jpeg(), width=400, height=300, output_format="jpeg")
    img = Image.open(io.BytesIO(result))
    assert img.size == (400, 300)
    assert mime == "image/jpeg"


def test_compress():
    original = make_jpeg()
    result, mime = process_image(original, quality=20, output_format="jpeg")
    assert len(result) < len(original)
    assert mime == "image/jpeg"


def test_convert_to_webp():
    result, mime = process_image(make_jpeg(), output_format="webp")
    img = Image.open(io.BytesIO(result))
    assert img.format == "WEBP"
    assert mime == "image/webp"


def test_convert_to_png():
    result, mime = process_image(make_jpeg(), output_format="png")
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"
    assert mime == "image/png"


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported output format"):
        process_image(make_jpeg(), output_format="bmp")


def test_resize_width_only():
    result, _ = process_image(make_jpeg(800, 600), width=200, output_format="jpeg")
    img = Image.open(io.BytesIO(result))
    assert img.size == (200, 600)


def test_resize_height_only():
    result, _ = process_image(make_jpeg(800, 600), height=100, output_format="jpeg")
    img = Image.open(io.BytesIO(result))
    assert img.size == (800, 100)

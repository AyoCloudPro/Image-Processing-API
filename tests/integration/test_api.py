import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from PIL import Image

from app.main import app

client = TestClient(app)


def make_test_image(width=800, height=600) -> io.BytesIO:
    img = Image.new("RGB", (width, height), color=(100, 149, 237))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


MOCK_BLOB_NAME = "processed/test-uuid.jpg"
MOCK_SIGNED_URL = "https://storage.googleapis.com/fake-signed-url"


@pytest.fixture(autouse=True)
def mock_gcs():
    """Mock all GCS calls for every test in this module."""
    with patch("app.routers.images.upload_to_gcs", return_value=MOCK_BLOB_NAME), \
         patch("app.routers.images.generate_signed_url", return_value=MOCK_SIGNED_URL):
        yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_process_image_success():
    response = client.post(
        "/images/process?width=400&height=300&quality=80&output_format=jpeg",
        files={"file": ("test.jpg", make_test_image(), "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["download_url"] == MOCK_SIGNED_URL
    assert data["output_format"] == "jpeg"
    assert data["width"] == 400
    assert data["height"] == 300
    assert data["quality"] == 80


def test_process_image_wrong_content_type():
    response = client.post(
        "/images/process",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 415


def test_process_image_invalid_format():
    response = client.post(
        "/images/process?output_format=bmp",
        files={"file": ("test.jpg", make_test_image(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_process_image_default_params():
    response = client.post(
        "/images/process",
        files={"file": ("test.jpg", make_test_image(), "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["output_format"] == "jpeg"
    assert data["quality"] == 85
    assert data["width"] is None
    assert data["height"] is None


def test_process_image_convert_to_webp():
    response = client.post(
        "/images/process?output_format=webp",
        files={"file": ("test.jpg", make_test_image(), "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.json()["output_format"] == "webp"


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

"""
Locust load test for the Image Processing API.

Usage:
    locust -f load_testing/locustfile.py --host=https://YOUR-CLOUD-RUN-URL

Then open http://localhost:8089 in your browser to start the test
and configure number of users and spawn rate.

For headless mode (e.g. in CI):
    locust -f load_testing/locustfile.py \
        --host=https://YOUR-CLOUD-RUN-URL \
        --headless \
        --users=50 \
        --spawn-rate=5 \
        --run-time=60s \
        --html=load_testing/report.html
"""

import io
import os
import random

from locust import HttpUser, between, task
from PIL import Image


API_KEY = os.getenv("API_KEY", "your-api-key-here")


def generate_test_image(width: int, height: int) -> bytes:
    """Generate an in-memory JPEG image of the given dimensions."""
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    img = Image.new("RGB", (width, height), color=color)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer.read()


class ImageProcessingUser(HttpUser):
    """
    Simulates a typical API user making a mix of image processing requests.
    Each virtual user waits 1-3 seconds between tasks to simulate realistic traffic.
    """
    wait_time = between(1, 3)

    def on_start(self):
        """Called once per user when they start — pre-generate test images."""
        self.small_image = generate_test_image(400, 300)
        self.medium_image = generate_test_image(800, 600)
        self.large_image = generate_test_image(1920, 1080)

    @task(5)
    def resize_small_image(self):
        """Most common task — resize a small image. Weight 5 = runs most often."""
        self.client.post(
            "/images/process?width=200&height=150&output_format=jpeg",
            files={"file": ("small.jpg", io.BytesIO(self.small_image), "image/jpeg")},
            headers={"X-API-Key": API_KEY},
            name="/images/process [resize small]",
        )

    @task(3)
    def resize_medium_image(self):
        """Resize a medium image. Weight 3 = runs frequently."""
        self.client.post(
            "/images/process?width=400&height=300&quality=80&output_format=jpeg",
            files={"file": ("medium.jpg", io.BytesIO(self.medium_image), "image/jpeg")},
            headers={"X-API-Key": API_KEY},
            name="/images/process [resize medium]",
        )

    @task(2)
    def compress_image(self):
        """Compress without resizing. Weight 2 = runs occasionally."""
        self.client.post(
            "/images/process?quality=40&output_format=jpeg",
            files={"file": ("medium.jpg", io.BytesIO(self.medium_image), "image/jpeg")},
            headers={"X-API-Key": API_KEY},
            name="/images/process [compress]",
        )

    @task(2)
    def convert_to_webp(self):
        """Convert to WebP format. Weight 2 = runs occasionally."""
        self.client.post(
            "/images/process?output_format=webp&quality=85",
            files={"file": ("medium.jpg", io.BytesIO(self.medium_image), "image/jpeg")},
            headers={"X-API-Key": API_KEY},
            name="/images/process [convert webp]",
        )

    @task(1)
    def process_large_image(self):
        """Process a large image. Weight 1 = runs least often, most expensive."""
        self.client.post(
            "/images/process?width=1280&height=720&quality=85&output_format=jpeg",
            files={"file": ("large.jpg", io.BytesIO(self.large_image), "image/jpeg")},
            headers={"X-API-Key": API_KEY},
            name="/images/process [large 1080p]",
        )

    @task(3)
    def health_check(self):
        """Health check — lightweight, used to measure baseline latency."""
        self.client.get(
            "/health",
            name="/health",
        )
import logging
import uuid
from datetime import timedelta

from google.cloud import storage

from app.config import settings

logger = logging.getLogger(__name__)

_client: storage.Client | None = None


def get_storage_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client(project=settings.gcp_project_id)
    return _client


def upload_to_gcs(
    image_bytes: bytes,
    mime_type: str,
    bucket_name: str,
    prefix: str = "",
) -> str:
    """Upload image bytes to GCS and return the blob name."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)

    extension = mime_type.split("/")[-1].replace("jpeg", "jpg")
    blob_name = f"{prefix}{uuid.uuid4()}.{extension}"

    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    logger.info("Uploaded %s bytes to gs://%s/%s", len(image_bytes), bucket_name, blob_name)
    return blob_name


def generate_signed_url(bucket_name: str, blob_name: str) -> str:
    """Generate a time-limited signed URL for a GCS object."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        expiration=timedelta(minutes=settings.signed_url_expiry_minutes),
        method="GET",
        version="v4",
    )

    logger.info(
        "Generated signed URL for gs://%s/%s (expires in %d min)",
        bucket_name,
        blob_name,
        settings.signed_url_expiry_minutes,
    )
    return url
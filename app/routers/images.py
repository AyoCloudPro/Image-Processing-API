import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.config import settings
from app.services.image_processor import process_image
from app.services.storage import generate_signed_url, upload_to_gcs

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024


class ProcessResponse(BaseModel):
    message: str
    download_url: str
    original_filename: str
    output_format: str
    width: Optional[int]
    height: Optional[int]
    quality: int


@router.post(
    "/process",
    response_model=ProcessResponse,
    summary="Upload and process an image",
    description=(
        "Upload an image file to be resized, compressed, and/or converted. "
        "Returns a signed GCS URL valid for 60 minutes."
    ),
    status_code=status.HTTP_200_OK,
)
async def process_image_endpoint(
    file: UploadFile = File(..., description="Image file to process (JPEG, PNG, or WebP)"),
    width: Optional[int] = Query(None, gt=0, le=8000, description="Target width in pixels"),
    height: Optional[int] = Query(None, gt=0, le=8000, description="Target height in pixels"),
    quality: int = Query(85, ge=1, le=95, description="Output quality (1–95, JPEG/WebP only)"),
    output_format: str = Query("jpeg", description="Output format: jpeg, png, or webp"),
):
    # Validate file type
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Uploaded file must be an image (JPEG, PNG, or WebP).",
        )

    # Read and validate file size
    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload size of {settings.max_upload_size_mb} MB.",
        )

    logger.info(
        "Processing image: filename=%s size=%d bytes format=%s",
        file.filename,
        len(image_bytes),
        output_format,
    )

    # Upload original to input bucket
    try:
        upload_to_gcs(
            image_bytes=image_bytes,
            mime_type=content_type,
            bucket_name=settings.gcs_input_bucket,
            prefix="originals/",
        )
    except Exception as exc:
        logger.error("Failed to upload original to GCS: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to store original image.",
        )

    # Process image
    try:
        processed_bytes, output_mime = process_image(
            image_bytes=image_bytes,
            width=width,
            height=height,
            quality=quality,
            output_format=output_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        logger.error("Image processing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image processing failed.",
        )

    # Upload processed image to output bucket
    try:
        blob_name = upload_to_gcs(
            image_bytes=processed_bytes,
            mime_type=output_mime,
            bucket_name=settings.gcs_output_bucket,
            prefix="processed/",
        )
        download_url = generate_signed_url(
            bucket_name=settings.gcs_output_bucket,
            blob_name=blob_name,
        )
    except Exception as exc:
        logger.error("Failed to upload processed image to GCS: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to store processed image.",
        )

    return ProcessResponse(
        message="Image processed successfully.",
        download_url=download_url,
        original_filename=file.filename or "unknown",
        output_format=output_format,
        width=width,
        height=height,
        quality=quality,
    )
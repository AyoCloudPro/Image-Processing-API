from fastapi import Header, HTTPException, status


async def verify_content_type(content_type: str = Header(...)):
    """Ensure uploads are image files."""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            details="Content-Type must be an image type (e.g. image/jpeg, image/png).",
        )
    return content_type
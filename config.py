from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_version: str = "1.0.0"
    gcp_project_id: str
    gcs_input_bucket: str
    gcs_output_bucket: str
    max_upload_size_mb: int = 10
    allowed_formats: list[str] = ["jpeg", "jpg", "png", "webp"]
    output_formats: list[str] = ["jpeg", "png", "webp"]
    signed_url_expiry_minutes: int = 60


settings = Settings()

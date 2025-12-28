from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Azure Form Recognizer
    AZURE_FORM_RECOGNIZER_ENDPOINT: str
    AZURE_FORM_RECOGNIZER_KEY: str
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "invoiceflow"
    MINIO_USE_SSL: bool = False
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3100"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # File upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_PAGES: int = 100
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()


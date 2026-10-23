
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Analytics Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "SUPER_SECRET_B2B_SAAS_KEY_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./analytics.db" # Default for local dev
    
    # S3 Config for artifacts
    S3_BUCKET: Optional[str] = "analytics-artifacts"
    S3_ENDPOINT: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

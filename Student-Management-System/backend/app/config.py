import os
from pydantic import BaseModel

class Settings(BaseModel):
    SECRET_KEY: str = "super-secure-secret-key-student-mgmt-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = "sqlite:///./student_management.db"

settings = Settings()


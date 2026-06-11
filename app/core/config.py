from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: str | None = None
    UPLOAD_MAX_SIZE: int = 5_242_880

    # allow unrelated env vars (docker .env may contain extra keys)
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()

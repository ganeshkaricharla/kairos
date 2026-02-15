from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "kairos"
    openrouter_api_key: str = ""
    google_client_id: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    model_config = {"env_file": ".env"}


settings = Settings()

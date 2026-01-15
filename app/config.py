from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")

    celery_broker_url: str = Field(default="redis://redis:6379/0",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(default="redis://redis:6379/0",
        env="CELERY_RESULT_BACKEND"
    )

    api_url: str = Field(
        default="https://jsonplaceholder.typicode.com/users",
        env="API_URL"
    )

    csv_output_path: str = Field(default="/app/data/users.csv",
        env="CSV_OUTPUT_PATH"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False



settings = Settings()
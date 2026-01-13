from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    pinecone_api_key: str
    pinecone_environment: str

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "RAG-CTE-System"

    # App
    app_name: str = "RAG-MLOps"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # Cache
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mysql_url: str
    minio_endpoint: str
    minio_public_endpoint: str = ""   # URL acessível pelo browser; defaults to minio_endpoint
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "alter-egos"
    jwt_secret: str
    jwt_expire_minutes: int = 60
    hf_api_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def public_endpoint(self) -> str:
        return self.minio_public_endpoint or self.minio_endpoint


settings = Settings()

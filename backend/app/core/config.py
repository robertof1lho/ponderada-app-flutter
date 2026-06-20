from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    hf_api_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

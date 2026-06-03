from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Odoo API Gateway"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    # Database (optional) - default to sqlite file
    database_url: str = "sqlite:///./app/app.db"

    # JWT / Auth
    jwt_secret_key: str = Field(default="change-me-in-production", description="Secret key for JWT")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(default=60 * 24, description="Access token expiry in minutes")

    odoo_url: str = Field(..., description="Base URL of the Odoo instance")
    odoo_db: str = Field(..., description="Odoo database name")
    odoo_username: str = Field(..., description="Odoo username")
    odoo_password: str = Field(..., description="Odoo password")
    odoo_rpc_timeout: int = Field(default=30, ge=1, description="XML-RPC timeout in seconds")

    # The env file is placed inside the `app` folder in this project layout.
    model_config = SettingsConfigDict(env_file="app/.env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

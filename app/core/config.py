from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    app_name: str = Field(default="FastAPI E-commerce", alias="APP_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Odoo config
    odoo_url: str = Field(..., alias="ODOO_URL")
    odoo_db: str = Field(..., alias="ODOO_DB")
    odoo_username: str = Field(..., alias="ODOO_USERNAME")
    odoo_password: str = Field(..., alias="ODOO_PASSWORD")
    odoo_rpc_timeout: int = Field(default=30, alias="ODOO_RPC_TIMEOUT")

    # PostgreSQL config
    database_url: str = Field(..., alias="DATABASE_URL")

    # Redis config
    redis_url: str = Field(..., alias="REDIS_URL")

    # Security & Supabase config
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_jwt_secret: str = Field(..., alias="SUPABASE_JWT_SECRET")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

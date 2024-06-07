from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DISCORD_TOKEN: str
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Config()

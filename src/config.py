"""Configuration for the Task MCP Server"""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

class Settings(BaseSettings):
    """Settings for the Task MCP Server"""

    #Google Cloud Config
    google_client_config: str = Field(
        "credentials/client_secrets.json",
        description="The path to store OAuth credentials",
    )

    google_token_file: str = Field(
        ".gcp-saved-tokens.json",
        description="The path to store OAuth credentials",
    )

    google_oauth_port: int = Field(
        8765,
        description="The port to use for OAuth"
    )

    # Google Task API scopes
    google_task_api_scopes: list[str] = Field(
        ["https://www.googleapis.com/auth/tasks"],
        description="The scopes to use for the Google Task API"
    )

    # Logging Config
    logging_level: str = Field(
        "INFO",
        description="The logging level to use for the server"
    )

    class Config:
        """Config for the Settings"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_ignore_empty = True

    def get_client_config_path(self) -> str:
        """Get the client config path"""
        return Path(self.google_client_config)

    def get_token_file_path(self) -> str:
        """Get the token file path"""
        return Path(self.google_token_file)

def get_settings() -> Settings:
    """Get application settings"""
    try:
        return Settings()
    except Exception as e:
        raise ValueError(
            f"Configuration error: {e}. "
            f"Please ensure Google OAuth client config and token paths are valid. "
            f"Current working directory: {os.getcwd()}. "
            f"GOOGLE_CLIENT_CONFIG: {os.getenv('GOOGLE_CLIENT_CONFIG')}, "
            f"GOOGLE_TOKEN_FILE: {os.getenv('GOOGLE_TOKEN_FILE')}"
        ) from e
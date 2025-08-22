"""
Configuration management for Life Cockpit automation.

Loads environment variables and provides type-safe access to configuration settings.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Microsoft Graph API Configuration
    azure_client_id: str = Field(..., env="AZURE_CLIENT_ID")
    azure_client_secret: str = Field(..., env="AZURE_CLIENT_SECRET")
    azure_tenant_id: str = Field(..., env="AZURE_TENANT_ID")
    graph_scopes: str = Field(
        default="https://graph.microsoft.com/.default",
        env="GRAPH_SCOPES"
    )
    
    # Dataverse Configuration
    dataverse_url: str = Field(..., env="DATAVERSE_URL")
    dataverse_client_id: Optional[str] = Field(None, env="DATAVERSE_CLIENT_ID")
    dataverse_client_secret: Optional[str] = Field(None, env="DATAVERSE_CLIENT_SECRET")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    
    # Application Configuration
    app_name: str = Field(default="life-cockpit", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    
    # Optional: Azure Logic Apps
    logic_apps_workflow_url: Optional[str] = Field(None, env="LOGIC_APPS_WORKFLOW_URL")
    logic_apps_callback_url: Optional[str] = Field(None, env="LOGIC_APPS_CALLBACK_URL")
    
    # Optional: OpenAI/Azure OpenAI
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: Optional[str] = Field(None, env="AZURE_OPENAI_API_KEY")
    azure_openai_deployment_name: Optional[str] = Field(None, env="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Development Settings
    debug: bool = Field(default=False, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> Settings:
    """
    Load configuration from environment variables and .env file.
    
    Returns:
        Configured settings instance
    
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load .env file if it exists
    env_file = Path(".env")
    if not os.getenv("BLC_SKIP_DOTENV"):
        if env_file.exists():
            load_dotenv(env_file)
    
    # Normalize env variable names: prefer AAD_*, support AZURE_* during transition
    # If AAD_* provided but AZURE_* missing, set AZURE_* from AAD_* so existing code keeps working
    aad_to_azure = {
        "AAD_CLIENT_ID": "AZURE_CLIENT_ID",
        "AAD_CLIENT_SECRET": "AZURE_CLIENT_SECRET",
        "AAD_TENANT_ID": "AZURE_TENANT_ID",
    }
    for aad_key, azure_key in aad_to_azure.items():
        aad_val = os.getenv(aad_key)
        azure_val = os.getenv(azure_key)
        if aad_val and not azure_val:
            os.environ[azure_key] = aad_val
    
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")


def validate_config(settings: Settings) -> bool:
    """
    Validate that all required configuration is present.
    
    Args:
        settings: Settings instance to validate
    
    Returns:
        True if configuration is valid
    
    Raises:
        ValueError: If configuration is invalid
    """
    errors = []
    
    # Check required Microsoft Graph settings
    if not settings.azure_client_id:
        errors.append("AZURE_CLIENT_ID is required")
    if not settings.azure_client_secret:
        errors.append("AZURE_CLIENT_SECRET is required")
    if not settings.azure_tenant_id:
        errors.append("AZURE_TENANT_ID is required")
    
    # Check required Dataverse settings
    if not settings.dataverse_url:
        errors.append("DATAVERSE_URL is required")
    
    # Validate URLs
    if settings.dataverse_url and not settings.dataverse_url.startswith(("http://", "https://")):
        errors.append("DATAVERSE_URL must be a valid URL")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True


def get_config() -> Settings:
    """
    Get validated configuration instance.
    
    Returns:
        Validated settings instance
    
    Raises:
        ValueError: If configuration is invalid or missing
    """
    settings = load_config()
    validate_config(settings)
    return settings


# Convenience functions for common config access
def get_azure_config():
    """Get Azure configuration as a dictionary."""
    config = get_config()
    return {
        "client_id": config.azure_client_id,
        "client_secret": config.azure_client_secret,
        "tenant_id": config.azure_tenant_id,
        "scopes": config.graph_scopes.split(",") if config.graph_scopes else []
    }


def get_dataverse_config():
    """Get Dataverse configuration as a dictionary."""
    config = get_config()
    return {
        "url": config.dataverse_url,
        "client_id": config.dataverse_client_id,
        "client_secret": config.dataverse_client_secret,
    }


def get_logging_config():
    """Get logging configuration as a dictionary."""
    config = get_config()
    return {
        "level": config.log_level,
        "file": config.log_file,
    }


# Global config instance
_config: Optional[Settings] = None


def config() -> Settings:
    """
    Get the global configuration instance (singleton pattern).
    
    Returns:
        Global settings instance
    """
    global _config
    if _config is None:
        _config = get_config()
    return _config

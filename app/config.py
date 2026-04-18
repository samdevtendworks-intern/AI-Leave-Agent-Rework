"""
Configuration Management
Handles environment variables and application settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # API Configuration
    app_name: str = "Leave Review Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Gemini AI Configuration
    gemini_api_key: Optional[str] = None
    
    # Business Rules
    min_team_capacity_percentage: float = 80.0
    burnout_threshold_months: int = 6
    unplanned_leave_threshold_hours: int = 24
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


# Global settings instance
settings = Settings()

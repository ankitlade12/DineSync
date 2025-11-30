"""Configuration Management for YelpReviewGym

Handles application settings and environment variables.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_env: str = "dev"
    yelp_api_key: str

    def __init__(self, **kwargs):
        """Initialize settings, checking Streamlit secrets first."""
        # Check if running in Streamlit and secrets are available
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'YELP_API_KEY' in st.secrets:
                # Use Streamlit secrets
                kwargs.setdefault('yelp_api_key', st.secrets['YELP_API_KEY'])
                if 'YELP_CLIENT_ID' in st.secrets:
                    os.environ['YELP_CLIENT_ID'] = st.secrets['YELP_CLIENT_ID']
        except (ImportError, FileNotFoundError, KeyError):
            # Not in Streamlit or secrets not configured, fall back to env
            pass
        
        super().__init__(**kwargs)

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

"""Configuration management for PA-Square bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_COMMAND_PREFIX: str = os.getenv("DISCORD_COMMAND_PREFIX", "!")
    DEFAULT_ROLE: str = os.getenv("DEFAULT_ROLE", "PAPA Follower")
    
    # Habitica Configuration
    HABITICA_BASE_URL: str = os.getenv("HABITICA_BASE_URL", "")
    HABITICA_USER: str = os.getenv("HABITICA_USER", "")
    HABITICA_PW: str = os.getenv("HABITICA_PW", "")
    APPLICATION_NAME: str = os.getenv("APPLICATION_NAME", "")
    
    # Logging Configuration
    LOG_FILE: str = os.getenv("LOG_FILE", "discord.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    
    # Flask Keep-Alive Configuration
    KEEP_ALIVE_HOST: str = os.getenv("KEEP_ALIVE_HOST", "0.0.0.0")
    KEEP_ALIVE_PORT: int = int(os.getenv("KEEP_ALIVE_PORT", "8080"))
    
    # API Rate Limiting
    HABITICA_API_DELAY: int = int(os.getenv("HABITICA_API_DELAY", "30"))  # seconds
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration variables are set."""
        required_vars = [
            ("DISCORD_TOKEN", cls.DISCORD_TOKEN),
            ("HABITICA_BASE_URL", cls.HABITICA_BASE_URL),
            ("HABITICA_USER", cls.HABITICA_USER),
            ("HABITICA_PW", cls.HABITICA_PW),
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Create a singleton instance
config = Config()

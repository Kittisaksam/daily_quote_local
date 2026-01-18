"""Configuration management for Daily Quote Bot."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

@dataclass
class Config:
    """Application configuration."""

    # Telegram Configuration
    telegram_bot_token: str
    telegram_chat_id: str

    # Anthropic Claude API
    anthropic_api_key: str

    # Schedule Configuration
    schedule_window: str  # morning, evening, or both
    morning_start: str = "07:00"
    morning_end: str = "09:00"
    evening_start: str = "18:00"
    evening_end: str = "20:00"

    # Quote Language
    quote_language: str = "both"  # en, th, or both

    # Data Paths
    quotes_file: Path = BASE_DIR / "data" / "quotes.json"
    stats_file: Path = BASE_DIR / "data" / "stats.json"

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate Telegram token
        if not self.telegram_bot_token or self.telegram_bot_token == "your_bot_token_here":
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

        # Validate Chat ID
        if not self.telegram_chat_id or self.telegram_chat_id == "your_chat_id_here":
            raise ValueError("TELEGRAM_CHAT_ID is not configured")

        # Validate Anthropic API key
        if not self.anthropic_api_key or self.anthropic_api_key == "your_anthropic_key_here":
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        # Validate schedule window
        valid_windows = ["morning", "evening", "both"]
        if self.schedule_window not in valid_windows:
            raise ValueError(f"SCHEDULE_WINDOW must be one of {valid_windows}")

        # Validate quote language
        valid_languages = ["en", "th", "both"]
        if self.quote_language not in valid_languages:
            raise ValueError(f"QUOTE_LANGUAGE must be one of {valid_languages}")

        # Ensure data directory exists
        self.quotes_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        schedule_window=os.getenv("SCHEDULE_WINDOW", "both"),
        morning_start=os.getenv("MORNING_START", "07:00"),
        morning_end=os.getenv("MORNING_END", "09:00"),
        evening_start=os.getenv("EVENING_START", "18:00"),
        evening_end=os.getenv("EVENING_END", "20:00"),
        quote_language=os.getenv("QUOTE_LANGUAGE", "both"),
    )


# Global config instance
try:
    config = load_config()
except ValueError:
    # Config not fully set up yet, will be validated when needed
    config = None

"""Configuration management for Daily Quote Bot."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (parent of config folder)
BASE_DIR = Path(__file__).parent.parent

# Valid configuration values
VALID_SCHEDULE_WINDOWS = ("morning", "evening", "both", "daily", "random")
VALID_LANGUAGES = ("en", "th", "both")

# Default time windows
DEFAULT_MORNING_START = "07:00"
DEFAULT_MORNING_END = "09:00"
DEFAULT_EVENING_START = "18:00"
DEFAULT_EVENING_END = "20:00"


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
    morning_start: str = DEFAULT_MORNING_START
    morning_end: str = DEFAULT_MORNING_END
    evening_start: str = DEFAULT_EVENING_START
    evening_end: str = DEFAULT_EVENING_END

    # Quote Language
    quote_language: str = "both"  # en, th, or both

    # Data Paths
    quotes_file: Path = BASE_DIR / "data" / "quotes.json"
    stats_file: Path = BASE_DIR / "data" / "stats.json"

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_required_fields()
        self._validate_schedule_window()
        self._validate_quote_language()
        self._ensure_data_directories()

    def _validate_required_fields(self):
        """Validate that required fields are set."""
        errors = []

        if not self.telegram_bot_token or self.telegram_bot_token == "your_bot_token_here":
            errors.append("TELEGRAM_BOT_TOKEN is not configured")

        if not self.telegram_chat_id or self.telegram_chat_id == "your_chat_id_here":
            errors.append("TELEGRAM_CHAT_ID is not configured")

        if not self.anthropic_api_key or self.anthropic_api_key == "your_anthropic_key_here":
            errors.append("ANTHROPIC_API_KEY is not configured")

        if errors:
            raise ValueError("; ".join(errors))

    def _validate_schedule_window(self):
        """Validate schedule window is a valid value."""
        if self.schedule_window not in VALID_SCHEDULE_WINDOWS:
            raise ValueError(
                f"SCHEDULE_WINDOW must be one of {VALID_SCHEDULE_WINDOWS}, "
                f"got '{self.schedule_window}'"
            )

    def _validate_quote_language(self):
        """Validate quote language is a valid value."""
        if self.quote_language not in VALID_LANGUAGES:
            raise ValueError(
                f"QUOTE_LANGUAGE must be one of {VALID_LANGUAGES}, "
                f"got '{self.quote_language}'"
            )

    def _ensure_data_directories(self):
        """Ensure data directories exist."""
        self.quotes_file.parent.mkdir(parents=True, exist_ok=True)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from environment variables.

    Returns:
        Config object with values from environment variables
    """
    return Config(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        schedule_window=os.getenv("SCHEDULE_WINDOW", "both"),
        morning_start=os.getenv("MORNING_START", DEFAULT_MORNING_START),
        morning_end=os.getenv("MORNING_END", DEFAULT_MORNING_END),
        evening_start=os.getenv("EVENING_START", DEFAULT_EVENING_START),
        evening_end=os.getenv("EVENING_END", DEFAULT_EVENING_END),
        quote_language=os.getenv("QUOTE_LANGUAGE", "both"),
    )


# Global config instance
config: Optional[Config] = None

try:
    config = load_config()
except ValueError:
    # Config not fully set up yet, will be validated when needed
    config = None

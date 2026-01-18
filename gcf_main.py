"""Google Cloud Functions Entry Point

This module provides the entry point for Google Cloud Functions deployment.
The actual implementation is in scripts/gcf_main.py.

Usage (deployed):
    https://<region>-<project>.cloudfunctions.net/daily-quote-bot?period=both

For local testing:
    functions-framework --target=send_daily_quote --source=gcf_main.py
"""

from scripts.gcf_main import (
    send_daily_quote,
    send_morning_quote,
    send_evening_quote,
    health_check,
)

__all__ = [
    "send_daily_quote",
    "send_morning_quote",
    "send_evening_quote",
    "health_check",
]

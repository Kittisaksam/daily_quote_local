"""Daily Quote Bot - Local Entry Point

This is the main entry point for running the bot locally with scheduler.
For Google Cloud Functions, see gcf_main.py.

Usage:
    python main.py
"""

from scripts.main import main

if __name__ == "__main__":
    main()

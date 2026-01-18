"""Telegram bot module for sending quotes and handling commands."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config.settings import config
from bot.quote_generator import get_quote

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class StatsManager:
    """Manage quote statistics."""

    def __init__(self, stats_file: Optional[Path] = None):
        """Initialize stats manager.

        Args:
            stats_file: Path to stats JSON file
        """
        self.stats_file = stats_file or config.stats_file

    def load_stats(self) -> dict:
        """Load statistics from file.

        Returns:
            Dictionary with statistics
        """
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'total_quotes_sent': 0,
                'local_quotes_sent': 0,
                'ai_quotes_sent': 0,
                'morning_quotes_sent': 0,
                'evening_quotes_sent': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'last_sent': None,
                'history': []
            }

    def save_stats(self, stats: dict):
        """Save statistics to file.

        Args:
            stats: Statistics dictionary
        """
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    def record_quote(self, quote: dict, time_period: str = "unknown"):
        """Record a sent quote.

        Args:
            quote: Quote dictionary
            time_period: 'morning', 'evening', or 'unknown'
        """
        stats = self.load_stats()

        # Update counters
        stats['total_quotes_sent'] += 1

        if quote.get('source') == 'ai':
            stats['ai_quotes_sent'] += 1
        else:
            stats['local_quotes_sent'] += 1

        if time_period == 'morning':
            stats['morning_quotes_sent'] += 1
        elif time_period == 'evening':
            stats['evening_quotes_sent'] += 1

        # Update streak
        now = datetime.now()
        today = now.date().isoformat()

        if stats['last_sent']:
            last_sent = datetime.fromisoformat(stats['last_sent']).date()
            if (now.date() - last_sent).days == 1:
                # Consecutive day
                stats['current_streak'] += 1
            elif (now.date() - last_sent).days > 1:
                # Streak broken
                stats['current_streak'] = 1
        else:
            stats['current_streak'] = 1

        # Update longest streak
        if stats['current_streak'] > stats['longest_streak']:
            stats['longest_streak'] = stats['current_streak']

        # Update last sent
        stats['last_sent'] = now.isoformat()

        # Add to history (keep last 100)
        history_entry = {
            'timestamp': now.isoformat(),
            'text': quote.get('text', '')[:100],  # Truncate long quotes
            'author': quote.get('author', 'Unknown'),
            'language': quote.get('language', 'en'),
            'source': quote.get('source', 'local'),
            'time_period': time_period
        }
        stats['history'].append(history_entry)

        # Keep only last 100 entries
        if len(stats['history']) > 100:
            stats['history'] = stats['history'][-100:]

        self.save_stats(stats)


# Global stats manager
stats_manager = StatsManager()


async def send_quote_to_chat(quote: dict, time_period: str = "unknown") -> bool:
    """Send a quote to the configured Telegram chat.

    Args:
        quote: Quote dictionary with 'text' and 'author'
        time_period: 'morning', 'evening', or 'unknown'

    Returns:
        True if successful, False otherwise
    """
    try:
        application = Application.builder().token(config.telegram_bot_token).build()

        # Format message
        text = f"🌟 *{quote['text']}*\n\n— {quote['author']}"

        # Send message
        await application.bot.send_message(
            chat_id=config.telegram_chat_id,
            text=text,
            parse_mode='Markdown'
        )

        # Record in stats
        stats_manager.record_quote(quote, time_period)

        logger.info(f"Quote sent successfully: {quote['text'][:50]}...")
        return True

    except Exception as e:
        logger.error(f"Error sending quote: {e}")
        return False


def send_quote_sync(quote: dict, time_period: str = "unknown") -> bool:
    """Synchronous wrapper for send_quote_to_chat.

    Args:
        quote: Quote dictionary
        time_period: 'morning', 'evening', or 'unknown'

    Returns:
        True if successful, False otherwise
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(send_quote_to_chat(quote, time_period))


# Telegram Bot Command Handlers

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_message = (
        "👋 Welcome to the Daily Quote Bot!\n\n"
        "I'll send you inspirational quotes every day.\n\n"
        "Available commands:\n"
        "/quote - Get a random quote now\n"
        "/stats - View your quote statistics\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(welcome_message)


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quote command."""
    quote = get_quote()
    text = f"🌟 *{quote['text']}*\n\n— {quote['author']}"
    await update.message.reply_text(text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    stats = stats_manager.load_stats()

    stats_text = (
        f"📊 *Quote Statistics*\n\n"
        f"📝 Total Quotes: {stats['total_quotes_sent']}\n"
        f"💾 Local Quotes: {stats['local_quotes_sent']}\n"
        f"🤖 AI Quotes: {stats['ai_quotes_sent']}\n"
        f"🌅 Morning Quotes: {stats['morning_quotes_sent']}\n"
        f"🌆 Evening Quotes: {stats['evening_quotes_sent']}\n"
        f"🔥 Current Streak: {stats['current_streak']} days\n"
        f"🏆 Longest Streak: {stats['longest_streak']} days\n"
    )

    if stats['last_sent']:
        last_sent = datetime.fromisoformat(stats['last_sent'])
        stats_text += f"\n🕐 Last Sent: {last_sent.strftime('%Y-%m-%d %H:%M')}"

    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "🤖 *Daily Quote Bot Help*\n\n"
        "Available commands:\n"
        "/start - Welcome message\n"
        "/quote - Get a random quote now\n"
        "/stats - View your quote statistics\n"
        "/help - Show this help message\n\n"
        "The bot will automatically send you quotes "
        "based on your configured schedule."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


def run_bot():
    """Run the Telegram bot (blocking)."""
    application = Application.builder().token(config.telegram_bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    run_bot()

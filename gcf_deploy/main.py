"""Google Cloud Functions entry point for Daily Quote Bot.

This module handles HTTP requests from Google Cloud Scheduler to send quotes.
Simplified version that doesn't use database/scheduler (stateless).
"""
import os
import logging
import random
from datetime import datetime
from flask import jsonify, request

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our bot modules
from bot.quote_generator import get_quote
from bot.telegram_bot import send_quote_sync
from config.settings import load_config


def should_send_random_quote(hour: int) -> bool:
    """Determine if we should send a quote at this hour (for random scheduling).

    Uses the date as a seed so we get the same result for all hours on the same day.
    Only ONE hour per day will return True.

    Args:
        hour: Hour of day (0-23)

    Returns:
        True if this is the selected hour for today, False otherwise
    """
    today = datetime.now().date()
    # Use date as seed to get consistent random number across all hours today
    random.seed(today.isoformat())
    # Randomly select one hour from 10-17 (8 hours)
    selected_hour = random.randint(10, 17)
    logger.info(f"Random quote scheduled for today at {selected_hour}:00, current hour: {hour}")
    return hour == selected_hour


def send_daily_quote(request):
    """Cloud Function entry point.

    This function is triggered by Google Cloud Scheduler via HTTP request.
    It's stateless - doesn't use database or scheduler.

    Args:
        request: Flask request object from Cloud Scheduler

    Returns:
        JSON response with status
    """
    logger.info("=" * 50)
    logger.info("Cloud Function triggered: send_daily_quote")
    logger.info("=" * 50)

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded: {config.schedule_window}")

        # Get time period from URL parameter
        time_period = request.args.get('period', 'both')

        # Get current hour for random scheduling
        current_hour = request.args.get('hour', datetime.now().hour, type=int)

        results = []

        # Send morning quote
        if time_period in ['morning', 'both']:
            if config.schedule_window in ['morning', 'both']:
                logger.info("Sending morning quote...")
                try:
                    # Get quote
                    quote = get_quote(language=config.quote_language)

                    # Send to Telegram
                    success = send_quote_sync(quote, time_period='morning')

                    if success:
                        logger.info("Morning quote sent successfully")
                        results.append({'period': 'morning', 'status': 'success'})
                    else:
                        logger.error("Failed to send morning quote")
                        results.append({'period': 'morning', 'status': 'failed', 'error': 'Send failed'})

                except Exception as e:
                    logger.error(f"Error sending morning quote: {e}")
                    results.append({'period': 'morning', 'status': 'failed', 'error': str(e)})

        # Send evening quote
        if time_period in ['evening', 'both']:
            if config.schedule_window in ['evening', 'both']:
                logger.info("Sending evening quote...")
                try:
                    # Get quote
                    quote = get_quote(language=config.quote_language)

                    # Send to Telegram
                    success = send_quote_sync(quote, time_period='evening')

                    if success:
                        logger.info("Evening quote sent successfully")
                        results.append({'period': 'evening', 'status': 'success'})
                    else:
                        logger.error("Failed to send evening quote")
                        results.append({'period': 'evening', 'status': 'failed', 'error': 'Send failed'})

                except Exception as e:
                    logger.error(f"Error sending evening quote: {e}")
                    results.append({'period': 'evening', 'status': 'failed', 'error': str(e)})

        # Send random quote (10:00-17:00)
        if time_period == 'random':
            logger.info(f"Checking random quote schedule for hour {current_hour}...")
            if should_send_random_quote(current_hour):
                logger.info("Sending random daily quote...")
                try:
                    # Get quote
                    quote = get_quote(language=config.quote_language)

                    # Send to Telegram
                    success = send_quote_sync(quote, time_period='random')

                    if success:
                        logger.info("Random quote sent successfully")
                        results.append({'period': 'random', 'hour': current_hour, 'status': 'success'})
                    else:
                        logger.error("Failed to send random quote")
                        results.append({'period': 'random', 'hour': current_hour, 'status': 'failed', 'error': 'Send failed'})

                except Exception as e:
                    logger.error(f"Error sending random quote: {e}")
                    results.append({'period': 'random', 'hour': current_hour, 'status': 'failed', 'error': str(e)})
            else:
                logger.info(f"Not the randomly selected hour for today, skipping...")
                results.append({'period': 'random', 'hour': current_hour, 'status': 'skipped', 'message': 'Not selected hour'})

        logger.info(f"Cloud Function completed: {results}")

        # Check if any failed
        failed_count = sum(1 for r in results if r['status'] == 'failed')

        return jsonify({
            'status': 'success' if failed_count == 0 else 'partial_success',
            'message': f'Sent {len(results) - failed_count}/{len(results)} quotes',
            'results': results
        }), 200 if failed_count == 0 else 207  # 207 = Multi-Status

    except Exception as e:
        logger.error(f"Error in Cloud Function: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Alias for Google Cloud Functions
def send_morning_quote(request):
    """Send morning quote only.

    Args:
        request: Flask request object

    Returns:
        JSON response
    """
    # Modify request args to include period=morning
    request.args = request.args.copy()
    request.args['period'] = 'morning'
    return send_daily_quote(request)


def send_evening_quote(request):
    """Send evening quote only.

    Args:
        request: Flask request object

    Returns:
        JSON response
    """
    # Modify request args to include period=evening
    request.args = request.args.copy()
    request.args['period'] = 'evening'
    return send_daily_quote(request)


# Health check endpoint
def health_check(request):
    """Health check endpoint.

    Args:
        request: Flask request object

    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Daily Quote Bot',
        'message': 'Cloud Function is running'
    }), 200

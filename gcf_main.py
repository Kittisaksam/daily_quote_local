"""Google Cloud Functions entry point for Daily Quote Bot.

This module handles HTTP requests from Google Cloud Scheduler to send quotes.
"""
import os
import logging
from flask import jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our bot modules
from bot.scheduler import get_scheduler
from config.settings import load_config


def send_daily_quote(request):
    """Cloud Function entry point.

    This function is triggered by Google Cloud Scheduler via HTTP request.

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

        # Create scheduler instance
        scheduler = get_scheduler()

        # Determine which quotes to send based on time period
        time_period = request.args.get('period', 'both')

        results = []

        # Send morning quote
        if time_period in ['morning', 'both']:
            if config.schedule_window in ['morning', 'both']:
                logger.info("Sending morning quote...")
                try:
                    scheduler.send_daily_quote('morning')
                    results.append({'period': 'morning', 'status': 'success'})
                except Exception as e:
                    logger.error(f"Failed to send morning quote: {e}")
                    results.append({'period': 'morning', 'status': 'failed', 'error': str(e)})

        # Send evening quote
        if time_period in ['evening', 'both']:
            if config.schedule_window in ['evening', 'both']:
                logger.info("Sending evening quote...")
                try:
                    scheduler.send_daily_quote('evening')
                    results.append({'period': 'evening', 'status': 'success'})
                except Exception as e:
                    logger.error(f"Failed to send evening quote: {e}")
                    results.append({'period': 'evening', 'status': 'failed', 'error': str(e)})

        logger.info(f"Cloud Function completed: {results}")

        return jsonify({
            'status': 'success',
            'message': 'Quotes sent successfully',
            'results': results
        }), 200

    except Exception as e:
        logger.error(f"Error in Cloud Function: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def send_morning_quote(request):
    """Send morning quote only.

    Args:
        request: Flask request object

    Returns:
        JSON response
    """
    return send_daily_quote(request)  # Will use period=morning from URL param


def send_evening_quote(request):
    """Send evening quote only.

    Args:
        request: Flask request object

    Returns:
        JSON response
    """
    return send_daily_quote(request)  # Will use period=evening from URL param


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

# Daily Quote Telegram Bot 🌟

A Python-based Telegram bot that sends AI-generated inspirational quotes daily, with optional Streamlit dashboard for viewing statistics and managing the bot.

## Features

- 🤖 **AI-Generated Quotes**: Uses GLM API (Zhipu AI) to generate unique inspirational quotes
- 💾 **Local Quote Cache**: Stores quotes locally for faster access
- 📅 **Flexible Scheduling**: Morning (7-9 AM) and/or Evening (6-8 PM) delivery
- 📊 **Statistics Dashboard**: Track your quotes, streaks, and progress
- 🌏 **Multi-Language**: Support for English and Thai quotes
- 💬 **Telegram Commands**: Interactive bot commands for on-demand quotes

## Project Structure

```
daily_quote/
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py      # Telegram bot logic
│   ├── quote_generator.py   # GLM API integration
│   └── scheduler.py         # Task scheduling (APScheduler)
├── data/
│   ├── quotes.json          # Local quotes cache
│   └── stats.json           # Quote statistics
├── dashboard/
│   ├── __init__.py
│   └── app.py               # Streamlit dashboard
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── main.py                  # Entry point for bot
├── run_dashboard.py         # Entry point for dashboard
├── requirements.txt
└── .env                     # API keys and tokens
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Telegram account
- GLM API key (Zhipu AI) - Get from https://open.bigmodel.cn/

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Get Your Chat ID

1. Start a conversation with your bot
2. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in your browser
3. Find your chat ID in the response (looks like `123456789`)

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   TELEGRAM_CHAT_ID=your_actual_chat_id_here
   GLM_API_KEY=your_actual_glm_api_key_here

   # Optional: Customize schedule
   SCHEDULE_WINDOW=both  # Options: morning, evening, both
   MORNING_START=07:00
   MORNING_END=09:00
   EVENING_START=18:00
   EVENING_END=20:00
   QUOTE_LANGUAGE=both  # Options: en, th, both
   ```

### 6. Run the Bot

**Start the Telegram bot with scheduler:**
```bash
python main.py
```

**Run the dashboard (optional):**
```bash
python run_dashboard.py
```
or
```bash
streamlit run dashboard/app.py
```

## Usage

### Telegram Commands

Once the bot is running, you can use these commands in Telegram:

- `/start` - Welcome message
- `/quote` - Get a random quote immediately
- `/stats` - View your quote statistics
- `/help` - Show help message

### Dashboard Features

The Streamlit dashboard provides:

- 📊 **Statistics Overview**: Total quotes, streaks, source distribution
- 📈 **Timeline View**: Quotes sent over time
- 💬 **Quote History**: Browse all sent quotes with filters
- 📚 **Local Quotes**: View your cached quotes
- 📤 **Manual Send**: Send a quote immediately
- 🤖 **AI Generate**: Test quote generation

## Configuration Options

### Schedule Windows

- `morning`: Send quotes between 7:00-9:00 AM
- `evening`: Send quotes between 6:00-8:00 PM
- `both`: Send twice daily (morning AND evening)

### Quote Sources

The bot uses a mix of:
- **Local quotes** (from `data/quotes.json`)
- **AI-generated quotes** (via GLM API / Zhipu AI)

By default, there's a 30% chance of AI-generated quotes, but this is randomized.

### Languages

- `en`: English only
- `th`: Thai only
- `both`: Randomly mix English and Thai

## Testing

**Test quote generation:**
```bash
python -c "from bot.quote_generator import get_quote; print(get_quote())"
```

**Test Telegram connection:**
```bash
python -c "from bot.telegram_bot import send_quote_sync; send_quote_sync({'text': 'Test message', 'author': 'Test'})"
```

## Cloud Deployment 🚀

### Run 24/7 without keeping your computer on!

#### Google Cloud Functions (Recommended - Free Tier)

**Free Tier:** 2 million invocations/month + 3 scheduler jobs/month

**Benefits:**
- ✅ Runs 24/7 on Google's infrastructure
- ✅ Auto-scales
- ✅ Pay only for what you use (likely FREE)

**Quick Start:**
1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
2. Create project at: https://console.cloud.google.com
3. Follow deployment guide: [GOOGLE_CLOUD_DEPLOY.md](GOOGLE_CLOUD_DEPLOY.md)
4. Run: `./deploy_gcf.sh`

**Deploy with one command:**
```bash
./deploy_gcf.sh
```

#### PythonAnywhere (Alternative - Free Tier)

Limited free tier, good for learning.

See: [PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)

---

## Troubleshooting

### Bot not sending messages

1. Check that your bot token is correct
2. Verify your chat ID
3. Check the logs in `daily_quote.log`
4. Make sure the bot process is running

### Scheduler not working

1. Check that `data/scheduler.sqlite` exists
2. Verify your time window settings in `.env`
3. Check logs for scheduler errors

### GLM API errors

1. Verify your API key is valid from https://open.bigmodel.cn/
2. Check your API quota/usage limits
3. The bot will fall back to local quotes if API fails

## Data Files

- `data/quotes.json`: Local quote cache (can add your own quotes here)
- `data/stats.json`: Statistics and history
- `data/scheduler.sqlite`: Persistent scheduler data
- `daily_quote.log`: Application logs

## License

MIT License - feel free to use and modify!

## Support

For issues or questions, please check the logs first, then review the configuration.

# Daily Quote Telegram Bot 🌟

A Python-based Telegram bot that sends AI-generated inspirational quotes daily, with support for multiple deployment platforms including Google Cloud Functions and PythonAnywhere.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white)](https://t.me/)

## ✨ Features

- 🤖 **AI-Generated Quotes**: Uses Anthropic Claude API to generate unique inspirational quotes
- 💾 **Local Quote Cache**: Stores quotes locally for faster access
- 📅 **Flexible Scheduling**:
  - Morning (7-9 AM)
  - Evening (6-8 PM)
  - Random daily scheduling (10 AM - 5 PM)
- 📊 **Statistics Dashboard**: Track quotes, streaks, and progress
- 🌏 **Multi-Language**: Support for English and Thai quotes
- 💬 **Telegram Commands**: Interactive bot commands for on-demand quotes
- ☁️ **Cloud Deployments**:
  - Google Cloud Functions (Free Tier)
  - PythonAnywhere

## 📁 Project Structure

```
daily_quote/
├── bot/                          # Bot core logic
│   ├── __init__.py
│   ├── telegram_bot.py          # Telegram bot integration
│   ├── quote_generator.py       # AI quote generation
│   └── scheduler.py             # Local task scheduling
├── config/                       # Configuration management
│   ├── __init__.py
│   └── settings.py
├── data/                         # Data files
│   ├── quotes.json              # Local quotes cache
│   └── stats.json               # Statistics tracking
├── dashboard/                    # Streamlit dashboard
│   ├── __init__.py
│   └── app.py
├── docs/                         # Documentation 📚
│   ├── DEPLOYMENT_GUIDE.md      # Google Cloud deployment guide
│   ├── LOCAL_RUN_GUIDE.md       # Local bot running guide ⭐
│   ├── TESTING_GUIDE.md         # Testing guide
│   ├── COST_BREAKDOWN.md        # Cost analysis
│   ├── GOOGLE_CLOUD_DEPLOY.md   # Original GCF guide
│   └── PYTHONANYWHERE_DEPLOY.md # PythonAnywhere guide
├── deploy_scripts/               # Deployment scripts
│   ├── deploy_gcf.sh            # Google Cloud Functions deploy
│   └── pythonanywhere_run.py    # PythonAnywhere entry point
├── scripts/                      # Application scripts ⭐
│   ├── gcf_main.py              # GCF entry point & implementation
│   ├── main.py                  # Local bot entry point & implementation
│   └── run_dashboard.py         # Dashboard entry point & implementation
├── gcf_requirements.txt          # GCF dependencies
├── requirements.txt              # Core dependencies
├── README.md                     # This file
├── CLAUDE.md                     # AI assistant documentation
└── .env                         # Environment variables (not in git)
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- Telegram account
- Anthropic API key - Get from https://console.anthropic.com/

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like `123456789:ABCdefGHI...`)

### 3. Get Your Chat ID

1. Start a conversation with your bot
2. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your chat ID in the response (looks like `123456789`)

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Add your configuration:
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Anthropic API (for AI quote generation)
ANTHROPIC_API_KEY=your_api_key_here

# Schedule Configuration
SCHEDULE_WINDOW=both  # Options: morning, evening, both, random
QUOTE_LANGUAGE=th     # Options: en, th

# Optional: Google Cloud
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_REGION=asia-southeast1
```

### 6. Run Locally

**Option A: Run in Terminal (Development)**
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python -m scripts.main
```

**Option B: Run in Background (Production - Recommended)**
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start bot with nohup (runs 24/7, survives terminal close)
nohup venv/bin/python -m scripts.main > bot_output.log 2>&1 &

# Check status
tail -f bot_output.log
```

📖 **Detailed Guide:** [docs/LOCAL_RUN_GUIDE.md](docs/LOCAL_RUN_GUIDE.md)

**Run the dashboard (optional):**
```bash
python scripts/run_dashboard.py
# or
streamlit run dashboard/app.py
```

## 💬 Telegram Commands

- `/start` - Welcome message and setup guide
- `/quote` - Get a random quote immediately
- `/stats` - View your quote statistics
- `/help` - Show help message

## ☁️ Cloud Deployment

### Google Cloud Functions (Recommended ⭐)

**Free Tier Benefits:**
- 2 million invocations/month
- 400,000 GB-seconds compute time
- 3 scheduler jobs
- **Estimated cost: $0.18/month (6 THB)**

**Quick Deploy:**
```bash
# Install Google Cloud SDK first
curl https://sdk.cloud.google.com | bash

# Deploy with one command
./deploy_scripts/deploy_gcf.sh

# Note: Deployment uses scripts/gcf_main.py as entry point
```

**Detailed Guide:** See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

**Test your deployment:**
```bash
# Get function URL
gcloud functions describe daily-quote-bot \
  --region=asia-southeast1 \
  --format="value(httpsTrigger.url)"

# Test endpoint
curl "https://your-function-url/?period=both"
```

### PythonAnywhere (Alternative)

**Limited free tier**, good for learning.

**Guide:** See [docs/PYTHONANYWHERE_DEPLOY.md](docs/PYTHONANYWHERE_DEPLOY.md)

## 📊 Dashboard Features

The Streamlit dashboard provides:

- 📊 **Statistics Overview**: Total quotes, streaks, source distribution
- 📈 **Timeline View**: Quotes sent over time
- 💬 **Quote History**: Browse all sent quotes with filters
- 📚 **Local Quotes**: View your cached quotes
- 📤 **Manual Send**: Send a quote immediately
- 🤖 **AI Generate**: Test quote generation

## 🧪 Testing

**Test quote generation:**
```bash
python -c "from bot.quote_generator import get_quote; print(get_quote())"
```

**Test Telegram connection:**
```bash
python -c "from bot.telegram_bot import send_quote_sync; send_quote_sync({'text': 'Test message', 'author': 'Test'})"
```

**Test Cloud Function locally:**
```bash
pip install functions-framework
functions-framework --target=send_daily_quote --source=scripts/gcf_main.py
```

**Test all endpoints:** See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)

## 💰 Cost Breakdown

### Personal Use (Current Setup)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Cloud Functions | 60 invocations | **$0.00** ✅ (Free Tier) |
| Cloud Scheduler | 2 jobs | **$0.00** ✅ (Free Tier) |
| Anthropic API | 60 requests | **$0.18** |
| **Total** | | **$0.18/month** (~6 THB) |

**Annual Cost:** ~$2.16 (~72 THB/year)

**Detailed Analysis:** See [docs/COST_BREAKDOWN.md](docs/COST_BREAKDOWN.md)

### Scaling Examples

| Users | Bots | Invocations/Month | Monthly Cost |
|-------|------|------------------|--------------|
| 1 (Personal) | 1 | 60 | $0.18 |
| 3 (Family) | 3 | 180 | $0.84 |
| 10 (Small) | 10 | 600 | $3.50 |
| 1000 (Large) | 1000 | 60,000 | $379.70 |

## 🔧 Configuration Options

### Schedule Windows

- `morning` - Send quotes between 7:00-9:00 AM
- `evening` - Send quotes between 6:00-8:00 PM
- `both` - Send twice daily (morning AND evening)
- `random` - Send once at random time (10 AM - 5 PM)

### Quote Sources

The bot uses a mix of:
- **Local quotes** (from `data/quotes.json`) - Fast, free
- **AI-generated quotes** (via Anthropic Claude) - Unique, $0.003 each

By default, AI quotes are always generated first with fallback to local.

### Languages

- `en` - English only
- `th` - Thai only
- `both` - Randomly mix English and Thai

## 📖 Documentation

- **[Local Run Guide](docs/LOCAL_RUN_GUIDE.md)** ⭐ - Run bot locally 24/7 with nohup
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Complete Google Cloud deployment walkthrough
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing procedures
- **[Cost Breakdown](docs/COST_BREAKDOWN.md)** - Detailed pricing analysis and optimization
- **[Google Cloud Deploy](docs/GOOGLE_CLOUD_DEPLOY.md)** - Original GCF documentation
- **[PythonAnywhere Deploy](docs/PYTHONANYWHERE_DEPLOY.md)** - PythonAnywhere setup guide

## 🛠️ Troubleshooting

### Bot not sending messages

1. ✅ Check bot token is correct
2. ✅ Verify chat ID
3. ✅ Check logs: `tail -f daily_quote.log`
4. ✅ Make sure process is running: `ps aux | grep main.py`

### Cloud Function not working

1. ✅ Check function logs: `gcloud functions logs read daily-quote-bot --region=asia-southeast1`
2. ✅ Verify environment variables in GCP console
3. ✅ Test endpoint manually: `curl "function-url/?period=both"`
4. ✅ Check scheduler jobs: `gcloud scheduler jobs list --location=asia-southeast1`

### Anthropic API errors

1. ✅ Verify API key from https://console.anthropic.com/
2. ✅ Check API quota/usage
3. ✅ Bot will fall back to local quotes if API fails

### Scheduler not triggering

1. ✅ Check scheduler status: `gcloud scheduler jobs list`
2. ✅ Verify timezone settings
3. ✅ Run manually: `gcloud scheduler jobs run daily-quote-morning --location=asia-southeast1`
4. ✅ Check execution logs in Cloud Console

## 📊 Monitoring

### Cloud Console Monitoring

- **Functions:** https://console.cloud.google.com/functions/list
- **Scheduler:** https://console.cloud.google.com/cloudscheduler
- **Logs:** https://console.cloud.google.com/logs/query

### CLI Monitoring

```bash
# View function logs
gcloud functions logs read daily-quote-bot --region=asia-southeast1 --limit=50

# Check scheduler jobs
gcloud scheduler jobs list --location=asia-southeast1

# Get function details
gcloud functions describe daily-quote-bot --region=asia-southeast1
```

### Local Monitoring

```bash
# Follow application logs
tail -f daily_quote.log

# Check if process is running
ps aux | grep "python main.py"
```

## 🔄 Updates & Maintenance

### Update deployed function

```bash
# Make changes to code
# ...

# Redeploy
./deploy_scripts/deploy_gcf.sh
```

### Update scheduler

```bash
# Update schedule time
gcloud scheduler jobs update daily-quote-morning \
  --schedule="0 7 * * *" \
  --time-zone="Asia/Bangkok" \
  --location=asia-southeast1
```

### View statistics

```bash
# View local stats
cat data/stats.json | python -m json.tool

# Or via dashboard
python scripts/run_dashboard.py
```

## 📝 Data Files

- `data/quotes.json` - Local quote cache (add your own quotes here!)
- `data/stats.json` - Statistics and quote history
- `data/scheduler.sqlite` - Persistent scheduler data (local only)
- `daily_quote.log` - Application logs

## 🤝 Contributing

Feel free to:
- Add more quotes to `data/quotes.json`
- Improve quote generation logic
- Enhance the dashboard
- Fix bugs or add features

## 📄 License

MIT License - feel free to use and modify!

## 💡 Tips

### Save on API Costs

**Option 1: Use local quotes only**
```env
# Set in .env or config
USE_AI_QUOTES=False
```
Cost: $0.00/month

**Option 2: Hybrid approach (80% local, 20% AI)**
```python
# Modify quote_generator.py
if random.random() < 0.8:
    return get_local_quote()
else:
    return get_ai_quote()
```
Cost: $0.036/month (80% savings!)

**Option 3: Cache AI quotes**
```python
# Generate 30 quotes/month, reuse them
# Cost: $0.09/month (50% savings)
```

### Performance Optimization

- Use **256 MB memory** (sufficient, cost-effective)
- Target **< 2 seconds** execution time
- Enable response caching where possible
- Monitor logs for errors

## 🔗 References

- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/docs)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)

## 📞 Support

For issues or questions:
1. Check logs first
2. Review troubleshooting section
3. Check relevant documentation in `docs/`
4. Review Cloud Console logs if deployed

---

**Made with ❤️ for daily inspiration**

*Last updated: January 18, 2026*

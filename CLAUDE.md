# Claude AI Assistant Documentation

This document provides context for Claude AI assistants working on the Daily Quote Telegram Bot project.

## Project Overview

**Project Name:** Daily Quote Telegram Bot
**Purpose:** A Telegram bot that sends AI-generated inspirational quotes daily
**Tech Stack:** Python 3.11+, Telegram Bot API, Anthropic Claude API, Google Cloud Functions
**Deployment:** Google Cloud Functions (primary), PythonAnywhere (alternative)

## Architecture

### Core Components

1. **Bot Module** (`bot/`)
   - `telegram_bot.py` - Telegram bot integration, command handlers
   - `quote_generator.py` - AI quote generation via Anthropic API
   - `scheduler.py` - Local APScheduler-based task scheduling

2. **Configuration** (`config/`)
   - `settings.py` - Environment-based configuration management
   - Uses `.env` file for secrets (not in git)

3. **Data Layer** (`data/`)
   - `quotes.json` - Local quote cache
   - `stats.json` - Statistics and quote history

4. **Scripts** (`scripts/`) ⭐
   - `gcf_main.py` - Google Cloud Functions entry point & implementation
   - `main.py` - Local bot entry point & implementation
   - `run_dashboard.py` - Dashboard entry point & implementation

5. **Dashboard** (`dashboard/`)
   - Streamlit-based UI for monitoring and manual operations

### Deployment Options

1. **Google Cloud Functions** (Production)
   - Entry point: `scripts/gcf_main.py` → `send_daily_quote()`
   - Scheduler: Cloud Scheduler (HTTP trigger)
   - Cost: ~$0.18/month (Free Tier + Anthropic API)

2. **Local** (Development)
   - Entry point: `scripts/main.py`
   - Scheduler: APScheduler (persistent via SQLite)

3. **PythonAnywhere** (Alternative)
   - Entry point: `deploy_scripts/pythonanywhere_run.py`
   - Limited free tier

## Key Features

### Quote Generation

- **Primary:** Anthropic Claude API (Claude 3 Haiku)
- **Fallback:** Local quotes from `data/quotes.json`
- **Languages:** English (`en`), Thai (`th`), or both
- **Cost:** ~$0.003 per AI-generated quote

### Scheduling Modes

1. **Morning** - 7:00-9:00 AM
2. **Evening** - 6:00-8:00 PM
3. **Both** - Morning AND evening
4. **Random** - Once per day, random time 10 AM - 5 PM (date-seeded)

### Telegram Commands

- `/start` - Welcome message
- `/quote` - Get random quote immediately
- `/stats` - View statistics
- `/help` - Show help message

## Environment Variables

Required variables in `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=123456789

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Schedule Configuration
SCHEDULE_WINDOW=both  # morning|evening|both|random
QUOTE_LANGUAGE=th     # en|th

# Optional: Google Cloud
GOOGLE_CLOUD_PROJECT=my-project-id
GOOGLE_CLOUD_REGION=asia-southeast1
```

## File Structure Changes

**Recent reorganizations:**
1. Created `docs/` - All documentation moved here
2. Created `deploy_scripts/` - Deployment scripts moved here
3. Created `scripts/` - All entry point & implementation files consolidated here
4. Removed root-level entry point wrappers (now use scripts/ directly)
5. Updated README.md with new structure and badges
6. Added CLAUDE.md (this file)

**Old locations → New locations:**
- `DEPLOYMENT_GUIDE.md` → `docs/DEPLOYMENT_GUIDE.md`
- `TESTING_GUIDE.md` → `docs/TESTING_GUIDE.md`
- `COST_BREAKDOWN.md` → `docs/COST_BREAKDOWN.md`
- `GOOGLE_CLOUD_DEPLOY.md` → `docs/GOOGLE_CLOUD_DEPLOY.md`
- `PYTHONANYWHERE_DEPLOY.md` → `docs/PYTHONANYWHERE_DEPLOY.md`
- `deploy_gcf.sh` → `deploy_scripts/deploy_gcf.sh`
- `pythonanywhere_run.py` → `deploy_scripts/pythonanywhere_run.py`
- Root entry points → Consolidated into `scripts/`:
  - `gcf_main.py` → `scripts/gcf_main.py`
  - `main.py` → `scripts/main.py`
  - `run_dashboard.py` → `scripts/run_dashboard.py`

## Common Tasks

### Testing Quote Generation

```python
from bot.quote_generator import get_quote
quote = get_quote(language='th')
print(quote)
```

### Testing Telegram Connection

```python
from bot.telegram_bot import send_quote_sync
quote = {'text': 'Test', 'author': 'Test'}
send_quote_sync(quote)
```

### Testing Cloud Function Locally

```bash
pip install functions-framework
functions-framework --target=send_daily_quote --source=scripts/gcf_main.py
curl "http://localhost:8080/?period=both"
```

### Deploying to Google Cloud

```bash
./deploy_scripts/deploy_gcf.sh
```

### Viewing Logs

**Local:**
```bash
tail -f daily_quote.log
```

**Cloud Functions:**
```bash
gcloud functions logs read daily-quote-bot \
  --region=asia-southeast1 \
  --limit=50
```

## Important Constraints

### Cloud Functions

1. **Stateless** - Cannot use file system for persistent storage
2. **Read-only** - Stats file writes are wrapped in try/except
3. **HTTP-triggered** - Uses query parameters for control
4. **Time limit** - Maximum 60 seconds per invocation
5. **Memory** - 256 MB (sufficient for this use case)

### Cost Optimization

1. **Free Tier Usage** - Currently using 0.003% of available invocations
2. **Scheduler Jobs** - Using 2/3 free tier jobs
3. **API Costs** - Only significant cost at ~$0.18/month
4. **Scaling** - Can add 1 more scheduler job without cost

### Known Issues

1. **Read-only filesystem** - Cloud Functions environment prevents stats persistence
2. **Random scheduling** - Date-seeded, may send same hour across all scheduler runs
3. **API fallback** - Falls back to local quotes if Anthropic API fails

## Git Workflow

### Current Status

- Branch: `main`
- Remote: `origin/main`
- Recent commits:
  - `648f097` - Add random scheduling and improve Cloud Functions deployment
  - `ccd9915` - Add Google Cloud Functions deployment support
  - `d38edde` - Initial commit: Daily Quote Bot with PythonAnywhere support

### Commit Messages

Follow this format:
```
Brief description

- Detail 1
- Detail 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Development Guidelines

### Code Style

- PEP 8 compliant Python code
- Type hints where appropriate
- Docstrings for functions/classes
- Error handling with logging

### Testing Before Deploying

1. Test quote generation locally
2. Test Telegram connection
3. Test Cloud Function locally (Functions Framework)
4. Test deployed function with curl
5. Test scheduler jobs manually

### Documentation Updates

When adding features:
1. Update README.md if user-facing
2. Update relevant docs/ file if technical
3. Update CLAUDE.md if architectural change
4. Commit with descriptive message

## Recent Changes (January 18, 2026)

### Added
- Random daily scheduling (date-seeded, hour 10-17)
- Read-only filesystem compatibility
- Health check endpoint
- Complete documentation suite:
  - DEPLOYMENT_GUIDE.md - Step-by-step Google Cloud deployment
  - TESTING_GUIDE.md - Comprehensive testing procedures
  - COST_BREAKDOWN.md - Detailed pricing analysis
- Organized folder structure (`docs/`, `deploy_scripts/`, `scripts/`)
- Updated README.md with badges, quick links, cost breakdown

### Modified
- `bot/telegram_bot.py` - Added error handling for read-only filesystem
- `scripts/gcf_main.py` - Added random scheduling logic, health check
- `gcf_requirements.txt` - Added SQLAlchemy dependency

### Test Results

All endpoints tested successfully:
- ✅ Root endpoint (`GET /`)
- ✅ Send both quotes (`?period=both`)
- ✅ Morning only (`?period=morning`)
- ✅ Evening only (`?period=evening`)
- ✅ Random scheduling (`?period=random&hour=14`)

Deployment to Google Cloud successful:
- URL: https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot
- Status: All tests passing

## Cost Summary

**Personal Use (Current):**
- Cloud Functions: $0.00 (Free Tier)
- Cloud Scheduler: $0.00 (Free Tier)
- Anthropic API: $0.18/month
- **Total:** $0.18/month (~6 THB or ~72 THB/year)

**Usage:**
- 60 invocations/month (0.003% of Free Tier)
- 2 scheduler jobs (66.67% of Free Tier)
- Can scale to ~46 bots before exceeding Free Tier

## Future Enhancements

### Potential Improvements

1. **Cost Optimization**
   - Implement hybrid approach (80% local, 20% AI)
   - Cache AI-generated quotes
   - Use local quotes only option

2. **Features**
   - Add more scheduler job (still within Free Tier)
   - Implement quote categories
   - Add user preferences

3. **Architecture**
   - Consider Pub/Sub for multi-user scenarios
   - Add monitoring dashboard
   - Implement automated testing

4. **Documentation**
   - Add video tutorials
   - Create contribution guide
   - Add API documentation

## Support Resources

### Internal Documentation
- README.md - User-facing overview
- docs/DEPLOYMENT_GUIDE.md - Deployment instructions
- docs/TESTING_GUIDE.md - Testing procedures
- docs/COST_BREAKDOWN.md - Pricing analysis

### External Resources
- Google Cloud Functions: https://cloud.google.com/functions/docs
- Anthropic API: https://docs.anthropic.com/claude/docs
- python-telegram-bot: https://docs.python-telegram-bot.org/

## Contact & Contribution

- **License:** MIT
- **Contributions:** Welcome (add quotes, fix bugs, add features)
- **Issues:** Check logs first, then documentation

---

**Last Updated:** January 18, 2026
**Project Status:** Production (Google Cloud Functions deployed and tested)
**Version:** 1.0

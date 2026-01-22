# Local Bot Running Guide

วิธีการรัน Daily Quote Bot บนเครื่อง local เพื่อให้ทำงานตลอด 24/7

## Prerequisites

- Python 3.11+ ติดตั้งแล้ว
- Telegram Bot Token และ Chat ID
- Anthropic API Key

## Installation

### 1. Clone Repository

```bash
cd /Users/coraline/Documents/daily_quote
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment

สร้างไฟล์ `.env` ใน root directory:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Schedule Configuration
SCHEDULE_WINDOW=daily    # morning|evening|both|daily|random
QUOTE_LANGUAGE=both      # en|th|both
```

## Running Bot

### Option 1: Run in Background (Recommended for 24/7) ⭐

ใช้ `nohup` เพื่อให้ bot ทำงานต่อเนื่องแม้ปิด Terminal:

```bash
nohup venv/bin/python -m scripts.main > bot_output.log 2>&1 &
echo "Bot started with PID: $!"
```

**ข้อดี:**
- ทำงานตลอด 24/7
- ไม่หยุดเมื่อปิด Terminal
- เหมาะสำหรับ server หรือเครื่องที่ไม่ปิดบ่อย

**ดู log:**
```bash
tail -f bot_output.log
```

**หยุด bot:**
```bash
pkill -f "python -m scripts.main"
```

---

### Option 2: Run with Screen

```bash
# สร้าง screen session
screen -S daily_quote

# Activate และรัน bot
source venv/bin/activate
python -m scripts.main

# กด Ctrl+A, D เพื่อออกจาก session (bot ยังทำงานอยู่)
```

**กลับมาที่ session:**
```bash
screen -r daily_quote
```

---

### Option 3: Run Normally (Development Only)

```bash
source venv/bin/activate
python -m scripts.main
```

⚠️ **หมายเหตุ:** Bot จะหยุดทำงานเมื่อ:
- ปิด Terminal
- กด Ctrl+C
- ปิดเครื่อง

## Bot Modes

### Schedule Modes (SCHEDULE_WINDOW)

| Mode | Description | Times |
|------|-------------|-------|
| `daily` | ส่ง 8 ครั้ง/วัน (7:00-19:00 น.) | 8 random times |
| `both` | ส่งเช้า+เย็น | 2 times/day |
| `morning` | ส่งเฉพาะเช้า | 7:00-9:00 น. |
| `evening` | ส่งเฉพาะเย็น | 18:00-20:00 น. |
| `random` | ส่งครั้งเดียว/วัน | 10:00-17:00 น. |

### Quote Languages (QUOTE_LANGUAGE)

| Language | Description |
|----------|-------------|
| `th` | ภาษาไทย |
| `en` | ภาษาอังกฤษ |
| `both` | ส่งทั้งสองภาษา |

## Monitoring

### Check Bot Status

```bash
# ดูว่า bot ทำงานอยู่หรือไม่
ps aux | grep "python -m scripts.main" | grep -v grep

# ดู log ล่าสุด
tail -50 bot_output.log

# ดู log แบบ real-time
tail -f bot_output.log
```

### View Scheduled Jobs

```bash
# ดู scheduler database
sqlite3 data/scheduler.sqlite "SELECT * FROM apscheduler_jobs;"
```

## Troubleshooting

### Bot ไม่ส่ง quote

1. **ตรวจสอบ bot ทำงานอยู่:**
   ```bash
   ps aux | grep "python -m scripts.main" | grep -v grep
   ```

2. **ตรวจสอบ log:**
   ```bash
   tail -100 bot_output.log
   ```

3. **ตรวจสอบ scheduler:**
   ```bash
   sqlite3 data/scheduler.sqlite "SELECT job_id, next_run_time FROM apscheduler_jobs;"
   ```

### ModuleNotFoundError

```bash
# ติดตั้ง dependencies ใหม่
source venv/bin/activate
pip install -r requirements.txt
pip install sqlalchemy
```

### Bot ตาย

```bash
# หยุด process เดิม
pkill -f "python -m scripts.main"

# รันใหม่
nohup venv/bin/python -m scripts.main > bot_output.log 2>&1 &
```

## Auto-Start on Boot (Optional)

### macOS (launchd)

สร้างไฟล์ `~/Library/LaunchAgents/com.dailyquote.bot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailyquote.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/coraline/Documents/daily_quote/venv/bin/python</string>
        <string>-m</string>
        <string>scripts.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/coraline/Documents/daily_quote</string>
    <key>StandardOutPath</key>
    <string>/Users/coraline/Documents/daily_quote/bot_output.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/coraline/Documents/daily_quote/bot_error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.dailyquote.bot.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com.dailyquote.bot.plist
```

## Tips

1. **ปิดเครื่อง:** Bot จะหยุดทำงาน ต้องรันใหม่เมื่อเปิดเครื่อง
2. **Log rotation:** ลบ `bot_output.log` เป็นระยะ เพื่อประหยัดพื้นที่
3. **Testing:** ใช้ `python -m bot.quote_generator` เพื่อทดสอบสร้าง quote

## Files Reference

| File | Description |
|------|-------------|
| `scripts/main.py` | Bot entry point |
| `bot/scheduler.py` | Scheduler logic |
| `bot/telegram_bot.py` | Telegram integration |
| `bot/quote_generator.py` | Quote generation |
| `data/scheduler.sqlite` | Scheduler database |
| `bot_output.log` | Bot logs |
| `.env` | Configuration |

---

**Last Updated:** January 22, 2026

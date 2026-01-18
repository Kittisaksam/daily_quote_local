# วิธี Deploy Daily Quote Bot ขึ้น PythonAnywhere (ฟรี)

## ทำไมต้อง PythonAnywhere?
- ฟรีสำหรับบัญชีพื้นฐาน
- รัน 24/7 ไม่ต้องเปิดคอมของคุณ
- รองรับ Python และการทำงานอัตโนมัติตามเวลา
- ง่ายต่อการติดตั้งและใช้งาน

---

## ขั้นตอนที่ 1: สมัครบัญชี PythonAnywhere

1. ไปที่ https://www.pythonanywhere.com
2. คลิก **"Create a Beginner account"** (ฟรี)
3. กรอกข้อมูล:
   - Username: (เลือกชื่อที่ต้องการ)
   - Email: อีเมลของคุณ
   - Password: รหัสผ่าน
4. ยืนยันอีเมลเมื่อได้รับ

---

## ขั้นตอนที่ 2: อัปโหลดโค้ดไป PythonAnywhere

### วิธี A: ผ่าน Web Interface (ง่ายที่สุด)

1. Login เข้า PythonAnywhere
2. ไปที่เมนู **"Files"**
3. อัปโหลดไฟล์ทั้งหมดจากโปรเจกต์:
   - คลิก **"Upload a file"**
   - อัปโหลดไฟล์เหล่านี้:
     ```
     ├── bot/
     │   ├── __init__.py
     │   ├── quote_generator.py
     │   ├── scheduler.py
     │   └── telegram_bot.py
     ├── config/
     │   ├── __init__.py
     │   └── settings.py
     ├── data/
     │   ├── quotes.json
     │   └── stats.json
     ├── .env
     ├── main.py
     ├── pythonanywhere_run.py
     └── requirements.txt
     ```

### วิธี B: ผ่าน Git (แนะนำ)

1. ใน PythonAnywhere, ไปที่ **"Consoles"** → **"Bash"**
2. สร้าง console ใหม่ แล้วรันคำสั่ง:

```bash
cd ~/daily_quote
git init
git remote add origin https://github.com/USERNAME/REPO.git
git pull origin main
```

---

## ขั้นตอนที่ 3: ติดตั้ง Dependencies

1. ไปที่เมนู **"Consoles"**
2. คลิก **"Bash"** (สร้าง console ใหม่ถ้ายังไม่มี)
3. รันคำสั่งต่อไปนี้:

```bash
# สร้าง virtual environment
mkvirtualenv daily_quote

# ติดตั้ง dependencies
pip install -r /path/to/your/files/requirements.txt
```

**หมายเหตุ:** เปลี่ยน `/path/to/your/files/` เป็น path จริงบน PythonAnywhere

---

## ขั้นตอนที่ 4: ตั้งค่า Environment Variables

1. ไปที่เมนู **"Web"** (หรือใช้วิธี Bash console ด้านล่าง)
2. ใน Bash console, แก้ไขไฟล์ `.bashrc`:

```bash
nano ~/.bashrc
```

3. เพิ่มบรรทัดต่อไปนี้ที่ท้ายไฟล์:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
export ANTHROPIC_API_KEY="your_api_key_here"
```

4. บันทึกไฟล์ (Ctrl+O, Enter, Ctrl+X)
5. รันคำสั่ง: `source ~/.bashrc`

---

## ขั้นตอนที่ 5: ตั้งค่า Scheduled Tasks (ส่งคำคมทุกวัน)

1. ไปที่เมนู **"Tasks"**
2. คลิก **"Create a new scheduled task"**

### สำหรับ Morning Quote:
- **Description:** Morning Quote
- **Schedule:** เลือกเวลา เช่น `08:00` every day
- **Command:**
  ```
  /path/to/virtualenv/bin/python /path/to/your/files/pythonanywhere_run.py scheduled
  ```

### สำหรับ Evening Quote:
- **Description:** Evening Quote
- **Schedule:** เลือกเวลา เช่น `20:00` every day
- **Command:** เหมือนด้านบน

3. คลิก **"Create"**

---

## ขั้นตอนที่ 6: ตั้งค่า Always-on Task (Bot Listener)

**ข้อควรระวัง:** บัญชีฟรีไม่มี Always-on task
- ถ้าต้องการใช้ฟีเจอร์นี้ ต้องอัปเกรดเป็นบัญชีรับเลี้ยง (~$5/เดือน)
- หรือขยาย Scheduled Task ให้รันบ่อยขึ้น (เช่น ทุก 10 นาที)

### ถ้ามีบัญชีรับเลี้ยง:

1. ไปที่เมนู **"Web"**
2. ในส่วน "Always-on tasks":
  - **Source file:** `/path/to/your/files/pythonanywhere_run.py`
  - **Working directory:** `/path/to/your/files`
  - **Command:** `bot`

### ถ้าใช้บัญชีฟรี:

สร้าง Scheduled Task ที่รันทุก 10-15 นาที:

```
/path/to/virtualenv/bin/python /path/to/your/files/pythonanywhere_run.py bot
```

---

## ขั้นตอนที่ 7: ทดสอบ

1. ไปที่เมนู **"Consoles"** → **"Bash"**
2. ทดสอบรัน script:

```bash
# ทดสอบ scheduled task
python /path/to/your/files/pythonanywhere_run.py scheduled

# ทดสอบ bot listener (รันสั้นๆ)
timeout 10 python /path/to/your/files/pythonanywhere_run.py bot
```

3. ตรวจสอบ log:

```bash
tail -f /var/www/daily_quote_pythonanywhere_com/log.log
```

---

## แก้ไขปัญหา (Troubleshooting)

### ไม่ได้รับข้อความ

1. **ตรวจสอบ Log:**
   ```bash
   tail -100 /var/www/daily_quote_pythonanywhere_com/log.log
   ```

2. **ตรวจสอบ Environment Variables:**
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

3. **ตรวจสอบว่า Task รันหรือยัง:**
   - ไปที่เมนู "Tasks" → "Task schedule"
   - ดูว่ามี "✓" สีเขียวหรือไม่

### Path ไม่ถูกต้อง

ถ้าได้ error เรื่อง path ให้:

1. ใน Bash console, รัน:
   ```bash
   pwd
   ```

2. ใช้ path นี้ใน command ของ Scheduled Tasks

### Virtual Environment ไม่ทำงาน

ตรวจสอบว่า virtual environment ถูกต้อง:

```bash
which python
# ควรได้: /home/username/.virtualenvs/daily_quote/bin/python
```

---

## จำกัดของบัญชีฟรี PythonAnywhere

- **ไม่มี Always-on tasks:** Bot จะไม่ตอบสนองคำสั่งทันที
- **Scheduled tasks:** จำกัด 1 task ต่อวันสำหรับบัญชีฟรี
- **CPU time:** จำกัดการใช้ CPU

**ทางเลือกถ้าต้องการฟีเจอร์เต็ม:**
- อัปเกรดเป็นบัญชีรับเลี้ยง (~$5/เดือน)
- หรือใช้ Render/Railway (ฟรีมากกว่า)

---

## ทางเลือกอื่น: ใช้ Render (ฟรี + ง่ายกว่า)

ถ้า PythonAnywhere ยุ่งยากไป ลองใช้ **Render.com** (ฟรี):

1. สร้าง `Dockerfile` และ `render.yaml`
2. Push โค้ดไป GitHub
3. เชื่อมต่อ Render กับ GitHub
4. Deploy อัตโนมัติ!

ต้องการให้ผมช่วยสร้างไฟล์สำหรับ Render ไหม?

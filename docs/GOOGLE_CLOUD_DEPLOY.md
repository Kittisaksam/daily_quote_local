# วิธี Deploy Daily Quote Bot บน Google Cloud Functions (ฟรี)

## ทำไมต้อง Google Cloud Functions?

✅ **Free Tier สูง:**
- 2 ล้าน invocations ต่อเดือน (ฟรี)
- GB*seconds ฟรี 400,000 ต่อเดือน
- 3 จ๊อบ Scheduler ฟรี

✅ **รัน 24/7:** ไม่ต้องเปิดคอม รันบน cloud ของ Google

✅ **เสถียร:** ใช้โครงสร้างของ Google ที่เสถียรและปลอดภัย

✅ **จ่ายตามการใช้งาน:** ถ้าใช้ฟรีไม่ถึง ไม่ต้องจ่ายเลย

---

## ขั้นตอนที่ 1: สร้าง Google Cloud Project

### 1.1 ไปที่ Google Cloud Console

เข้าไปที่: https://console.cloud.google.com

### 1.2 สร้าง Project ใหม่

1. คลิกที่ dropdown ด้านบน (ที่ชื่อ project)
2. คลิก **"NEW PROJECT"**
3. กรอกข้อมูล:
   - **Project name:** `daily-quote-bot` (หรือชื่อที่ต้องการ)
   - **Organization:** ไม่ต้องเลือก (ถ้าไม่มี)
4. คลิก **"CREATE"**

⏳ รอสักครู่ (ประมาณ 1-2 นาที) ให้ project สร้างเสร็จ

---

## ขั้นตอนที่ 2: ติดตั้ง Google Cloud SDK

### 2.1 ติดตั้ง gcloud CLI

#### สำหรับ macOS:
```bash
# ใช้ Homebrew
brew install google-cloud-sdk

# หรือดาวน์โหลดจาก
# https://cloud.google.com/sdk/docs/install
```

#### สำหรับ Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### สำหรับ Windows:
ดาวน์โหลด installer จาก: https://cloud.google.com/sdk/docs/install

### 2.2 Authenticate กับ Google

```bash
# Login เข้า Google account
gcloud auth login

# จะเปิด browser ให้ login
```

### 2.3 ตั้งค่า default project

```bash
# แสดงรายชื่อ projects
gcloud projects list

# ตั้งค่า default project
gcloud config set project daily-quote-bot

# หรือใช้ ID project ของคุณ
# gcloud config set project YOUR_PROJECT_ID
```

---

## ขั้นตอนที่ 3: เปิดใช้งาน APIs ที่จำเป็น

```bash
# เปิดใช้ Cloud Functions API
gcloud services enable cloudfunctions.googleapis.com

# เปิดใช้ Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# เปิดใช้ Cloud Pub/Sub API
gcloud services enable pubsub.googleapis.com
```

หรือไปเปิดที่ Console:
1. เข้าไปที่ **"APIs & Services"** → **"Library"**
2. ค้นหาและเปิดใช้:
   - Cloud Functions API
   - Cloud Scheduler API
   - Cloud Pub/Sub API

---

## ขั้นตอนที่ 4: ตั้งค่า Environment Variables

### 4.1 สร้างไฟล์ `.env` ในเครื่อง

```bash
cd /path/to/daily_quote
nano .env
```

### 4.2 ใส่ค่า Environment Variables

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# AI Configuration (optional)
ANTHROPIC_API_KEY=your_api_key_here

# Schedule Configuration (optional)
SCHEDULE_WINDOW=both
MORNING_START=08:00
MORNING_END=09:00
EVENING_START=20:00
EVENING_END=21:00
QUOTE_LANGUAGE=th
```

### 4.3 โหลด Environment Variables

```bash
# สำหรับ Linux/macOS
export $(cat .env | xargs)

# หรือใช้ python-dotenv (ใน deploy script จะใช้อัตโนมัติ)
```

---

## ขั้นตอนที่ 5: Deploy ด้วย Script

### 5.1 ให้สิทธิ์ execute กับ script

```bash
chmod +x deploy_gcf.sh
```

### 5.2 รัน deployment script

```bash
./deploy_gcf.sh
```

Script จะทำอัตโนมัติ:
1. ✅ ตรวจสอบ authentication
2. ✅ เปิดใช้ APIs ที่จำเป็น
3. ✅ Deploy Cloud Function
4. ✅ สร้าง Cloud Scheduler jobs

### 5.3 กรอกข้อมูลเมื่อถาม

เมื่อ script ถาม ให้กรอก:

1. **Project ID:** `daily-quote-bot` (หรือ ID ของคุณ)
2. **Morning Schedule:** เวลาส่งคำคมเช้า เช่น:
   - `0 8 * * *` = 8:00 น. ทุกวัน
   - `30 7 * * *` = 7:30 น. ทุกวัน

3. **Evening Schedule:** เวลาส่งคำคมเย็น เช่น:
   - `0 20 * * *` = 20:00 น. (8 โมงเย็น) ทุกวัน

---

## ขั้นตอนที่ 6: ทดสอบ

### 6.1 ทดสอบ Cloud Function

```bash
# รับ URL ของ function
gcloud functions describe daily-quote-bot \
    --region=asia-southeast1 \
    --format="value(httpsTrigger.url)"

# ทดสอบส่งคำคม
curl "FUNCTION_URL?period=both"
```

### 6.2 ตรวจสอบ Logs

```bash
gcloud functions logs read daily-quote-bot \
    --region=asia-southeast1 \
    --limit=50
```

### 6.3 ตรวจสอบ Scheduler Jobs

```bash
gcloud scheduler jobs list --location=asia-southeast1
```

### 6.4 ทดสอบ Trigger จาก Scheduler

```bash
# Trigger งาน morning
gcloud scheduler jobs run daily-quote-morning --location=asia-southeast1

# Trigger งาน evening
gcloud scheduler jobs run daily-quote-evening --location=asia-southeast1
```

---

## วิธีการดูแลรักษา

### ดู Logs แบบ Real-time

```bash
gcloud functions logs read daily-quote-bot \
    --region=asia-southeast1 \
    --follow
```

### แก้ไขเวลา Schedule

```bash
# แก้ไข morning schedule
gcloud scheduler jobs update http daily-quote-morning \
    --location=asia-southeast1 \
    --schedule="0 9 * * *" \
    --time-zone="Asia/Bangkok"

# แก้ไข evening schedule
gcloud scheduler jobs update http daily-quote-evening \
    --location=asia-southeast1 \
    --schedule="30 21 * * *" \
    --time-zone="Asia/Bangkok"
```

### Update Function เมื่อมีการแก้โค้ด

```bash
gcloud functions deploy daily-quote-bot \
    --runtime=python311 \
    --region=asia-southeast1 \
    --source=. \
    --entry-point=send_daily_quote \
    --requirements-file=gcf_requirements.txt \
    --allow-unauthenticated
```

### ลบ Function (ถ้าต้องการ)

```bash
# ลบ scheduler jobs
gcloud scheduler jobs delete daily-quote-morning --location=asia-southeast1
gcloud scheduler jobs delete daily-quote-evening --location=asia-southeast1

# ลบ function
gcloud functions delete daily-quote-bot --region=asia-southeast1
```

---

## ค่าใช้จ่าย (Pricing)

### Free Tier ของ Google Cloud Functions

| รายการ | Free Tier | เกิน (จ่ายตามการใช้) |
|--------|-----------|---------------------|
| Invocations | 2 ล้าน/เดือน | $0.40 ต่อล้านครั้ง |
| Compute (GB-sec) | 400,000/เดือน | $0.0000165 ต่อ GB-sec |
| Network | 5 GB/เดือน | $0.12 ต่อ GB |

### Free Tier ของ Cloud Scheduler

- 3 จ๊อบ/เดือน (ฟรี)
- $0.10 ต่อจ๊อบ (เกินจากนั้น)

### การประเมินต้นทุน

สำหรับ Daily Quote Bot:
- ส่ง 2 ครั้ง/วัน = 60 ครั้ง/เดือน
- **ใช้เพียง 0.003% ของ Free Tier** ✅

**สรุป:** ฟรีทั้งหมด! ไม่ต้องจ่ายเงิน

---

## แก้ปัญหา (Troubleshooting)

### ปัญหา: Authentication Error

```bash
gcloud auth login
gcloud auth application-default login
```

### ปัญหา: Permission Denied

ตรวจสอบ IAM permissions:

```bash
gcloud projects get-iam-policy PROJECT_ID
```

ต้องมี permission:
- Cloud Functions Developer
- Cloud Scheduler Admin

### ปัญหา: Function ไม่ส่งข้อความ

ตรวจสอบ logs:

```bash
gcloud functions logs read daily-quote-bot \
    --region=asia-southeast1 \
    --limit=100
```

### ปัญหา: Scheduler ไม่ทำงาน

ตรวจสอบ:

```bash
gcloud scheduler jobs describe daily-quote-morning \
    --location=asia-southeast1
```

ตรวจสอบว่า:
- ✅ Schedule state = "enabled"
- ✅ Time zone ถูกต้อง
- ✅ URL ถูกต้อง

### ปัญหา: Environment Variables หาย

เมื่อ redeploy ต้องระบุ env vars ใหม่:

```bash
--set-env-vars=TELEGRAM_BOT_TOKEN=xxx,TELEGRAM_CHAT_ID=yyy
```

---

## ปรับแต่งเพิ่มเติม

### เปลี่ยน Region

เลือก region ใกล้คุณ:

```bash
--region=asia-southeast1  # Singapore
--region=asia-east2       # Hong Kong
--region=asia-northeast1  # Tokyo
```

### เพิ่ม Memory/Timeout

ถ้าต้องการให้ประมวลผลได้เร็วขึ้น:

```bash
gcloud functions deploy daily-quote-bot \
    --memory=512MB \
    --timeout=120s \
    ...
```

---

## เปรียบเทียบกับ PythonAnywhere

| คุณสมบัติ | PythonAnywhere | Google Cloud Functions |
|----------|----------------|----------------------|
| **ราคา** | ฟรี (จำกัด) | ฟรี (2M invocations) |
| **Always-on** | ❌ ต้องจ่าย | ✅ ฟรี |
| **Scheduler** | ✅ มี | ✅ มี (Cloud Scheduler) |
| **Scalability** | ❌ จำกัด | ✅ Auto-scale |
| **Setup** | ง่าย | กลาง-ยาก |
| **เหมาะกับ** | เรียนรู้ | Production |

**แนะนำ:** ถ้าต้องการความเสถียรและฟรี → Google Cloud Functions

---

## ถัดไป?

🎉 **ยินดีด้วย! Bot ของคุณรัน 24/7 แล้ว**

ต่อไปคุณสามารถ:
- ✅ ปิดคอมได้เลย bot จะรันบน cloud
- ✅ แก้โค้ดแล้ว redeploy ได้ทันที
- ✅ เพิ่มฟีเจอร์ใหม่ๆ ได้ตามต้องการ

ต้องการความช่วยเหลือเพิ่มเติมไหม?

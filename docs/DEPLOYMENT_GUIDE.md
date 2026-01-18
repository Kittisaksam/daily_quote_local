# คู่มือการ Deploy Daily Quote Bot ไปยัง Google Cloud Functions

> คู่มือนี้ออกแบบมาเพื่อการเรียนรู้ อธิบายทีละขั้นตอนตั้งแต่เริ่มต้นจนสำเร็จ

## 📋 สารบัญ

1. [แนะนำระบบ](#แนะนำระบบ)
2. [เตรียมความพร้อมก่อนเริ่ม](#เตรียมความพร้อมก่อนเริ่ม)
3. [สร้าง Google Cloud Project](#สร้าง-google-cloud-project)
4. [ติดตั้ง Google Cloud CLI](#ติดตั้ง-google-cloud-cli)
5. [ตั้งค่าการยืนยันตัวตน](#ตั้งค่าการยืนยันตัวตน)
6. [เตรียม Environment Variables](#เตรียม-environment-variables)
7. [Deploy Cloud Function](#deploy-cloud-function)
8. [ตั้งค่า Cloud Scheduler](#ตั้งค่า-cloud-scheduler)
9. [ทดสอบระบบ](#ทดสอบระบบ)
10. [การจัดการและ Monitoring](#การจัดการและ-monitoring)
11. [สรุปค่าใช้จ่าย](#สรุปค่าใช้จ่าย)

---

## แนะนำระบบ

### สถาปัตยกรรมระบบ

```
┌─────────────────┐
│ Cloud Scheduler │ ◄─── ตั้งเวลาส่ง Quote (cron job)
└────────┬────────┘
         │ HTTP Trigger (GET)
         ▼
┌─────────────────┐
│ Cloud Functions │ ◄─── รัน Python code
│  (Python 3.11)  │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Anthropic   │  │   Telegram   │
│     API      │  │     API      │
│  (AI Quotes) │  │  (Send msg)  │
└──────────────┘  └──────────────┘
```

### Services ที่ใช้

| Service | วัตถุประสงค์ |
|---------|--------------|
| **Cloud Functions** | รัน Python code สำหรับส่ง Quote |
| **Cloud Scheduler** | ตั้งเวลาเรียก Cloud Function ตาม cron schedule |
| **Cloud Logging** | เก็บ logs สำหรับ monitoring |
| **Cloud Build** | Build และ deploy (automatic) |

---

## เตรียมความพร้อมก่อนเริ่ม

### 1. สิ่งที่ต้องมีก่อน

- [ ] Google Account (Gmail)
- [ ] Credit/Debit Card สำหรับลงทะเบียน Google Cloud (Google จะเก็บเงินจริงเฉพาะตอนใช้เกิน Free Tier)
- [ ] Telegram Bot Token และ Chat ID
- [ ] Anthropic API Key (สำหรับ AI Quote generation)
- [ ] Computer/Mac ที่ติดตั้ง Python 3.11 ขึ้นไป

### 2. ตรวจสอบเครื่องมือที่ต้องใช้

```bash
# ตรวจสอบ Python version
python3 --version
# ควรเป็น Python 3.11 ขึ้นไป

# ตรวจสอบ git
git --version
```

---

## สร้าง Google Cloud Project

### Step 1: เข้าสู่ Google Cloud Console

1. ไปที่ https://console.cloud.google.com
2. ล็อกอินด้วย Google Account
3. คลิกปุ่ม **"Select a project"** ด้านบน
4. คลิก **"NEW PROJECT"**

### Step 2: กรอกข้อมูล Project

```
Project name: daily-quote-bot
Organization: No organization (หรือเลือก organization ถ้ามี)
Location: No organization
```

5. คลิก **"CREATE"**

> **⏱️ เวลา:** ใช้เวลาประมาณ 1-2 นาทีในการสร้าง project

### Step 3: เลือก Project ที่สร้าง

- รอสักครู่ จากนั้นคลิก **"Select project"** เพื่อเข้าสู่ project ใหม่

### Step 4: เปิดใช้งาน Billing (จำเป็น)

> ⚠️ **Important:** แม้จะมี Free Tier แต่ Google ต้องการบัตรเครดิตเพื่อยืนยันตัวตน

1. ไปที่เมนู **Navigation** ☰ → **Billing**
2. คลิก **"Link a billing account"**
3. ถ้ายังไม่มี ให้สร้าง billing account:
   - กรอกข้อมูลบัตรเครดิต/เดบิต
   - เลือก **"Free Trial"** ($300 เครดิตฟรีสำหรับ 90 วัน)
4. ยืนยันว่า billing account เชื่อมโยงกับ project แล้ว

> 💡 **Tip:** หลังจากใช้ Free Trial ($300) หมด หรือผ่าน 90 วัน ระบบจะ **ไม่คิดเงินอัตโนมัติ** จนกว่าคุณจะอัปเกรดเป็น Paid Account

---

## ติดตั้ง Google Cloud CLI

gcloud CLI เป็นเครื่องมือบรรทัดคำสั่งสำหรับจัดการ Google Cloud resources

### สำหรับ macOS

```bash
# ดาวน์โหลดและติดตั้ง
curl https://sdk.cloud.google.com | bash

# รีสตาร์ท shell เพื่อให้ PATH อัปเดต
exec -l $SHELL

# ตรวจสอบการติดตั้ง
gcloud --version
```

ผลลัพธ์ที่คาดหวัง:
```
Google Cloud SDK 472.0.0
bq 2.0.98
core 2024.01.15
gsutil 5.26
```

### สำหรับ Linux

```bash
# ดาวน์โหลด
curl https://sdk.cloud.google.com > install.sh

# ติดตั้ง
bash install.sh --disable-prompts

# รีสตาร์ท shell
exec -l $SHELL

# ตรวจสอบ
gcloud --version
```

### สำหรับ Windows

ดาวน์โหลด installer จาก: https://cloud.google.com/sdk/docs/install

---

## ตั้งค่าการยืนยันตัวตน

### Step 1: ล็อกอิน

```bash
gcloud auth login
```

- Browser จะเปิดขึ้นมา
- เลือก Google Account ที่ต้องการใช้
- คลิก **"Allow"** เพื่ออนุญาตให้ gcloud เข้าถึง account

### Step 2: ตั้งค่า Default Project

```bash
# แสดงรายการ projects ทั้งหมด
gcloud projects list

# ตั้งค่า default project
gcloud config set project daily-quote-bot
```

### Step 3: ตั้งค่า Default Region (ถ้าต้องการ)

```bash
# แสดง regions ทั้งหมด
gcloud functions regions list

# ตั้งค่า region (ใช้ที่ใกล้เคียงเพื่อ latency ต่ำ)
# สำหรับ ASEAN: asia-southeast1 (Singapore), asia-southeast2 (Jakarta)
gcloud config set functions/region asia-southeast1
```

> 💡 **Region Recommendation:**
> - **asia-southeast1** (Singapore) - ยอดนิยม, เสถียร
> - **asia-east2** (Hong Kong) - ทางเลือกอื่น
> - **us-central1** (Iowa) - ราคาถูกกว่า แต่ latency สูงกว่า

### Step 4: เปิดใช้งาน Required APIs

```bash
# เปิดใช้งาน Cloud Functions API
gcloud services enable cloudfunctions.googleapis.com

# เปิดใช้งาน Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# เปิดใช้งาน Cloud Build API (สำหรับ deployment)
gcloud services enable cloudbuild.googleapis.com

# ตรวจสอบ APIs ที่เปิดใช้งานแล้ว
gcloud services list --enabled | grep -E "cloudfunctions|cloudscheduler|cloudbuild"
```

> ⏱️ **เวลา:** ใช้เวลา 1-2 นาทีต่อ API ที่จะเปิดใช้งานสำเร็จ

---

## เตรียม Environment Variables

สร้างไฟล์ `.env` ใน project root:

```bash
# สร้างไฟล์ .env
touch .env

# แก้ไขไฟล์
nano .env หรือ vim .env
```

วางค่าต่อไปนี้ (แทนที่ด้วยค่าจริงของคุณ):

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Anthropic API (สำหรับ AI Quote Generation)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Schedule Configuration
SCHEDULE_WINDOW=both  # Options: morning, evening, both, random
QUOTE_LANGUAGE=th     # Options: en, th

# Google Cloud (optional - สำหรับ script)
GOOGLE_CLOUD_PROJECT=daily-quote-bot
GOOGLE_CLOUD_REGION=asia-southeast1
```

### วิธีรับค่า Configuration

#### 1. Telegram Bot Token & Chat ID

```bash
# 1. คุยกับ @BotFather บน Telegram
# 2. พิมพ์ /newbot แล้วตั้งชื่อ bot
# 3. BotFather จะส่ง BOT_TOKEN มาให้

# 4. รับ Chat ID ด้วยวิธี:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# หรือคุยกับ @userinfobot บน Telegram
```

#### 2. Anthropic API Key

```bash
# 1. ไปที่ https://console.anthropic.com
# 2. ล็อกอิน หรือสมัครใหม่
# 3. ไปที่ API Keys section
# 4. สร้าง API Key ใหม่
# 5. เก็บ Key นี้ไว้อย่างปลอดภัย (จะแสดงครั้งเดียวเท่านั้น!)
```

---

## Deploy Cloud Function

มี 2 วิธีในการ Deploy:

### วิธีที่ 1: ใช้ Deployment Script (แนะนำ)

```bash
# ทำให้ script สามารถรันได้
chmod +x deploy_gcf.sh

# Deploy ด้วย script
./deploy_gcf.sh
```

Script จะทำอัตโนมัติ:
1. ✅ ตรวจสอบ gcloud CLI
2. ✅ ตรวจสอบการยืนยันตัวตน
3. ✅ ตั้งค่า project
4. ✅ ตรวจสอบ APIs
5. ✅ Deploy Cloud Function
6. ✅ สร้าง Cloud Scheduler jobs
7. ✅ แสดง URL และคำสั่งทดสอบ

### วิธีที่ 2: Deploy ด้วยคำสั่ง gcloud โดยตรง

```bash
# ตั้งค่า environment variables
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_CHAT_ID="your_chat_id"
export ANTHROPIC_API_KEY="your_api_key"

# Deploy Cloud Function
gcloud functions deploy daily-quote-bot \
  --runtime=python311 \
  --region=asia-southeast1 \
  --source=. \
  --entry-point=send_daily_quote \
  --requirements-file=gcf_requirements.txt \
  --allow-unauthenticated \
  --set-env-vars=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN",TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID",ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY",SCHEDULE_WINDOW=both,QUOTE_LANGUAGE=th \
  --memory=256MB \
  --timeout=60s \
  --max-instances=1 \
  --trigger-http
```

> ⏱️ **เวลา:** ใช้เวลาประมาณ 2-5 นาทีในการ deploy ครั้งแรก (ครั้งต่อไปจะเร็วกว่า)

### อธิบาย Parameters

| Parameter | ค่า | ความหมาย |
|-----------|-----|-----------|
| `--runtime` | python311 | Python version 3.11 |
| `--region` | asia-southeast1 | Region สำหรับ deploy |
| `--source` | . | Source code directory |
| `--entry-point` | send_daily_quote | ฟังก์ชันหลักที่จะเรียก |
| `--requirements-file` | gcf_requirements.txt | Python dependencies |
| `--allow-unauthenticated` | - | อนุญาตให้เรียกโดยไม่ต้อง auth |
| `--set-env-vars` | ... | Environment variables |
| `--memory` | 256MB | Memory สูงสุดที่ใช้ได้ |
| `--timeout` | 60s | เวลาสูงสุดต่อ execution |
| `--max-instances` | 1 | จำนวน instances สูงสุด |
| `--trigger-http` | - | Trigger ด้วย HTTP request |

### ตรวจสอบการ Deploy

```bash
# ตรวจสอบสถานะ function
gcloud functions describe daily-quote-bot --region=asia-southeast1

# แสดง URL ของ function
gcloud functions describe daily-quote-bot \
  --region=asia-southeast1 \
  --format="value(httpsTrigger.url)"

# ดู logs ล่าสุด
gcloud functions logs read daily-quote-bot \
  --region=asia-southeast1 \
  --limit=20
```

---

## ตั้งค่า Cloud Scheduler

Cloud Scheduler ใช้สำหรับเรียก Cloud Function ตามเวลาที่กำหนด (cron job)

### เข้าใจ Cron Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

ตัวอย่าง:
- `0 8 * * *` = ทุกวัน เวลา 08:00
- `0 20 * * *` = ทุกวัน เวลา 20:00 (8 โมงเย็น)
- `0 */6 * * *` = ทุก 6 ชั่วโมง
- `0 8 * * 1-5` = วันจันทร์-ศุกร์ เวลา 08:00

### Step 1: รับ Function URL

```bash
FUNCTION_URL=$(gcloud functions describe daily-quote-bot \
  --region=asia-southeast1 \
  --format="value(httpsTrigger.url)")

echo "Function URL: $FUNCTION_URL"
```

### Step 2: สร้าง Morning Scheduler

```bash
gcloud scheduler jobs create http daily-quote-morning \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --location=asia-southeast1 \
  --uri="$FUNCTION_URL?period=morning" \
  --http-method=GET \
  --oidc-service-account-email="$(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
```

### Step 3: สร้าง Evening Scheduler

```bash
gcloud scheduler jobs create http daily-quote-evening \
  --schedule="0 20 * * *" \
  --time-zone="Asia/Bangkok" \
  --location=asia-southeast1 \
  --uri="$FUNCTION_URL?period=evening" \
  --http-method=GET \
  --oidc-service-account-email="$(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
```

### ตรวจสอบ Schedulers

```bash
# แสดง schedulers ทั้งหมด
gcloud scheduler jobs list --location=asia-southeast1

# ดูรายละเอียด scheduler
gcloud scheduler jobs describe daily-quote-morning --location=asia-southeast1

# ทดสอบรัน scheduler ทันที (ไม่ต้องรอเวลา)
gcloud scheduler jobs run daily-quote-morning --location=asia-southeast1
```

### อัปเดต Scheduler (ถ้าต้องการเปลี่ยนเวลา)

```bash
# เปลี่ยนเวลาเป็น 07:00 แทน 08:00
gcloud scheduler jobs update http daily-quote-morning \
  --schedule="0 7 * * *" \
  --location=asia-southeast1 \
  --time-zone="Asia/Bangkok"
```

### ลบ Scheduler

```bash
gcloud scheduler jobs delete daily-quote-morning --location=asia-southeast1
```

---

## ทดสอบระบบ

### Test 1: ทดสอบ Cloud Function โดยตรง

```bash
# รับ URL
FUNCTION_URL=$(gcloud functions describe daily-quote-bot \
  --region=asia-southeast1 \
  --format="value(httpsTrigger.url)")

# ทดสอบส่ง quote (ทั้ง morning และ evening)
curl "$FUNCTION_URL?period=both"

# ผลลัพธ์ที่คาดหวัง:
# {
#   "status": "success",
#   "message": "Sent 2/2 quotes",
#   "results": [
#     {"period": "morning", "status": "success"},
#     {"period": "evening", "status": "success"}
#   ]
# }
```

### Test 2: ทดสอบ Scheduler ทันที

```bash
# ทดสอบ morning scheduler
gcloud scheduler jobs run daily-quote-morning --location=asia-southeast1

# รอสักครู่ แล้วตรวจสอบ Telegram
# คุณควรจะได้รับ quote แล้ว
```

### Test 3: ดู Logs

```bash
# ดู logs ล่าสุด 20 บรรทัด
gcloud functions logs read daily-quote-bot \
  --region=asia-southeast1 \
  --limit=20

# ดู logs แบบ real-time (follow)
gcloud functions logs read daily-quote-bot \
  --region=asia-southeast1 \
  --limit=0 \
  --filter="timestamp>=\"$(date -u +%Y-%m-%dT%H:%M:%S)\""

# ดู logs ทั้งหมดใน Cloud Console
# https://console.cloud.google.com/functions/list
# → คลิก daily-quote-bot → แท็บ "Logs"
```

### Test 4: ทดสอบด้วย Local (ก่อน deploy จริง)

```bash
# ติดตั้ง Functions Framework
pip install functions-framework

# รัน local server
export $(cat .env | xargs)
functions-framework --target=send_daily_quote --source=gcf_main.py --debug

# ทดสอบในอีก terminal
curl "http://localhost:8080/send_daily_quote?period=both"
```

---

## การจัดการและ Monitoring

### Monitoring ด้วย Cloud Logging

```bash
# เข้าถึง Cloud Console
https://console.cloud.google.com/functions/list

# หรือใช้คำสั่ง gcloud
gcloud logging logs list

# ดู logs ของ function
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=daily-quote-bot" \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)"
```

### ดู Metrics และ Statistics

```bash
# ดูจำนวน calls
gcloud functions metrics daily-quote-bot \
  --region=asia-southeast1

# ดู execution time
gcloud functions metrics execution-times daily-quote-bot \
  --region=asia-southeast1
```

### Update Cloud Function

เมื่อคุณแก้ไข code และต้องการ redeploy:

```bash
# Deploy ใหม่ (คำสั่งเดิมกับตอนแรก)
gcloud functions deploy daily-quote-bot \
  --runtime=python311 \
  --region=asia-southeast1 \
  --source=. \
  --entry-point=send_daily_quote \
  --requirements-file=gcf_requirements.txt \
  --allow-unauthenticated \
  --set-env-vars=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN",TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID",ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --memory=256MB \
  --timeout=60s \
  --max-instances=1 \
  --trigger-http
```

### Delete Cloud Function

```bash
# ลบ function (จะลบ schedulers ด้วยอัตโนมัติไม่ได้ ต้องลบ apart)
gcloud functions delete daily-quote-bot --region=asia-southeast1

# ลบ schedulers
gcloud scheduler jobs delete daily-quote-morning --location=asia-southeast1
gcloud scheduler jobs delete daily-quote-evening --location=asia-southeast1
```

---

## สรุปค่าใช้จ่าย

### Free Tier Limits (Google Cloud)

Google Cloud มี Free Tier สำหรับ Cloud Functions:

| Resource | Free Tier | หลังจากใช้ฟรี |
|----------|-----------|-------------|
| **Invocations** | 2 ล้านครั้ง/เดือน | $0.40 ต่อ 1 ล้านครั้ง |
| **Compute Time** | 400,000 GB-seconds | $0.0000165/GB-second |
| **Network** | 1 GB/เดือน | $0.12/GB |
| **Scheduler Jobs** | 3 jobs | $0.10 ต่อ job/เดือน |

### คำนวณค่าใช้จ่ายสำหรับ Daily Quote Bot

#### สมมติใช้งาน:
- Morning quote: 1 ครั้ง/วัน
- Evening quote: 1 ครั้ง/วัน
- **รวม:** 2 invocations/วัน = **60 invocations/เดือน**

#### Cost Calculation:

| Item | Usage | Cost (หลัง Free Tier) |
|------|-------|---------------------|
| **Invocations** | 60/เดือน | **ฟรี** (ในเขต 2 ล้าน/เดือน) |
| **Compute Time** | ~2 sec × 60 = 120 GB-sec/เดือน | **ฟรี** (ในเขต 400,000 GB-sec/เดือน) |
| **Network** | ~1 KB × 60 = ~60 KB/เดือน | **ฟรี** (ในเขต 1 GB/เดือน) |
| **Scheduler Jobs** | 2 jobs | **ฟรี** (ในเขต 3 jobs) |
| **Total** | - | **$0.00/เดือน** ✅ |

### Breakdown หากไม่มี Free Tier:

ถ้าไม่มี Free Tier หรือใช้เกินลิมิต:

```
Invocations: 60 × $0.40/1,000,000 = $0.000024
Compute: 120 GB-sec × $0.0000165 = $0.00198
Network: 0.00006 GB × $0.12 = $0.0000072
Scheduler: 2 × $0.10 = $0.20

Total: ~$0.22/เดือน = 7-8 บาท/เดือน
```

### 💡 สรุป: **ค่าใช้จ่าย = ฟรีสนิท** ✅

เนื่องจากการใช้งานน้อยมาก (60 calls/เดือน) ยังอยู่ใน Free Tier ทั้งหมด

### Additional Costs อื่นๆ ที่อาจเกิดขึ้น:

| Service | Cost | หมายเหตุ |
|---------|------|----------|
| **Anthropic API** | ~$0.003/request | สำหรับ AI quote generation |
| **Telegram API** | ฟรี | ไม่มีค่าใช้จ่าย |

> 💡 **Tip:** หากต้องการลดค่าใช้จ่าย Anthropic API สามารถ:
> 1. ปิด AI generation ใช้เฉพาะ local quotes
> 2. Cache quotes ที่ generate แล้ว
> 3. ใช้ API ถูกกว่า (เช่น OpenAI)

### ค่าใช้จ่ายเฉลี่ยต่อปี:

```
Cloud Functions:      $0.00   (ฟรีใน Free Tier)
Cloud Scheduler:      $0.00   (ฟรีใน Free Tier)
Anthropic API:        ~$0.65  (60 req × $0.003 × 12 เดือน)
─────────────────────────────
Total/ปี:             ~$0.65  = 23 บาท/ปี 💰
```

---

## 🎉 สรุปสิ่งที่ได้เรียนรู้

ในคู่มือนี้คุณได้เรียนรู้:

1. ✅ วิธีสร้าง Google Cloud Project
2. ✅ วิธีติดตั้งและใช้งาน gcloud CLI
3. ✅ วิธี Deploy Python code ไป Cloud Functions
4. ✅ วิธีตั้งเวลาด้วย Cloud Scheduler (cron job)
5. ✅ วิธี Monitoring และดู Logs
6. ✅ วิธีคำนวณค่าใช้จ่าย

---

## 🔗 References

- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [gcloud CLI Documentation](https://cloud.google.com/sdk/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

---

## 📞 ติดต่อ/ถามตอบ

หากมีคำถามหรือติดปัญหา:
- ดู Logs: `gcloud functions logs read daily-quote-bot --region=asia-southeast1`
- Cloud Console: https://console.cloud.google.com/functions/list
- Stack Overflow: ใช้ tag `google-cloud-functions`

---

**สร้างเมื่อ:** 18 ม.ค. 2026
**เวอร์ชัน:** 1.0
**โดย:** Claude Sonnet 4.5

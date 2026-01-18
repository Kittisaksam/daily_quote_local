# คู่มือการ Test Daily Quote Bot บน Google Cloud Functions

> คู่มือนี้อธิบายวิธีการ test การ deploy ทีละขั้นตอน เพื่อยืนยันว่าระบบทำงานได้อย่างถูกต้อง

## 📋 สารบัง

1. [เตรียมความพร้อม](#เตรียมความพร้อม)
2. [รับ Function URL](#รับ-function-url)
3. [Test ด้วย cURL](#test-ด้วย-curl)
4. [Test ด้วย Web Browser](#test-ด้วย-web-browser)
5. [Test ด้วย Postman](#test-ด้วย-postman)
6. [Test Cloud Scheduler](#test-cloud-scheduler)
7. [ตรวจสอบ Logs](#ตรวจสอบ-logs)
8. [Troubleshooting](#troubleshooting)
9. [ตัวอย่าง Response](#ตัวอย่าง-response)

---

## เตรียมความพร้อม

### สิ่งที่ต้องมี

- [ ] Function URL ของ Cloud Function ที่ deploy แล้ว
- [ ] Terminal/Command Line
- [ ] หรือ Web Browser
- [ ] หรือ Postman (optional)

---

## รับ Function URL

### วิธีที่ 1: ใช้ gcloud CLI

```bash
# ระบุ project และ region
export PROJECT_ID="my-daily-quote-local"
export REGION="asia-southeast1"
export FUNCTION_NAME="daily-quote-bot"

# รับ URL
gcloud functions describe $FUNCTION_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --format="value(httpsTrigger.url)"
```

ผลลัพธ์:
```
https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot
```

### วิธีที่ 2: ดูจาก Cloud Console

1. ไปที่: https://console.cloud.google.com/functions/list
2. เลือก Project ของคุณ
3. คลิกที่ function name (เช่น `daily-quote-bot`)
4. ดูที่ Tab **Trigger** หรือ **Overview**
5. Copy URL ที่ปรากฏ

### วิธีที่ 3: ดูจาก Deployment Output

เมื่อ deploy เสร็จ จะมี URL แสดงใน output:

```
https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot
```

---

## Test ด้วย cURL

### ติดตั้ง cURL

```bash
# macOS (มีอยู่แล้ว)
curl --version

# Linux/Ubuntu
sudo apt-get install curl

# Windows
# ดาวน์โหลดจาก https://curl.se/download.html
```

### Test 1: Health Check / Root Endpoint

```bash
# Test เรียก function โดยไม่มี parameter
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot"
```

**ผลลัพธ์ที่คาดหวัง:**
```json
{
  "status": "success",
  "message": "Sent 2/2 quotes",
  "results": [
    {"period": "morning", "status": "success"},
    {"period": "evening", "status": "success"}
  ]
}
```

**ความหมาย:**
- Function ทำงานปกติ
- ส่ง quote ทั้ง morning และ evening สำเร็จ

### Test 2: ส่งทั้ง Morning และ Evening

```bash
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=both"
```

**ผลลัพธ์ที่คาดหวัง:**
```json
{
  "status": "success",
  "message": "Sent 2/2 quotes",
  "results": [
    {"period": "morning", "status": "success"},
    {"period": "evening", "status": "success"}
  ]
}
```

**ความหมาย:**
- ส่ง quote ทั้ง 2 ช่วงเวลาสำเร็จ
- คุณควรจะได้รับ 2 ข้อความใน Telegram

### Test 3: ส่งเฉพาะ Morning Quote

```bash
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=morning"
```

**ผลลัพธ์ที่คาดหวัง:**
```json
{
  "status": "success",
  "message": "Sent 1/1 quotes",
  "results": [
    {"period": "morning", "status": "success"}
  ]
}
```

### Test 4: ส่งเฉพาะ Evening Quote

```bash
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=evening"
```

**ผลลัพธ์ที่คาดหวัง:**
```json
{
  "status": "success",
  "message": "Sent 1/1 quotes",
  "results": [
    {"period": "evening", "status": "success"}
  ]
}
```

### Test 5: Test Random Scheduling

```bash
# Test สำหรับ hour 14 (2 โมงเย็น)
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=random&hour=14"
```

**ผลลัพธ์ที่คาดหวัง (ถ้า hour 14 ถูกเลือก):**
```json
{
  "status": "success",
  "message": "Sent 1/1 quotes",
  "results": [
    {
      "period": "random",
      "hour": 14,
      "status": "success"
    }
  ]
}
```

**ผลลัพธ์ที่คาดหวัง (ถ้า hour 14 ไม่ถูกเลือก):**
```json
{
  "status": "success",
  "message": "Sent 0/1 quotes",
  "results": [
    {
      "period": "random",
      "hour": 14,
      "status": "skipped",
      "message": "Not selected hour"
    }
  ]
}
```

**ความหมาย:**
- Random scheduling ใช้ date เป็น seed
- เลือกสุ่ม 1 ชั่วโมงจาก 10-17 นาฬิกา
- เฉพาะชั่วโมงที่ถูกเลือกเท่านั้นจะส่ง quote

### Test 6: ดู Response อย่างละเอียด (pretty print)

```bash
# ใช้ jq สำหรับ pretty print JSON
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=both" | jq .

# หรือใช้ python
curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=both" | python3 -m json.tool
```

### Test 7: ดู HTTP Headers

```bash
# ดู response headers
curl -i "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=morning"

# ดูเฉพาะ headers
curl -I "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=morning"
```

**ผลลัพธ์ที่คาดหวัง:**
```
HTTP/2 200
content-type: application/json
...
```

### Test 8: วัด Performance (Response Time)

```bash
# วัดเวลาที่ใช้
time curl "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=morning"

# หรือใช้ curl แบบละเอียด
curl -w "\nTime Total: %{time_total}s\n" \
  "https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=morning"
```

---

## Test ด้วย Web Browser

### วิธีที่ 1: พิมพ์ URL โดยตรง

เปิด browser และพิมพ์:

```
https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot?period=both
```

### วิธีที่ 2: ใช้ Bookmarks

สร้าง bookmarks สำหรับ test แต่ละแบบ:

| Bookmark Name | URL |
|---------------|-----|
| Test Both | `https://.../?period=both` |
| Test Morning | `https://.../?period=morning` |
| Test Evening | `https://.../?period=evening` |
| Test Random (14h) | `https://.../?period=random&hour=14` |

### วิธีที่ 3: ใช้ Browser DevTools

1. เปิด URL ใน browser
2. กด F12 เปิด DevTools
3. ไปที่ Tab **Network**
4. Refresh page
5. คลิกที่ request
6. ดู:
   - Status Code (ควรเป็น 200)
   - Response Time
   - Response Body

---

## Test ด้วย Postman

### ขั้นตอน

1. เปิด Postman
2. สร้าง Request ใหม่:
   - **Method:** GET
   - **URL:** `https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot`
3. ไปที่ Tab **Params**
4. เพิ่ม parameter:
   - Key: `period`
   - Value: `both`
5. คลิก **Send**

### Test Cases ใน Postman

สร้าง collection ชื่อ "Daily Quote Bot Tests" และเพิ่ม requests:

| Request Name | Method | Params |
|--------------|--------|--------|
| Health Check | GET | (ไม่มี) |
| Send Both | GET | period=both |
| Send Morning | GET | period=morning |
| Send Evening | GET | period=evening |
| Random Hour 10 | GET | period=random&hour=10 |
| Random Hour 14 | GET | period=random&hour=14 |
| Random Hour 17 | GET | period=random&hour=17 |

### บันทึก Test Results

ใช Postman Runner สำหรับ:
- Run ทุก test อัตโนมัติ
- เก็บผลลัพธ์
- Export เป็น report

---

## Test Cloud Scheduler

### ตรวจสอบ Scheduler Jobs

```bash
# แสดง schedulers ทั้งหมด
gcloud scheduler jobs list \
  --project=my-daily-quote-local \
  --location=asia-southeast1

# ดูรายละเอียด scheduler
gcloud scheduler jobs describe daily-quote-morning \
  --project=my-daily-quote-local \
  --location=asia-southeast1
```

### Test รัน Scheduler ทันที

```bash
# รัน morning scheduler ทันที
gcloud scheduler jobs run daily-quote-morning \
  --project=my-daily-quote-local \
  --location=asia-southeast1

# รัน evening scheduler ทันที
gcloud scheduler jobs run daily-quote-evening \
  --project=my-daily-quote-local \
  --location=asia-southeast1
```

หลังจากรัน:
1. รอสักครู่
2. ตรวจสอบ Telegram ของคุณ
3. คุณควรจะได้รับ quote แล้ว

### ตรวจสอบ Scheduler Execution History

```bash
# ดู execution logs
gcloud scheduler jobs describe daily-quote-morning \
  --project=my-daily-quote-local \
  --location=asia-southeast1
```

หรือดูใน Cloud Console:
1. ไปที่ https://console.cloud.google.com/cloudscheduler
2. เลือก job
3. ดู execution history

---

## ตรวจสอบ Logs

### วิธีที่ 1: ใช้ gcloud CLI

```bash
# ดู logs ล่าสุด 20 บรรทัด
gcloud functions logs read daily-quote-bot \
  --project=my-daily-quote-local \
  --region=asia-southeast1 \
  --limit=20

# ดู logs แบบ real-time (follow)
gcloud functions logs read daily-quote-bot \
  --project=my-daily-quote-local \
  --region=asia-southeast1 \
  --limit=0

# ดู logs ตาม time range
gcloud functions logs read daily-quote-bot \
  --project=my-daily-quote-local \
  --region=asia-southeast1 \
  --start-time="2026-01-18T00:00:00Z" \
  --end-time="2026-01-18T23:59:59Z"
```

### วิธีที่ 2: ดูจาก Cloud Console

1. ไปที่: https://console.cloud.google.com/functions/list
2. คลิกที่ `daily-quote-bot`
3. คลิก Tab **Logs**
4. จะเห็น logs แบบ real-time

### วิธีที่ 3: ดูจาก Logging

1. ไปที่: https://console.cloud.google.com/logs/query
2. ใช้ query นี้:
   ```
   resource.type="cloud_function"
   resource.labels.function_name="daily-quote-bot"
   resource.labels.region="asia-southeast1"
   ```
3. คลิก **Run Query**

### Log Examples

**Successful execution:**
```
INFO: Cloud Function triggered: send_daily_quote
INFO: Configuration loaded: both
INFO: Sending morning quote...
INFO: Morning quote sent successfully
INFO: Sending evening quote...
INFO: Evening quote sent successfully
INFO: Cloud Function completed: [{'period': 'morning', 'status': 'success'}, {'period': 'evening', 'status': 'success'}]
```

**Error example:**
```
ERROR: Error sending quote: HTTP 401 Unauthorized
ERROR: Failed to send morning quote
```

---

## Troubleshooting

### ปัญหา: Function ไม่ตอบสนอง (Timeout)

**สาเหตุ:**
- Function ใช้เวลานานเกินไป (เกิน 60 วินาที)
- Network latency สูง

**วิธีแก้:**
```bash
# เพิ่ม timeout
gcloud functions deploy daily-quote-bot \
  --timeout=120s \
  ...
```

### ปัญหา: Status 401 Unauthorized

**สาเหตุ:**
- Telegram Bot Token ผิด
- API Key หมดอายุ

**วิธีแก้:**
1. ตรวจสอบ environment variables
2. ตรวจสอบ token/key
3. Deploy ใหม่ด้วยค่าที่ถูกต้อง

### ปัญหา: Quotes ไม่ถูกส่งไป Telegram

**สาเหตุ:**
- Chat ID ผิด
- Bot ไม่ได้รับอนุญาตจาก user

**วิธีแก้:**
1. ตรวจสอบ Chat ID
2. แน่ใจว่าได้คุยกับ bot ครั้งนึง (send /start)
3. ตรวจสอบ logs

### ปัญหา: Random scheduling ไม่ทำงาน

**สาเหตุ:**
- ส่ง hour ที่ไม่ถูกเลือก

**วิธีแก้:**
```bash
# ลอง test ทุก hour 10-17
for hour in {10..17}; do
  echo "Testing hour $hour:"
  curl "https://.../?period=random&hour=$hour" | jq .
done
```

### ปัญหา: Scheduler ไม่ทำงาน

**สาเหตุ:**
- Service account ไม่มี permission
- Timezone ผิด

**วิธีแก้:**
```bash
# ตรวจสอบ service account
gcloud scheduler jobs describe daily-quote-morning \
  --location=asia-southeast1

# ตรวจสอบ timezone
gcloud scheduler jobs update daily-quote-morning \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok"
```

---

## ตัวอย่าง Response

### Success Response

**Status Code:** 200 OK

```json
{
  "status": "success",
  "message": "Sent 2/2 quotes",
  "results": [
    {
      "period": "morning",
      "status": "success"
    },
    {
      "period": "evening",
      "status": "success"
    }
  ]
}
```

### Partial Success Response

**Status Code:** 207 Multi-Status

```json
{
  "status": "partial_success",
  "message": "Sent 1/2 quotes",
  "results": [
    {
      "period": "morning",
      "status": "success"
    },
    {
      "period": "evening",
      "status": "failed",
      "error": "Send failed"
    }
  ]
}
```

### Error Response

**Status Code:** 500 Internal Server Error

```json
{
  "status": "error",
  "message": "Configuration error: TELEGRAM_BOT_TOKEN not set"
}
```

### Skipped Response (Random Scheduling)

**Status Code:** 200 OK

```json
{
  "status": "success",
  "message": "Sent 0/1 quotes",
  "results": [
    {
      "period": "random",
      "hour": 11,
      "status": "skipped",
      "message": "Not selected hour"
    }
  ]
}
```

---

## Checklist การ Test

ก่อนที่จะถือว่าระบบพร้อมใช้งาน:

- [ ] Test root endpoint (GET /)
- [ ] Test period=both
- [ ] Test period=morning
- [ ] Test period=evening
- [ ] Test random scheduling (หลาย hour)
- [ ] รับ quotes ใน Telegram แล้ว
- [ ] Test morning scheduler ด้วย manual run
- [ ] Test evening scheduler ด้วย manual run
- [ ] ตรวจสอบ logs ไม่มี error
- [ ] Test หลายครั้งเพื่อความมั่นใจ

---

## ตัวอย่างการ Test อย่างสมบูรณ์

```bash
#!/bin/bash

# ตั้งค่า
FUNCTION_URL="https://asia-southeast1-my-daily-quote-local.cloudfunctions.net/daily-quote-bot"

echo "=== Daily Quote Bot Test Suite ==="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
curl -s "$FUNCTION_URL" | jq .
echo ""

# Test 2: Both quotes
echo "Test 2: Send Both Quotes"
curl -s "$FUNCTION_URL?period=both" | jq .
echo ""

# Test 3: Morning only
echo "Test 3: Morning Only"
curl -s "$FUNCTION_URL?period=morning" | jq .
echo ""

# Test 4: Evening only
echo "Test 4: Evening Only"
curl -s "$FUNCTION_URL?period=evening" | jq .
echo ""

# Test 5: Random scheduling
echo "Test 5: Random Scheduling (Hour 14)"
curl -s "$FUNCTION_URL?period=random&hour=14" | jq .
echo ""

# Test 6: Measure performance
echo "Test 6: Performance Test"
time curl -s "$FUNCTION_URL?period=morning" > /dev/null
echo ""

echo "=== All Tests Completed ==="
echo "Please check your Telegram for quotes!"
```

บันทึกเป็น `test.sh` แล้วรัน:

```bash
chmod +x test.sh
./test.sh
```

---

**สร้างเมื่อ:** 18 ม.ค. 2026
**เวอร์ชัน:** 1.0
**โดย:** Claude Sonnet 4.5

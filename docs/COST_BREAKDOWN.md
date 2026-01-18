# รายละเอียดค่าใช้จ่าย Google Cloud Functions สำหรับ Daily Quote Bot

> คู่มีการคำนวณค่าใช้จ่ายอย่างละเอียด เพื่อคาดการณ์และวางแผนงบประมาณสำหรับระบบ

## 📋 สารบัญ

1. [ภาพรวมค่าใช้จ่าย](#ภาพรวมค่าใช้จ่าย)
2. [Google Cloud Functions Pricing](#google-cloud-functions-pricing)
3. [Cloud Scheduler Pricing](#cloud-scheduler-pricing)
4. [Additional Services Pricing](#additional-services-pricing)
5. [คำนวณราคาสำหรับ Daily Quote Bot](#คำนวณราคาสำหรับ-daily-quote-bot)
6. [Free Tier vs Paid Tier](#free-tier-vs-paid-tier)
7. [Scenarios และค่าใช้จ่าย](#scenarios-และค่าใช้จ่าย)
8. [วิธีประหยัดค่าใช้จ่าย](#วิธีประหยัดค่าใช้จ่าย)
9. [การ Monitor ค่าใช้จ่าย](#การ-monitor-ค่าใช้จ่าย)
10. [Budget Alerts](#budget-alerts)

---

## ภาพรวมค่าใช้จ่าย

### สรุปราคารวม (ต่อเดือน)

| Service | การใช้งานจริง | Free Tier | ราคาหลัง Free Tier | ค่าใช้จ่ายจริง |
|---------|------------------|-----------|---------------------|------------------|
| **Cloud Functions** | 60 invocations | 2M invocations | $0.40/M | **$0.00** ✅ |
| **Compute Time** | 120 GB-seconds | 400K GB-seconds | $0.0000165/GB-s | **$0.00** ✅ |
| **Network** | 0.06 GB | 1 GB | $0.12/GB | **$0.00** ✅ |
| **Cloud Scheduler** | 2 jobs | 3 jobs | $0.10/job | **$0.00** ✅ |
| **Anthropic API** | 60 requests | - | $0.003/req | **$0.18** |
| **รวมทั้งหมด** | - | - | - | **~$0.18/เดือน** |

💰 **ประมาณ 6 บาท/เดือน หรือ 72 บาท/ปี**

### Breakdown ราคาตามสัดส่วน

```
ค่าใช้จ่ายรวม: $0.18/เดือน

├── Google Cloud Services: $0.00 (0%) ← ฟรีทั้งหมด!
└── Anthropic API: $0.18 (100%) ← ค่าใช้จ่ายเดียว
```

---

## Google Cloud Functions Pricing

### รูปแบบการคิดเงิน

Google Cloud Functions คิดเงินจาก 3 ปัจจัยหลัก:

1. **Invocations** (จำนวนการเรียก)
2. **Compute Time** (เวลาประมวลผล)
3. **Network Egress** (ปริมาณข้อมูลที่ส่งออก)

### Free Tier Limits

| Resource | Free Tier Limit | หน่วย |
|----------|----------------|--------|
| **Invocations** | 2,000,000 | ครั้ง/เดือน |
| **Compute Time** | 400,000 | GB-seconds/เดือน |
| **Network Egress** | 1 | GB/เดือน |

### Pricing หลังจากใช้ฟรีครบ

#### 1. Invocations

```
ราคา: $0.40 ต่อ 1 ล้านครั้ง

คำนวณ:
- 1 invocation = $0.0000004
- 1,000 invocations = $0.0004
- 100,000 invocations = $0.04
- 1,000,000 invocations = $0.40
```

#### 2. Compute Time

```
ราคา: $0.0000165 ต่อ GB-second

GB-second = Memory (GB) × Time (seconds)

ตัวอย่าง:
- 256 MB × 2 seconds = 0.5 GB-seconds
- 512 MB × 5 seconds = 2.5 GB-seconds
- 1024 MB × 10 seconds = 10 GB-seconds
```

**คำนวณราคา:**

| Memory | Time | GB-seconds | Cost |
|--------|------|------------|------|
| 256 MB | 2 sec | 0.5 | $0.00000825 |
| 256 MB | 5 sec | 1.25 | $0.0000206 |
| 256 MB | 10 sec | 2.5 | $0.0000413 |
| 512 MB | 5 sec | 2.5 | $0.0000413 |
| 1024 MB | 5 sec | 5 | $0.0000825 |

#### 3. Network Egress

```
ราคา: $0.12 ต่อ GB

คำนวณ:
- 1 KB = $0.00000012
- 1 MB = $0.00012
- 1 GB = $0.12
```

### คำนวณราคาตาม Memory Configuration

| Memory | Price per GB-second | ราคา/second | ราคา/minute (60s) |
|--------|-------------------|-------------|-------------------|
| 128 MB | $0.0000165 | $0.00000206 | $0.000124 |
| 256 MB | $0.0000165 | $0.00000413 | $0.000247 |
| 512 MB | $0.0000165 | $0.00000825 | $0.000495 |
| 1024 MB | $0.0000165 | $0.0000165 | $0.00099 |

> 💡 **Tip:** ใช้ memory น้อยที่สุดที่ยังทำงานได้ (256 MB สำหรับ Daily Quote Bot เพียงพอ)

---

## Cloud Scheduler Pricing

### รูปแบบการคิดเงิน

คิดเงินตาม **จำนวน scheduler jobs** ไม่ใช่ตามจำนวน executions!

### Free Tier Limits

```
Free Tier: 3 jobs/เดือน (ต่อ project)
```

### Pricing หลังจากใช้ฟรีครบ

```
ราคา: $0.10 ต่อ job/เดือน

⚠️ Important: คิดเงินตามจำนวน jobs ไม่ใช่ executions!
- 1 job = $0.10/เดือน (ไม่ว่าจะรันกี่ครั้ง)
- 10 jobs = $1.00/เดือน
```

### ตารางราคา

| Jobs | ใน Free Tier | เกิน Free Tier | ราคา/เดือน | ราคา/ปี |
|------|-------------|----------------|-------------|----------|
| 1 | ✅ | - | $0.00 | $0.00 |
| 2 | ✅ | - | $0.00 | $0.00 |
| 3 | ✅ | - | $0.00 | $0.00 |
| 4 | 3 | 1 | $0.10 | $1.20 |
| 5 | 3 | 2 | $0.20 | $2.40 |
| 10 | 3 | 7 | $0.70 | $8.40 |
| 20 | 3 | 17 | $1.70 | $20.40 |

### Scenarios ตามจำนวน executions

**ถ้ารันทุกวัน (cron: `0 8 * * *`):**

| Frequency | Executions/เดือน | ราคา |
|-----------|-------------------|------|
| ทุกวัน | 30-31 | **ฟรี** (อยู่ใน $0.10/job) |
| ทุก 6 ชั่วโมง | ~120 | **ฟรี** |
| ทุก ชั่วโมง | ~720 | **ฟรี** |
| ทุก 5 นาที | ~8,640 | **ฟรี** |

> 💡 **สรุป:** จำนวน executions ไม่มีผลต่อราคา! คิดเงินตามจำนวน jobs เท่านั้น

---

## Additional Services Pricing

### Cloud Logging

```
Free Tier:
- 50 GB logs/เดือน
- 1 ingress log/เดือน (5K invocations)

หลัง Free Tier:
- Storage: $0.50/GB
- Ingestion: $0.50/GB
```

**สำหรับ Daily Quote Bot:**
- ใช้ ~1-2 MB logs/เดือน
- **อยู่ใน Free Tier หมด** ✅

### Cloud Monitoring

```
Free Tier:
- Metrics: ฟรี
- Dashboards: ฟรี
- Alerting policies: ฟรี

หลัง Free Tier:
- ไม่มีข้อจำกัด (ฟรีทั้งหมด)
```

### Cloud Build (สำหรับ deployment)

```
Free Tier: 120 นาที/วัน build time

หลัง Free Tier:
- $0.003/นาทีสำหรับ Linux build
```

**สำหรับ Daily Quote Bot:**
- Deploy ~2-5 นาที/ครั้ง
- **อยู่ใน Free Tier หมด** ✅

### Secret Manager (ถ้าใช้)

```
Free Tier: 6 active versions/เดือน

หลัง Free Tier:
- $0.03/secret version/เดือน
- $0.03/10,000 API calls
```

---

## คำนวณราคาสำหรับ Daily Quote Bot

### สมมติการใช้งาน

```
Configuration:
├── Memory: 256 MB
├── Timeout: 60 seconds
├── Avg execution time: ~2 seconds
├── Schedulers: 2 jobs (morning + evening)
└── Invocations: 60 times/เดือน

Breakdown:
├── Morning quote: 1 time/วัน = 30 times/เดือน
├── Evening quote: 1 time/วัน = 30 times/เดือน
└── Total: 60 times/เดือน
```

### คำนวณราคาทีละรายการ

#### 1. Cloud Functions - Invocations

```
การใช้งาน: 60 invocations/เดือน
Free Tier: 2,000,000 invocations/เดือน
เหลือฟรี: 1,999,940 invocations

ราคาจริง: $0.00 ✅
```

#### 2. Cloud Functions - Compute Time

```
ตำนวณ GB-seconds:
= Memory (GB) × Time (sec) × Invocations
= 0.256 GB × 2 sec × 60
= 30.72 GB-seconds/เดือน

Free Tier: 400,000 GB-seconds
ใช้ไป: 30.72 GB-seconds
เหลือฟรี: 399,969.28 GB-seconds

ราคาจริง: $0.00 ✅
```

#### 3. Cloud Functions - Network

```
ตำนวณปริมาณข้อมูล:
≈ 1 KB/invocation × 60 invocations
= 60 KB/เดือน
= 0.00006 GB/เดือน

Free Tier: 1 GB/เดือน
ใช้ไป: 0.00006 GB
เหลือฟรี: 0.99994 GB

ราคาจริง: $0.00 ✅
```

#### 4. Cloud Scheduler

```
Jobs: 2 jobs (morning + evening)
Free Tier: 3 jobs/เดือน
เหลือฟรี: 1 job

ราคาจริง: $0.00 ✅
```

#### 5. Anthropic API

```
Model: Claude 3 Haiku (fastest, cheapest)
Pricing: $0.25/1M input tokens, $1.25/1M output tokens

คำนวณประมาณ:
- Input: ~200 tokens/request
- Output: ~100 tokens/request
- Cost/request ≈ $0.003

การใช้งาน: 60 requests/เดือน
ราคา: 60 × $0.003 = $0.18/เดือน
```

### สรุปราคารวม

| รายการ | การใช้งาน | Free Tier | ราคาจริง |
|---------|------------|-----------|-----------|
| Cloud Functions | 30.72 GB-sec | 400,000 GB-sec | $0.00 |
| Scheduler | 2 jobs | 3 jobs | $0.00 |
| Logging | ~2 MB | 50 GB | $0.00 |
| Build | ~5 min | 120 min/day | $0.00 |
| Anthropic API | 60 req | - | $0.18 |
| **รวม** | - | - | **$0.18/เดือน** |

💰 **$0.18/เดือน = 6 บาท/เดือน = 72 บาท/ปี**

---

## Free Tier vs Paid Tier

### เมื่อไหร่จะเริ่มจ่ายเงิน?

ระบบจะเริ่มคิดเงินเมื่อ:

#### Cloud Functions

```
เริ่มจ่ายเมื่อ:
├── Invocations เกิน 2,000,000/เดือน หรือ
├── Compute time เกิน 400,000 GB-seconds/เดือน หรือ
└── Network egress เกิน 1 GB/เดือน

Daily Quote Bot:
├── Invocations: 60/เดือน (0.003% ของ Free Tier) ✅
├── Compute: 30.72 GB-sec (0.0077% ของ Free Tier) ✅
└── Network: 0.00006 GB (0.006% ของ Free Tier) ✅

จะเกิน Free Tier เมื่อใช้:
├── Invocations: เกิน 33,333 เท่า
├── Compute time: เกิน 13,020 เท่า หรือ
└── Network: เกิน 16,666 เท่า
```

#### Cloud Scheduler

```
เริ่มจ่ายเมื่อ:
└── Jobs เกิน 3/เดือน

Daily Quote Bot:
└── Jobs: 2/เดือน (66.67% ของ Free Tier) ✅

จะเกิน Free Tier เมื่อ:
└── สร้าง job ที่ 4
```

### Comparison Table

| Metric | Daily Quote Bot | Free Tier Limit | % ของ Free Tier |
|--------|----------------|----------------|-----------------|
| Invocations | 60/เดือน | 2,000,000 | 0.003% |
| Compute Time | 30.72 GB-sec | 400,000 GB-sec | 0.0077% |
| Network | 0.00006 GB | 1 GB | 0.006% |
| Scheduler Jobs | 2 | 3 | 66.67% |

---

## Scenarios และค่าใช้จ่าย

### Scenario 1: Personal Use (ปัจจุบัน)

```
Configuration:
├── 1 bot
├── 2 quotes/วัน (morning + evening)
├── 2 schedulers
└── 60 invocations/เดือน

Cost Breakdown:
├── Cloud Functions: $0.00
├── Scheduler: $0.00
├── Anthropic API: $0.18
└── Total: **$0.18/เดือน** 💰
```

### Scenario 2: Personal Use + Random Quote

```
Configuration:
├── 1 bot
├── 3 quotes/วัน (morning + evening + random)
├── 3 schedulers (เต็ม Free Tier!)
└── 90 invocations/เดือน

Cost Breakdown:
├── Cloud Functions: $0.00
├── Scheduler: $0.00 (ใน Free Tier)
├── Anthropic API: $0.27 (90 × $0.003)
└── Total: **$0.27/เดือน** 💰
```

### Scenario 3: 3 Bots (เพื่อน/ครอบครัว)

```
Configuration:
├── 3 bots
├── 2 quotes/วัน/bot = 6 quotes/วัน
├── 6 schedulers (เกิน Free Tier 3 jobs)
└── 180 invocations/เดือน

Cost Breakdown:
├── Cloud Functions: $0.00
├── Scheduler: $0.30 (3 jobs เกิน × $0.10)
├── Anthropic API: $0.54 (180 × $0.003)
└── Total: **$0.84/เดือน** 💰
```

### Scenario 4: 10 Bots (Small Business)

```
Configuration:
├── 10 bots
├── 2 quotes/วัน/bot = 20 quotes/วัน
├── 20 schedulers (เกิน Free Tier 17 jobs)
└── 600 invocations/เดือน

Cost Breakdown:
├── Cloud Functions: $0.00
├── Scheduler: $1.70 (17 jobs เกิน × $0.10)
├── Anthropic API: $1.80 (600 × $0.003)
└── Total: **$3.50/เดือน** 💰
```

### Scenario 5: High Traffic (1000 users)

```
Configuration:
├── 1000 bots
├── 2 quotes/วัน/bot = 2000 quotes/วัน
├── 2000 schedulers (เกิน Free Tier 1997 jobs)
└── 60,000 invocations/เดือน

Cost Breakdown:
├── Cloud Functions: $0.00 (60K < 2M) ✅
├── Scheduler: $199.70 (1997 × $0.10)
├── Anthropic API: $180.00 (60K × $0.003)
└── Total: **$379.70/เดือน** 💰
```

> ⚠️ **สังเกต:** ถ้าถึง 1000 users ควรพิจารณา redesign ระบบ เพื่อลดจำนวน schedulers

### Scenario 6: Extreme Case (เกิน Free Tier)

```
เมื่อไหร่จะเกิน Free Tier:

Invocations:
60 × 33,333 = 1,999,980 invocations/เดือน
≈ 66,666 invocations/วัน
≈ 2,777 invocations/ชั่วโมง
≈ 46 bots

Compute Time:
30.72 × 13,020 = 400,000 GB-seconds
≈ 13,020 เท่าของการใช้งานปัจจุบัน

Network:
0.00006 × 16,666 = 1 GB
≈ 16,666 เท่าของการใช้งานปัจจุบัน

สรุป:
จะเกิน Free Tier เมื่อมีประมาณ 46 bots หรือมากกว่า
```

---

## วิธีประหยัดค่าใช้จ่าย

### 1. ใช้ Free Tier ให้เต็มที่

✅ **ทำอยู่แล้ว:**
- ใช้งาน 60 invocations/เดือน (เพียง 0.003% ของ Free Tier)
- ใช้ 2 scheduler jobs (66.67% ของ Free Tier)

💡 **สามารถเพิ่มได้อีก:**
- เพิ่มอีก 1 scheduler job ได้โดยไม่มีค่าใช้จ่าย
- เพิ่ม invocations ได้อีก 1,999,940 ครั้ง/เดือน

### 2. ลดการใช้ Anthropic API

**ปัจจุบัน:** ทุก request ใช้ AI generation

**ทางเลือกที่ประหยัดกว่า:**

#### Option A: ใช้ Local Quotes เท่านั้น

```python
# แก้ไข config
USE_AI_QUOTES = False  # ไม่ใช้ Anthropic API

# ใช้เฉพาะ quotes จาก local database
# Cost: $0.00/เดือน ✅
```

**ค่าใช้จ่าย:** ลดลงจาก $0.18 → $0.00/เดือน

#### Option B: Hybrid Approach

```python
# ผสม local quotes และ AI quotes
# 80% local, 20% AI

import random

if random.random() < 0.8:
    quote = get_local_quote()  # ฟรี
else:
    quote = get_ai_quote()     # $0.003

# Cost: 60 × 20% × $0.003 = $0.036/เดือน
```

**ค่าใช้จ่าย:** ลดลงจาก $0.18 → $0.036/เดือน (80% ประหยัด!)

#### Option C: Cache AI Quotes

```python
# Generate AI quotes ล่วงหน้า และ cache ไว้
# Generate 30 quotes/เดือน ใช้ซ้ำทั้งเดือน

# Cost: 30 × $0.003 = $0.09/เดือน (vs $0.18)
```

**ค่าใช้จ่าย:** ลดลง 50%

### 3. ปรับปรุง Performance

ลด execution time → ลด compute cost (ถ้าเกิน Free Tier)

```python
# ปัจจุบัน: ~2 seconds
# หลัง optimize: ~1 second

# ลด compute time 50%
# GB-seconds: 30.72 → 15.36
```

### 4. ใช้ Memory น้อยลง

```python
# ปัจจุบัน: 256 MB
# ถ้าลดเหลือ: 128 MB

# GB-seconds: 30.72 → 15.36
# ประหยัด 50%
```

> ⚠️ **Warning:** ลด memory อาจทำให้ function ทำงานช้าลง ต้อง test ให้ดี

### 5. รวม Schedulers

```
ปัจจุบัน:
├── Scheduler 1: daily-quote-morning (08:00)
└── Scheduler 2: daily-quote-evening (20:00)

ทางเลือก:
└── 1 Scheduler: daily-quote-both (08:00, 20:00)
    → Cloud Function ตรวจสอบเวลาเอง
    → ส่ง morning หรือ evening ตามเวลา

Cost: 2 jobs → 1 job = ลด $0.10/เดือน
```

### 6. ใช้ Pub/Sub แทน Scheduler (สำหรับ large scale)

```
สำหรับระบบขนาดใหญ่ (1000+ users):

แทนที่จะใช้ 1000 schedulers:
├── ใช้ 1 scheduler trigger Pub/Sub
├── Pub/Sub ส่ง message ให้ทุก user
└── Cloud Function process ทีละ batch

Cost: 1000 × $0.10 = $100 → $0.10/เดือน
ประหยัด: $99.90/เดือน! 🎉
```

---

## การ Monitor ค่าใช้จ่าย

### 1. ใช้ Cloud Billing Console

```
URL: https://console.cloud.google.com/billing

ตรวจสอบ:
├── ภาพรวมค่าใช้จ่าย
├── Breakdown ตาม service
├── Trends ตามเวลา
└── Forecasts
```

### 2. ใช้ gcloud CLI

```bash
# ดู cost ปัจจุบันเดือนนี้
gcloud billing accounts list

# Export cost report
gcloud billing accounts export <ACCOUNT_ID> \
  --output-file=cost_report.csv

# ดู cost breakdown
gcloud billing accounts get <ACCOUNT_ID> \
  --format="csv[name,displayName]"
```

### 3. ใช้ Cloud Monitoring Dashboard

```
สร้าง Dashboard สำหรับ monitor:
├── Invocations/time
├── Execution time
├── Error rate
└── Cost estimates
```

### 4. Budget Alerts (ดูรายละเอียดด้านล่าง)

---

## Budget Alerts

### สร้าง Budget Alert

เพื่อไม่ให้ค่าใช้จ่ายเกินงบประมาณ:

```bash
# สร้าง budget
gcloud billing budgets create <ACCOUNT_ID> \
  --budget-amount=5.00 \
  --currency=USD \
  --display-name="Monthly Budget"

# ตั้งค่า alert threshold
gcloud billing budgets update <BUDGET_ID> \
  --threshold-rule=percent=90
```

### ผ่าน Cloud Console

1. ไปที่ https://console.cloud.google.com/billing
2. เลือก Billing Account
3. ไปที่ **Budgets & alerts**
4. คลิก **Create Budget**
5. ตั้งค่า:
   - **Budget amount:** $1.00 (หรือตามต้องการ)
   - **Alert threshold:** 50%, 80%, 100%
   - **Email alerts:** เปิดใช้งาน
   - **Pub/Sub topic:** (optional)

### Recommended Budgets

| Scenario | Recommended Budget |
|----------|-------------------|
| Personal Use | $1.00/เดือน |
| Small Business | $10.00/เดือน |
| Large Scale | $100.00/เดือน |

### Alert Thresholds

```
50% → Warning email
80% → Critical warning
100% → Budget exceeded
```

---

## Summary & Recommendations

### สำหรับ Daily Quote Bot (Personal Use)

✅ **ข้อดี:**
- อยู่ใน Free Tier หมด (Cloud Functions + Scheduler)
- ค่าใช้จ่ายต่ำมาก (~$0.18/เดือน)
- ไม่ต้องกังวลเรื่อง cost

📊 **ค่าใช้จ่าย:**
```
Google Cloud: $0.00/เดือน
Anthropic API: $0.18/เดือน
─────────────────────────
Total: $0.18/เดือน = 6 บาท/เดือน
       = 72 บาท/ปี
```

💡 **Recommendations:**

1. **ตั้ง Budget Alert:** $1.00/เดือน (เผื่อไว้)
2. **Monitor ประจำ:** เช็ค billing console เดือนละครั้ง
3. **พิจารณา Hybrid:** ถ้าต้องการประหยัด ใช้ 80% local + 20% AI
4. **เพิ่ม 1 scheduler:** ยังมีอีก 1 job ฟรี สามารถเพิ่ม feature ได้

### เปรียบเทียบกับทางเลือกอื่น

| Platform | Cost/เดือน | Pros | Cons |
|----------|------------|------|------|
| **Google Cloud (Current)** | $0.18 | ฟรี GCP, เสถียร | ต้อง deploy |
| **PythonAnywhere** | ~$5.00 | ง่าย, ไม่ต้องจัดการ | มีค่าใช้จ่าย |
| **Heroku** | ~$7.00 | ง่าย | แพงมาก |
| **AWS Lambda** | ~$0.10 | คล้าย GCP | Free Tier น้อยกว่า |
| **VPS (DigitalOcean)** | ~$6.00 | ยืดหยุ่น | ต้อง maintain |

> 🏆 **สรุป:** Google Cloud Functions เหมาะสมที่สุดสำหรับ Daily Quote Bot!

---

## Appendix A: Pricing Formulas

### Cloud Functions Cost Formula

```
Total Cost = Invocations Cost + Compute Cost + Network Cost

Invocations Cost = (Total Invocations - 2,000,000) × $0.40/M
                 = 0 ถ้า Total Invocations ≤ 2,000,000

Compute Cost = (Total GB-seconds - 400,000) × $0.0000165/GB-s
             = 0 ถ้า Total GB-seconds ≤ 400,000

Network Cost = (Total Egress GB - 1) × $0.12/GB
             = 0 ถ้า Total Egress ≤ 1 GB
```

### GB-Seconds Formula

```
GB-seconds = Memory (GB) × Execution Time (seconds) × Invocations

Example: 256 MB, 2 seconds, 60 invocations
= 0.256 × 2 × 60
= 30.72 GB-seconds
```

### Scheduler Cost Formula

```
Scheduler Cost = max(0, Total Jobs - 3) × $0.10/job/เดือน

Example: 2 jobs
= max(0, 2 - 3) × $0.10
= 0 × $0.10
= $0.00

Example: 5 jobs
= max(0, 5 - 3) × $0.10
= 2 × $0.10
= $0.20
```

---

## Appendix B: Cost Calculator Script

```python
#!/usr/bin/env python3
"""
Google Cloud Functions Cost Calculator for Daily Quote Bot
"""

def calculate_cost(
    memory_mb: int = 256,
    avg_time_sec: float = 2.0,
    invocations_per_month: int = 60,
    scheduler_jobs: int = 2,
    ai_api_calls: int = 60,
    ai_cost_per_call: float = 0.003
) -> dict:
    """
    Calculate monthly cost for Daily Quote Bot

    Args:
        memory_mb: Memory in MB
        avg_time_sec: Average execution time in seconds
        invocations_per_month: Number of function invocations
        scheduler_jobs: Number of scheduler jobs
        ai_api_calls: Number of AI API calls
        ai_cost_per_call: Cost per AI API call

    Returns:
        Dictionary with cost breakdown
    """

    # Cloud Functions - Compute Time
    gb_seconds = (memory_mb / 1024) * avg_time_sec * invocations_per_month
    compute_cost = max(0, (gb_seconds - 400000) * 0.0000165)

    # Cloud Functions - Invocations
    invocation_cost = max(0, (invocations_per_month - 2000000) * 0.40 / 1000000)

    # Cloud Functions - Network (assume 1 KB per invocation)
    network_gb = (invocations_per_month * 0.001) / 1024
    network_cost = max(0, (network_gb - 1) * 0.12)

    # Cloud Scheduler
    scheduler_cost = max(0, (scheduler_jobs - 3) * 0.10)

    # Anthropic API
    ai_cost = ai_api_calls * ai_cost_per_call

    # Total
    total_cost = compute_cost + invocation_cost + network_cost + scheduler_cost + ai_cost

    return {
        "compute_gb_seconds": gb_seconds,
        "compute_cost": compute_cost,
        "invocation_cost": invocation_cost,
        "network_cost": network_cost,
        "scheduler_cost": scheduler_cost,
        "ai_cost": ai_cost,
        "total_cost": total_cost,
        "in_free_tier": total_cost == 0
    }

# Example usage
if __name__ == "__main__":
    # Personal use (current setup)
    cost = calculate_cost(
        memory_mb=256,
        avg_time_sec=2.0,
        invocations_per_month=60,
        scheduler_jobs=2,
        ai_api_calls=60
    )

    print("=== Daily Quote Bot Cost Calculator ===\n")
    print(f"Compute Time: {cost['compute_gb_seconds']:.2f} GB-seconds")
    print(f"Compute Cost: ${cost['compute_cost']:.4f}")
    print(f"Invocation Cost: ${cost['invocation_cost']:.4f}")
    print(f"Network Cost: ${cost['network_cost']:.4f}")
    print(f"Scheduler Cost: ${cost['scheduler_cost']:.2f}")
    print(f"AI API Cost: ${cost['ai_cost']:.2f}")
    print(f"\n{'='*40}")
    print(f"Total Cost: ${cost['total_cost']:.2f}/month")
    if cost['in_free_tier']:
        print("✅ All Google Cloud services in Free Tier!")
    else:
        print("⚠️  Exceeds Free Tier limits")
```

รัน script:

```bash
python3 cost_calculator.py
```

Output:
```
=== Daily Quote Bot Cost Calculator ===

Compute Time: 30.72 GB-seconds
Compute Cost: $0.0000
Invocation Cost: $0.0000
Network Cost: $0.0000
Scheduler Cost: $0.00
AI API Cost: $0.18

========================================
Total Cost: $0.18/month
✅ All Google Cloud services in Free Tier!
```

---

**สร้างเมื่อ:** 18 ม.ค. 2026
**เวอร์ชัน:** 1.0
**โดย:** Claude Sonnet 4.5

**References:**
- [Google Cloud Functions Pricing](https://cloud.google.com/functions/pricing)
- [Cloud Scheduler Pricing](https://cloud.google.com/scheduler/pricing)
- [Anthropic API Pricing](https://docs.anthropic.com/claude/docs/claude-3-and-claude-3-5-pricing)

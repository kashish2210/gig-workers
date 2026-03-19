# GigShield -- AI-Powered Parametric Insurance for India's Gig Workers

> **Guidewire DEVTrails 2026 | Unicorn Chase | Phase 1 Submission**

![Platform](https://img.shields.io/badge/Platform-Web-0a84ff)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab)
![Django](https://img.shields.io/badge/Django-5.x-092e20)
![AI/ML](https://img.shields.io/badge/AI-Rule--Engine%20%2B%20ML-f59e0b)
![License](https://img.shields.io/badge/License-MIT-a3a3a3)

### Submission Links
*   **Live App:** [https://gig-workers.onrender.com/](https://gig-workers.onrender.com/)
*   **Demo Video:** [https://youtu.be/RJyxeHbifNI](https://youtu.be/RJyxeHbifNI)
*   **Demo Worker:** `demo_worker` / `worker123`
*   **Admin Access:** `admin` / `admin123`

---

## Executive Summary

Every day, 7.7 million gig delivery partners across India wake up not knowing if the weather, pollution, or a sudden curfew will wipe out their earnings for the day. When monsoon rains flood Mumbai's streets or Delhi's AQI crosses 450, these workers do not just lose a shift -- they lose the money that pays rent, buys food, and keeps their families afloat. There is no sick leave. No employer safety net. No insurance product designed for someone who earns INR 4,500 a week delivering food on a motorcycle.

**GigShield** is a parametric insurance platform that solves this. It monitors real-time weather and air quality data across Indian cities, and when conditions breach predefined thresholds -- 30mm/hr rainfall, 45 degree heat, AQI above 400 -- it automatically triggers claims and pays affected workers within hours. No paperwork. No claim forms. No delays. The worker does not need to do anything; the system detects the disruption, validates the event against third-party data sources, and initiates the payout.

What makes GigShield different from traditional insurance is threefold: (1) premiums are dynamically priced using 9 risk factors specific to each worker's city, vehicle, shift, and history, so pricing is fair and transparent; (2) claims are parametric -- triggered by objective, verifiable data rather than subjective assessments; and (3) everything runs on a weekly cycle that matches how gig workers actually earn and spend.

---

## The User: India's Delivery Partners

### Who They Are

Our primary users are platform-based food and grocery delivery partners -- the riders you see navigating traffic on Zomato, Swiggy, Zepto, and Blinkit. They are overwhelmingly male (95%), aged 18-35, earning between INR 15,000 and INR 25,000 per month. Most drive motorcycles or scooters. Many have migrated from smaller towns to metro cities for work. They are not salaried employees; they are classified as independent contractors, which means they receive zero benefits: no health insurance, no paid leave, no income protection of any kind.

### Why Food Delivery Partners Specifically

We focus on food delivery over other gig categories for four precise reasons:

1. **Highest weather sensitivity.** Food delivery is an outdoor, last-mile activity. Unlike ride-hailing (where passengers may still need transport in rain), food delivery demand drops sharply during heavy rainfall, extreme heat, or poor air quality -- but the cost of being on the road does not.

2. **Direct income-to-hours correlation.** A delivery partner earns per delivery. If conditions prevent them from working for 4 hours, they lose exactly 4 hours of income. This makes parametric payouts calculable with high accuracy.

3. **Urban concentration.** Food delivery is concentrated in metro and tier-1 cities (Mumbai, Delhi, Bangalore, Chennai, Kolkata, Hyderabad, Pune) where reliable weather and AQI data exists via public APIs.

4. **Scale.** Zomato and Swiggy alone employ over 400,000 active delivery partners. The total addressable market for platform delivery workers in India exceeds 7.7 million.

### A Day in the Life: What We Are Insuring Against

Consider Rahul, a 24-year-old Swiggy delivery partner in Mumbai's Andheri zone. He earns roughly INR 4,500 per week, working 9-hour shifts on his motorcycle. During monsoon season (June through September), he loses an average of 6 working days per month to heavy rain -- that is INR 3,800 in lost income every monsoon month, or nearly 20% of his monthly earnings.

Rahul cannot afford traditional insurance. He does not have a fixed employer to provide group coverage. He needs something that costs less than INR 100 per week, pays out automatically, and does not require him to file paperwork during a storm.

This is the exact product GigShield provides.

### Persona-Driven Design Decisions

| Design Decision | Persona Insight |
|-----------------|-----------------|
| Weekly premium cycle | Workers are paid weekly by platforms; monthly billing creates cash flow mismatch |
| Auto-triggered claims | Workers are busy delivering; manual claim filing has high abandonment |
| UPI-based payouts | 98% of delivery partners use UPI as their primary payment method |
| Hindi/English UI | Future: vernacular support for non-English-speaking partners |
| Mobile-responsive web | Workers use budget Android phones; native app install is friction |
| Simple plan tiers | Decision fatigue is real; three clear options reduce cognitive load |

---

## How GigShield Works

### End-to-End Architecture

```
WORKER JOURNEY                          SYSTEM BACKEND
                                        
1. Sign Up + Profile Setup              Django User + GigWorkerProfile
   - Platform, city, zone               9 risk factors captured
   - Earnings, vehicle, shift           Risk score computed (0-100)
                                        
2. Choose a Weekly Plan                  InsurancePlan (3 tiers)
   - Basic / Standard / Premium         PremiumCalculation audit trail
   - Dynamic premium shown              9-factor multiplier applied
                                        
3. Real-Time Monitoring                  external_apis/weather.py
   (runs continuously)                  OpenWeatherMap + WAQI APIs
                                        Mock fallback for demo mode
                                        
4. Disruption Detected                   claims/trigger_engine.py
   - Threshold breached                 DisruptionEvent created
   - Severity auto-classified           Affected policies identified
                                        
5. Auto-Claim Initiated                  Claim object created
   - Payout calculated                  fraud_score field populated
   - Evidence snapshot stored           weather_data_snapshot saved
                                        
6. Payout                               payments/ module (Phase 2)
   - Approved amount disbursed          UPI/bank transfer via Razorpay
```

### Data Model Relationships

```
User (AbstractUser)
  |-- role: worker | admin
  |-- GigWorkerProfile (1:1)
  |     |-- platform, city, zone, vehicle, shift
  |     |-- avg_weekly_earnings, experience_months
  |     |-- risk_score, risk_category
  |
  |-- Policy (1:many, via worker FK)
        |-- plan -> InsurancePlan
        |-- week_start, week_end
        |-- base_premium, risk_adjustment, final_premium
        |-- coverage_amount, claims_made, total_claimed
        |-- PremiumCalculation (1:many, audit trail)
        |     |-- 9 individual factor values
        |     |-- model_version: "v1.0-rule-based"
        |
        |-- Claim (1:many)
              |-- disruption_event -> DisruptionEvent
              |-- disruption_type, initiation_type
              |-- estimated_hours_lost, estimated_income_loss
              |-- approved_amount, payout_amount
              |-- fraud_score, fraud_flags
              |-- weather_data_snapshot, aqi_data_snapshot

DisruptionTrigger
  |-- trigger_type: heavy_rain | extreme_heat | severe_pollution | ...
  |-- threshold_value, threshold_unit, threshold_comparison
  |-- payout_percentage, cities_affected
  |
  |-- DisruptionEvent (1:many)
        |-- severity: low | moderate | high | severe | extreme
        |-- measured_value, data_source
        |-- auto_claims_generated
```

---

## Parametric Insurance Engine

### What "Parametric" Means

Traditional insurance requires a worker to (1) experience a loss, (2) file a claim, (3) provide evidence, (4) wait for an adjuster, and (5) receive a payout weeks later. Parametric insurance replaces all of this with a single rule: **if a measurable condition crosses a threshold, the payout is automatic.**

GigShield's parametric triggers are defined as `DisruptionTrigger` objects, each with a threshold value, comparison operator, and payout percentage. When real-time data from weather or AQI APIs meets or exceeds the threshold, the `trigger_engine.py` module:

1. Creates a `DisruptionEvent` with severity auto-classified by how far the measured value exceeds the threshold (1.0-1.2x = moderate, 1.2-1.5x = high, 1.5-2.0x = severe, 2.0x+ = extreme).
2. Queries all active `Policy` objects in the affected city whose plans cover the disruption type.
3. Validates each policy has not already claimed that day and has remaining claim days for the week.
4. Calculates payout based on the worker's declared daily income, hours lost, and the trigger's payout percentage, capped at remaining weekly coverage.
5. Creates `Claim` objects with `initiation_type='automatic'`, attaches the weather data snapshot as evidence, and marks them as approved.

### Active Trigger Definitions

| Trigger | Threshold | Payout % | Data Source | Covered Cities |
|---------|-----------|----------|-------------|----------------|
| Heavy Rainfall | >= 30 mm/hr | 70% | OpenWeatherMap | Mumbai, Chennai, Kolkata, Delhi, Bangalore, Hyderabad, Pune |
| Extreme Heat | >= 45 C | 60% | OpenWeatherMap | Delhi, Jaipur, Ahmedabad, Lucknow, Nagpur, Noida, Gurgaon |
| Severe Air Pollution | AQI >= 400 | 60% | WAQI API | Delhi, Noida, Gurgaon, Lucknow, Kanpur, Patna |
| Flooding | >= 200 mm/24hr | 80% | Weather + Govt alerts | Mumbai, Chennai, Kolkata, Hyderabad, Bangalore |
| Cyclone Warning | Level >= 1 | 100% | IMD alerts | Chennai, Mumbai, Kolkata, Visakhapatnam, Bhubaneswar |

### Manual Claims

Workers can also file manual claims for disruptions not auto-detected by the system. These follow a review workflow (pending -> under_review -> approved/rejected) and carry a `fraud_score` field for AI-based validation.

---

## AI Strategy

### Phase 1 (Current): Rule-Based Intelligence

We are transparent about this: Phase 1 uses a **rule-based engine**, not machine learning. This is a deliberate architectural choice, not a limitation. Here is why:

- **No training data exists** for gig worker parametric insurance in India. We cannot train a model without historical claims data, which we are generating now.
- **Rule-based systems are auditable.** Regulators and investors can inspect every pricing decision. Each premium calculation is stored as a `PremiumCalculation` record with all 9 factor values, enabling full auditability.
- **The rules encode domain expertise.** City risk multipliers (Mumbai 1.30x, Bangalore 1.05x) are calibrated against historical weather patterns. Season factors (monsoon 1.25x, winter 0.90x) reflect actual disruption frequency. These are not arbitrary numbers.

**What the rule engine does today:**
- Computes dynamic premiums using 9 multiplicative risk factors
- Auto-classifies disruption severity from measured-vs-threshold ratios
- Generates risk scores for worker profiles
- Stores every calculation as an audit record with `model_version: "v1.0-rule-based"`

### Phase 2 (Weeks 3-4): Machine Learning Models

With Phase 1 generating claims data, Phase 2 introduces two ML models:

**Dynamic Pricing Model (XGBoost)**
- Training data: premium calculations, claim outcomes, weather history per city/zone
- Features: city, zone, season, vehicle type, shift, experience, claim history, 7-day weather forecast, current AQI
- Target: optimal premium multiplier that maintains 60-70% loss ratio
- Deployment: replaces the lookup-table multipliers in `premium_engine.py`; `model_version` field updates to `"v2.0-xgboost"`

**Fraud Detection Model (Isolation Forest)**
- Training data: claim records with known fraud flags
- Features: GPS coordinates vs. registered zone, weather data cross-verification, claim frequency, payout patterns
- Target: anomaly score (0-100) written to `Claim.fraud_score`
- Flags: written to `Claim.fraud_flags` as JSON array (e.g., `["location_mismatch", "duplicate_claim_window"]`)

### Phase 3 (Weeks 5-6): Advanced Intelligence

- **LSTM-based disruption forecasting:** Predict next-week disruption probability per city/zone using historical weather sequences, enabling proactive premium adjustments
- **Per-worker premium optimization:** Personalized pricing based on individual claim patterns, not just segment-level factors
- **NLP for manual claims:** Extract disruption type and severity from free-text claim descriptions to auto-categorize manual claims

---

## Dynamic Premium Calculation

### The 9-Factor Formula

```
Final Premium = Base Rate x F_city x F_zone x F_season x F_vehicle
                           x F_shift x F_experience x F_claims x F_weather x F_aqi

Where each factor is a multiplier around 1.0:
  > 1.0 = higher risk, higher premium
  < 1.0 = lower risk, discount applied
```

### Factor Definitions

| Factor | Source | Range | Rationale |
|--------|--------|-------|-----------|
| City | Worker profile | 1.00 - 1.30 | Mumbai (1.30) has 3x the monsoon claim risk of Bangalore (1.05) |
| Zone | Worker profile | 1.00 - 1.15 | Flood-prone zones (Andheri, Sion, Dadar) carry 15% surcharge |
| Season | System clock | 0.90 - 1.25 | Monsoon (Jun-Sep) is 1.25x; winter (Nov-Feb) is 0.90x |
| Vehicle | Worker profile | 1.00 - 1.25 | Bicycle/on-foot workers (1.20-1.25x) are most weather-vulnerable |
| Shift | Worker profile | 0.95 - 1.15 | Night shift (1.15x) has visibility/safety risks; morning (0.95x) is safest |
| Experience | Worker profile | 0.90 - 1.05 | 24+ months experience earns 10% discount; new workers pay 5% more |
| Claims History | Database query | 0.92 - 1.20 | Zero past claims = 8% no-claim discount; 5+ claims = 20% surcharge |
| Weather Forecast | OpenWeatherMap | 1.00 - 1.15 | Rain probability > 70% triggers 15% loading |
| AQI Forecast | WAQI API | 1.00 - 1.20 | AQI > 300 triggers 20% loading |

### Worked Example

```
Worker: Rahul, Mumbai (Andheri), Motorcycle, Flexible shift, 18 months experience
Plan:   Standard Shield (Base: INR 79/week)
Season: Summer (March)

Calculation:
  Base:                INR 79.00
  x City (Mumbai):     1.30
  x Zone (Andheri):    1.15    (flood-prone zone)
  x Season (Summer):   1.15
  x Vehicle (Moto):    1.00
  x Shift (Flexible):  1.00
  x Experience (18mo): 0.95    (discount for >12 months)
  x Claims (0 past):   0.92    (no-claim discount)
  x Weather:           1.00
  x AQI:               1.00
  --------------------------
  Combined Multiplier: 1.3367
  Final Premium:       INR 79 x 1.3367 = INR 106/week
  Coverage:            INR 4,500 x 0.70 = INR 3,150/week
```

Every calculation is persisted in the `PremiumCalculation` table with individual factor values, enabling trend analysis and model training in Phase 2.

---

## Plan Tiers

| | Basic Shield | Standard Shield | Premium Shield |
|--|-------------|-----------------|----------------|
| Base Premium | INR 49/week | INR 79/week | INR 129/week |
| Max Weekly Coverage | INR 2,000 | INR 4,000 | INR 7,000 |
| Income Coverage | 50% | 70% | 85% |
| Claim Days/Week | 2 | 3 | 5 |
| Waiting Period | 4 hours | 2 hours | 1 hour |
| Weather Disruptions | Yes | Yes | Yes |
| Pollution Events | No | Yes | Yes |
| Civil Unrest | No | No | Yes |
| Platform Outages | No | No | Yes |

### Why Weekly Billing

Gig workers are paid weekly by their platforms. Monthly insurance premiums create a cash flow mismatch that leads to policy lapses. Weekly billing at INR 49-129 aligns with how workers actually receive income. Workers can skip a week with no penalty -- there is no lock-in.

---

## Market Crash Resilience

The DEVTrails Market Crash event simulates a sudden economic downturn that threatens startup survival. GigShield is built to weather this through structural design choices:

### Low Fixed Costs
GigShield runs on free-tier infrastructure (Railway/Render for hosting, OpenWeatherMap and WAQI free API tiers). Our primary cost is cloud compute, which scales linearly with user count. A 50% drop in users means a roughly 50% drop in costs.

### Counter-Cyclical Demand
Economic downturns push more people into gig work, not fewer. When formal employment contracts, the gig workforce expands. This means our addressable market grows during a crash, not shrinks. More delivery partners means more potential policyholders.

### Parametric Efficiency
Because claims are auto-triggered by objective data (weather, AQI), our operational costs do not scale with claims volume the way a traditional insurer's would. There is no army of adjusters to pay. The trigger engine processes disruptions in milliseconds.

### Premium Adjustment Levers
During a market downturn, we can adjust in three ways without product changes:
1. **Raise base premiums** by 10-15% to maintain loss ratios
2. **Tighten trigger thresholds** (e.g., heavy rain from 30mm to 40mm) to reduce claim frequency
3. **Cap weekly coverage** amounts to limit payout exposure

### Burn Rate Control
With a weekly billing model, revenue is collected every 7 days, not every 30. This gives us 4x the cash flow granularity of monthly billing. If we need to cut costs, we see the revenue impact within a week and can adjust pricing the following week.

### Reserve Management
A prudent reserve policy (holding 2-3 weeks of expected claims as float) ensures we can honor payouts even during a spike in disruption events. The `PremiumCalculation` audit trail lets us model loss ratios historically and project reserves accurately.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Django 5.x + Django REST Framework | Rapid development, mature ORM, built-in auth and admin |
| Database | SQLite (dev) / PostgreSQL (prod) | Zero-config dev, production-grade at scale |
| AI/ML | Scikit-Learn, Pandas, NumPy | Industry-standard ML toolkit, sufficient for Phase 2 models |
| Frontend | Django Templates + Vanilla JS | No build step, server-rendered for speed, Chart.js for analytics |
| Weather Data | OpenWeatherMap API | Reliable, free tier covers development and demo, global coverage |
| Air Quality | WAQI API | Real-time AQI data for Indian cities, free tier available |
| Payments | Razorpay (test mode) | UPI and bank payout support, India-native payment rails |
| Static Files | WhiteNoise | Production-grade static file serving without nginx |
| Icons | Lucide Icons | Lightweight, consistent, MIT-licensed |
| Deployment | Railway or Render | Free-tier cloud hosting with git-based deploys |

---

## Project Structure

```
devtrails/
|-- manage.py
|-- requirements.txt
|-- README.md
|-- gigshield/             Django project settings, root URL config, WSGI
|-- accounts/              Custom User model (AbstractUser), GigWorkerProfile,
|                          registration, login, profile management
|-- policies/              InsurancePlan (3 tiers), Policy (weekly cycle),
|   |-- premium_engine.py  PremiumCalculation. The premium engine implements
|                          the 9-factor dynamic pricing formula.
|-- claims/                DisruptionTrigger definitions, DisruptionEvent
|   |-- trigger_engine.py  records, Claim model with auto/manual initiation.
|                          The trigger engine monitors conditions and auto-
|                          creates claims when thresholds are breached.
|-- fraud/                 Fraud detection module (Phase 2-3). Claim.fraud_score
|                          and Claim.fraud_flags fields are already in the
|                          data model, ready for ML integration.
|-- payments/              Payout processing module (Phase 2-3). Razorpay
|                          integration for UPI/bank disbursement.
|-- analytics/             Worker dashboard (live weather, AQI, policy status,
|                          claims history) and admin dashboard (aggregate
|                          analytics, claims trends, city-level data).
|-- external_apis/         OpenWeatherMap and WAQI API integrations with
|   |-- weather.py         automatic fallback to realistic mock data when
|   |-- aqi.py             API keys are not configured.
|-- ml_models/             ML model training scripts and serialized models
|                          (Phase 2-3). Joblib for model persistence.
|-- static/                CSS design system, JavaScript, Chart.js configs
|-- templates/             Django HTML templates for all views
```

---

## Running Locally

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_TEAM/gigshield.git
cd gigshield

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / Mac
.\venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed initial data (plans, triggers, demo user accounts)
python manage.py seed_data

# Start the development server
python manage.py runserver
```

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Gig Worker | demo_worker | worker123 |

### Key URLs

| Page | URL |
|------|-----|
| Landing Page | http://127.0.0.1:8000/ |
| Worker Dashboard | http://127.0.0.1:8000/dashboard/ |
| Insurance Plans | http://127.0.0.1:8000/policies/plans/ |
| My Policies | http://127.0.0.1:8000/policies/my-policies/ |
| File a Claim | http://127.0.0.1:8000/claims/file/ |
| Disruption Simulator | http://127.0.0.1:8000/claims/simulate/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |

---

## Business Viability

### Unit Economics (Per Worker Per Month)

```
Revenue:
  Average premium: INR 79/week x 4.33 = INR 342/month

Cost:
  Average claim events: 2 per month
  Average payout per event: INR 300
  Total claims: INR 600/month

Loss Ratio: 600 / 342 = 175%   <-- unsustainable at this scale
```

This loss ratio is typical for early-stage parametric insurance and improves with scale through three mechanisms:

1. **Risk pooling.** Not every worker in every city is disrupted every week. With 1,000+ policies across 7 cities, the law of large numbers reduces per-worker variance.
2. **Dynamic pricing convergence.** As claims data accumulates, the ML pricing model (Phase 2) adjusts premiums to reflect actual risk per segment, pushing the loss ratio toward the 60-70% industry target.
3. **Trigger threshold tuning.** If a trigger fires too frequently (e.g., 30mm rain in Mumbai during monsoon), we can adjust the threshold upward to reduce claim frequency while still covering genuinely disruptive events.

### Revenue Projections (Year 1)

| Quarter | Active Policies | Monthly Revenue | Monthly Claims | Loss Ratio |
|---------|----------------|-----------------|----------------|------------|
| Q1 | 500 | INR 1.71L | INR 1.50L | 88% |
| Q2 | 2,000 | INR 6.84L | INR 4.80L | 70% |
| Q3 | 5,000 | INR 17.1L | INR 10.5L | 61% |
| Q4 | 10,000 | INR 34.2L | INR 20.0L | 58% |

Break-even loss ratio target: 65%. Achieved at approximately 3,000 active policies with dynamic pricing enabled.

---

## Development Roadmap

### Phase 1 -- Ideation and Foundation (Weeks 1-2) [COMPLETE]

- [x] Django project architecture with modular app structure
- [x] Custom user model with role-based access (worker / admin)
- [x] GigWorkerProfile with 9 risk-relevant fields
- [x] 3-tier insurance plan system (Basic / Standard / Premium)
- [x] 9-factor dynamic premium calculation engine with audit trail
- [x] 5 parametric trigger definitions with auto-claim generation
- [x] OpenWeatherMap and WAQI API integration with mock fallback
- [x] Worker dashboard with live weather, AQI, policy status, claims
- [x] Admin dashboard with aggregate analytics
- [x] Disruption simulator for demo and testing
- [x] Professional landing page with product positioning
- [x] Complete onboarding flow: register, profile setup, plan selection, policy purchase

### Phase 2 -- Automation and ML (Weeks 3-4)

- [ ] XGBoost dynamic pricing model trained on Phase 1 claims data
- [ ] Isolation Forest fraud detection model
- [ ] Full policy lifecycle management (renewal, expiration, lapse)
- [ ] Worker notification system (email/SMS on claim events)
- [ ] Claims review workflow for manual claims
- [ ] 3-5 live parametric trigger automations via scheduled tasks

### Phase 3 -- Scale and Optimize (Weeks 5-6)

- [ ] LSTM-based disruption forecasting for proactive pricing
- [ ] Per-worker personalized premium optimization
- [ ] Instant payout via Razorpay UPI sandbox
- [ ] Advanced fraud detection (GPS spoofing, duplicate claims)
- [ ] Admin analytics: loss ratios, predictive risk dashboards
- [ ] 5-minute demo video and final pitch deck

---

## Web Platform Justification

We chose a web platform over a native mobile application for the following reasons:

1. **Accessibility.** Works on any device with a browser, including budget Android phones that delivery partners typically use.
2. **Zero install friction.** No app store download required. Workers access GigShield via a URL shared by their platform coordinator.
3. **Instant deployment.** Updates ship immediately without app store review cycles, critical during a 6-week hackathon timeline.
4. **Demo-friendly.** Judges and investors can access the product from any browser without installation.
5. **Progressive enhancement.** The application can be wrapped as a Progressive Web App (PWA) for home screen access and offline support in Phase 3.
## some screenshots:
<img width="1919" height="861" alt="image" src="https://github.com/user-attachments/assets/25823d39-7dbb-4cfe-8e4b-c798a1ce7410" />
<img width="1919" height="868" alt="image" src="https://github.com/user-attachments/assets/d24a1bf0-0f46-47ad-b920-972001a11be0" />
<img width="945" height="845" alt="image" src="https://github.com/user-attachments/assets/08eb9781-c475-42fa-a0bd-1d56b5c4785b" />
<img width="1307" height="649" alt="image" src="https://github.com/user-attachments/assets/f3bb2249-1139-4242-a500-8ba7614f9eb9" />
<img width="1337" height="830" alt="image" src="https://github.com/user-attachments/assets/cc4352e4-143f-44ec-b252-baadf1800cad" />
<img width="1918" height="860" alt="image" src="https://github.com/user-attachments/assets/a6ca7a56-68da-4338-bf17-eb007953b465" />
<img width="692" height="784" alt="image" src="https://github.com/user-attachments/assets/f46f88cc-3d38-47d6-a046-58ddfb78fda8" />
<img width="1919" height="861" alt="image" src="https://github.com/user-attachments/assets/8194b88f-dc49-4285-9040-9fbba88eaabb" />
<img width="1919" height="869" alt="image" src="https://github.com/user-attachments/assets/412e89bc-3490-4114-bc7d-87fa7375f420" />
<img width="1914" height="866" alt="image" src="https://github.com/user-attachments/assets/72b11970-9412-455a-99a4-4bf2185a45c8" />
<img width="1899" height="864" alt="image" src="https://github.com/user-attachments/assets/b607f71f-40e8-46ec-8c04-c94d9db07d79" />
<img width="1919" height="863" alt="image" src="https://github.com/user-attachments/assets/92350a92-cc1b-440b-921b-a972cdccb7c7" />


---

## Team

> Guidewire DEVTrails 2026 -- Dispecables

---

*GigShield: because your income deserves protection, rain or shine.*

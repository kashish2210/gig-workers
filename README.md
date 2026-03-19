# 🛡️ GigShield — AI-Powered Parametric Insurance for India's Gig Workers

> **Guidewire DEVTrails 2026 | Unicorn Chase**

![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.10-green)
![Django](https://img.shields.io/badge/Django-5.x-green)
![AI/ML](https://img.shields.io/badge/AI%2FML-Scikit--Learn-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Executive Summary

**GigShield** is India's first AI-powered parametric insurance platform built exclusively for platform-based delivery partners (Zomato, Swiggy, Zepto, etc.). It provides automated income protection against external disruptions like extreme weather, severe air pollution, flooding, and civil unrest — events that cause gig workers to lose 20-30% of their monthly earnings with no existing safety net.

### The Problem
- **7.7 million** delivery partners in India's gig economy
- External disruptions (weather, pollution, curfews) cause **20-30% income loss**
- **Zero** existing income protection insurance products for gig workers
- Traditional insurance is too slow, too expensive, and doesn't fit the weekly earnings cycle

### Our Solution  
An AI-enabled parametric insurance platform that:
- **Automatically detects** disruptions via real-time weather & AQI APIs
- **Auto-triggers claims** when parametric thresholds are breached
- **Dynamically prices** weekly premiums using 9+ risk factors
- **Instantly pays out** to workers' UPI accounts
- **Detects fraud** using anomaly detection AI

---

## 🎯 Chosen Persona: Food Delivery Partners (Zomato/Swiggy)

We focus on **food delivery partners** because:
1. **Highest weather sensitivity** — deliveries halt in heavy rain, extreme heat
2. **Daily earnings model** — direct correlation between hours worked and income
3. **Urban concentration** — coverage in metro cities with reliable weather data
4. **Largest segment** — Zomato + Swiggy alone have 400,000+ delivery partners

### Persona-Based Scenarios

| Scenario | Disruption | Impact | GigShield Response |
|----------|-----------|--------|--------------------|
| Rahul, Mumbai | Heavy monsoon rain (50mm/hr) | Can't deliver for 6 hours | Auto-claim triggered, ₹450 payout in 2 hrs |
| Priya, Delhi | AQI hits 450 (Severe) | Health advisory, no outdoor work | Auto-claim, 60% income coverage for the day |
| Ahmed, Chennai | Cyclone warning | All deliveries suspended | Full-day payout at 100% coverage |
| Meena, Bangalore | Flooding in delivery zone | Roads impassable | Zone-specific auto-claim, 80% coverage |

---

## 🔧 Application Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKER JOURNEY                           │
│                                                                 │
│  1. SIGN UP         2. PROFILE SETUP        3. CHOOSE PLAN     │
│  ┌──────────┐       ┌──────────────┐       ┌─────────────┐     │
│  │ Register │──────▶│ Platform,    │──────▶│ Basic ₹49   │     │
│  │ Account  │       │ City, Zone,  │       │ Standard ₹79│     │
│  └──────────┘       │ Earnings     │       │ Premium ₹129│     │
│                     └──────────────┘       └──────┬──────┘     │
│                                                   │             │
│  6. PAYOUT          5. AUTO-CLAIM          4. MONITORING       │
│  ┌──────────┐       ┌──────────────┐       ┌─────────────┐     │
│  │ Instant  │◀──────│ Threshold    │◀──────│ Weather API │     │
│  │ UPI/Bank │       │ Breached →   │       │ AQI API     │     │
│  └──────────┘       │ Claim Created│       │ Real-time   │     │
│                     └──────────────┘       └─────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Workflow Steps

1. **Onboarding (2 minutes)**
   - Account creation with phone/email
   - Platform selection (Zomato, Swiggy, etc.)
   - Location setup (city, zone, pincode)
   - Earnings declaration (weekly average)
   - AI risk profiling → Risk score generated

2. **Policy Selection**
   - 3 plan tiers: Basic, Standard, Premium
   - Dynamic premium calculated using 9 risk factors
   - Weekly billing aligned with earnings cycle
   - Transparent factor breakdown shown to user

3. **Real-Time Monitoring**
   - Weather data (OpenWeatherMap API)
   - Air Quality Index (WAQI API)
   - Parametric triggers continuously checked
   - 5+ disruption types monitored

4. **Auto Claim Processing**
   - Trigger threshold breached → Disruption Event created
   - All active policies in affected zone identified
   - Claims auto-initiated with evidence snapshot
   - Fraud detection AI validates the claim

5. **Instant Payout**
   - Approved claims paid via UPI/bank transfer
   - Zero paperwork for workers
   - Payout within 2 hours of disruption

---

## 💰 Weekly Premium Model

### Base Rates
| Plan | Base Premium | Max Coverage | Income % | Claim Days/Week |
|------|-------------|-------------|----------|-----------------|
| Basic Shield | ₹49/week | ₹2,000 | 50% | 2 |
| Standard Shield | ₹79/week | ₹4,000 | 70% | 3 |
| Premium Shield | ₹129/week | ₹7,000 | 85% | 5 |

### Dynamic Premium Calculation (9 Risk Factors)

```
Final Premium = Base × (city × zone × season × vehicle × shift 
                        × experience × claims_history × weather × aqi)

Example for Rahul (Mumbai, Motorcycle, Flexible shift, 18mo exp):
  Base: ₹79.00
  × City (Mumbai): 1.30
  × Zone (Andheri): 1.15
  × Season (Summer): 1.15
  × Vehicle (Motorcycle): 1.00
  × Shift (Flexible): 1.00
  × Experience (18mo): 0.95
  × Claims History (0): 0.92
  × Weather Forecast: 1.00
  × AQI Forecast: 1.00
  ─────────────────────
  Final: ₹79 × 1.3367 = ₹106/week
  Coverage: ₹4,500 × 0.70 = ₹3,150/week
```

### Justification
- **Weekly cycle** matches gig worker payout frequency
- **No penalties** for skipping a week
- **Dynamic pricing** ensures fair rates based on actual risk
- **Range**: ₹35-₹180/week depending on risk profile

---

## 🎯 Parametric Triggers

| Trigger | Threshold | Payout % | Data Source |
|---------|-----------|----------|-------------|
| Heavy Rainfall | ≥ 30 mm/hr | 70% | OpenWeatherMap |
| Extreme Heat | ≥ 45°C | 60% | OpenWeatherMap |
| Severe AQI | ≥ 400 | 60% | WAQI API |
| Flooding | ≥ 200mm/24hr | 80% | Weather + Govt alerts |
| Cyclone Warning | Level ≥ 1 | 100% | IMD alerts |

---

## 🤖 AI/ML Integration Plan

### Phase 1 (Current) — Rule-Based Engine
- 9-factor premium calculation using lookup tables
- Risk scoring based on city, vehicle, shift, experience
- Season-adjusted pricing

### Phase 2 — Machine Learning Models
- **Dynamic Pricing Model**: Gradient boosted decision tree (XGBoost) trained on:
  - Historical weather patterns per city/zone
  - Claim frequency by location/season
  - Worker behavior patterns
  - Real-time weather forecast integration

- **Fraud Detection Model**: Anomaly detection using Isolation Forest:
  - GPS location validation
  - Weather data cross-verification
  - Duplicate claim detection
  - Historical claim pattern analysis

### Phase 3 — Advanced AI
- **Predictive Risk Modeling**: LSTM for next-week disruption forecasting
- **Personalized Pricing**: Per-worker premium optimization
- **NLP for Claims**: Natural language processing for manual claim descriptions

---

## 🏗️ Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Django 5.x + DRF | Robust, rapid development, ORM |
| **Database** | SQLite → PostgreSQL | Simple dev, production-ready |
| **AI/ML** | Scikit-Learn, Pandas, NumPy | Industry-standard ML toolkit |
| **Frontend** | Django Templates + Vanilla JS | Fast, no build step needed |
| **Charts** | Chart.js | Interactive analytics dashboards |
| **Weather API** | OpenWeatherMap (free) | Reliable, global coverage |
| **AQI API** | WAQI (free) | Real-time air quality data |
| **Payments** | Razorpay Test Mode | UPI/bank payout simulation |
| **Icons** | Lucide Icons | Modern, consistent icon set |
| **CSS** | Custom Design System | Premium dark theme with glassmorphism |
| **Deployment** | Railway / Render | Free tier cloud hosting |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_TEAM/gigshield.git
cd gigshield

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed initial data (plans, triggers, demo users)
python manage.py seed_data

# Start the server
python manage.py runserver
```

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Worker | demo_worker | worker123 |

### Key URLs
- **Landing Page**: http://127.0.0.1:8000/
- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Insurance Plans**: http://127.0.0.1:8000/policies/plans/
- **Simulate Disruption**: http://127.0.0.1:8000/claims/simulate/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
gigshield/
├── manage.py
├── requirements.txt
├── README.md
├── gigshield/           # Django settings & URLs
├── accounts/            # User auth, profiles, risk scoring
├── policies/            # Insurance plans, policies, premium engine
│   └── premium_engine.py    # 9-factor dynamic premium calculator
├── claims/              # Claims, parametric triggers, auto-claims
│   └── trigger_engine.py    # Real-time disruption trigger engine
├── fraud/               # AI fraud detection (Phase 2-3)
├── payments/            # Payout processing (Phase 2-3)
├── analytics/           # Dashboards & analytics
├── external_apis/       # Weather & AQI API integrations
├── ml_models/           # ML model training & inference
├── static/              # CSS, JS, images
└── templates/           # HTML templates
```

---

## 📅 Development Plan

### Phase 1 ✅ (Weeks 1-2) — Ideation & Foundation
- [x] Project architecture & setup
- [x] Custom user model with roles
- [x] Gig worker profile & onboarding
- [x] Insurance plan tiers
- [x] Dynamic premium calculation engine
- [x] Parametric trigger definitions
- [x] Claims auto-initiation engine
- [x] Weather & AQI API integration
- [x] Premium landing page
- [x] Worker dashboard with live weather
- [x] Admin dashboard with analytics
- [x] Disruption simulator for demos

### Phase 2 (Weeks 3-4) — Automation & Protection
- [ ] ML-based dynamic pricing model
- [ ] Full policy lifecycle management
- [ ] Zero-touch claim experience
- [ ] 3-5 live parametric trigger automations
- [ ] Claims review workflow
- [ ] Worker notification system

### Phase 3 (Weeks 5-6) — Scale & Optimize
- [ ] Advanced fraud detection AI (GPS spoofing, fake claims)
- [ ] Instant payout via Razorpay/UPI sandbox
- [ ] Worker dashboard: earnings protected, coverage status
- [ ] Admin dashboard: loss ratios, predictive analytics
- [ ] 5-minute demo video
- [ ] Final pitch deck

---

## 🌐 Web Platform Justification

We chose a **web platform** over mobile because:
1. **Accessibility**: Works on any device with a browser
2. **No app store delays**: Instant deployment and updates
3. **Lower friction**: No download required for workers
4. **Demo-friendly**: Easy to showcase in presentations
5. **Progressive enhancement**: Can be wrapped as a PWA later

---

## 📊 Business Viability

### Unit Economics (Per Worker Per Month)
- Average premium: ₹79/week × 4 = **₹316/month**
- Average claims: 2 events/month × ₹300 avg = **₹600/month**
- Loss ratio target: **60-70%** (industry standard for parametric)
- Break-even at scale: **~1,000 active policies**

### Revenue Projections (Year 1)
| Quarter | Active Workers | Monthly Revenue | Monthly Claims |
|---------|---------------|-----------------|----------------|
| Q1 | 500 | ₹1.58L | ₹1.0L |
| Q2 | 2,000 | ₹6.32L | ₹4.0L |
| Q3 | 5,000 | ₹15.8L | ₹9.0L |
| Q4 | 10,000 | ₹31.6L | ₹18.0L |

---

## 👥 Team

> Guidewire DEVTrails 2026 — Unicorn Chase

---

*Built with ❤️ for India's gig workers. Because your income deserves protection, rain or shine.*

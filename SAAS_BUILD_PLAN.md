# API Load Tester + AI Website Analyzer - SaaS Build Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  Dashboard | Tests | AI Analyzer | History | Profile | Pricing│
└────────────────────────┬────────────────────────────────────┘
                         │ (REST + WebSocket)
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Production)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Auth (JWT)   │  │Subscription  │  │ Load Test    │       │
│  │ & Users      │  │ & Payments   │  │ Engine       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ AI Analyzer  │  │ Metrics/DB   │  │ WebSocket    │       │
│  │ (Grock)      │  │ Storage      │  │ Real-time    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────┐  ┌────────▼──────┐  ┌────▼─────────┐
│  MongoDB   │  │  Worker Queue │  │ Background   │
│  (Tests,   │  │  (Async)      │  │ Tasks        │
│  Metrics)  │  │               │  │              │
└────────────┘  └───────────────┘  └──────────────┘
```

## Data Models

**User**
- id, email, password_hash, name
- plan (free/pro), created_at, plan_expires

**Subscription**
- user_id, plan_type, daily_limit
- tests_used_today, last_reset

**Test**
- id, user_id, name, urls, status
- concurrency, duration, metrics[], created_at

**Metrics**
- test_id, rps, latency_avg, latency_p95, success_rate, timestamp

**AIAnalysis**
- id, url, tech_stack, emails, social_links, grock_summary

## Implementation Phases

✅ Phase 1: Backend Models + Auth (JWT)
✅ Phase 2: Subscription System + Dummy Payment
✅ Phase 3: Load Testing with Plan Limits
✅ Phase 4: AI Analyzer + WebSocket
✅ Phase 5: Complete React Frontend
✅ Phase 6: Integration + Setup Docs
✅ Phase 7: Docker + Deployment

## Key Features

- Free Plan: 2 tests/day, 10 concurrency max
- Pro Plan: unlimited tests, 1000 concurrency
- Real-time metrics dashboard
- AI website analyzer
- CSV/JSON export
- User authentication with JWT
- Dummy payment for Pro upgrade (replaceable with Stripe)

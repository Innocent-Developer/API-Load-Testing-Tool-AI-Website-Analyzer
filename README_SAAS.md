# LoadTester Pro - API Load Testing & Website Analyzer SaaS Platform

**Production-ready SaaS platform** for API load testing and website analysis with JWT authentication, subscription plans, payments, and AI-powered website analysis.

## Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with 24-hour expiration
- **Bcrypt password hashing** via passlib
- Sign up, login, token refresh endpoints
- Protected API endpoints with Authorization header validation

### 💳 Subscription & Billing
- **Freemium model**: Free tier and Pro tier
- **Plan enforcement** on every test creation
- **Dummy payment system** with transaction tracking
- Upgrade endpoints for plan transitions

### 📊 Load Testing
- **Create custom load tests** with multiple URLs
- **Real-time WebSocket metrics** streaming
- **Per-second metrics** collection and storage
- **PDF/JSON export** based on plan

### 🤖 AI Website Analyzer
- **Analyze any website** with Grock API (mock integration)
- **Tech stack detection** (React, Next.js, frameworks)
- **SEO scoring** and performance metrics
- **Extract contact emails** and social links
- **AI-generated summaries** of website capabilities

### 📈 Dashboard
- User statistics and usage tracking
- Recent tests overview
- Plan information and remaining limits
- Test creation and management interface

---

## Architecture

### Backend Structure
```
backend/
├── main_saas.py           # FastAPI app entry point
├── config.py              # Configuration management
├── models_saas.py         # Pydantic models (300+ lines)
├── auth_service.py        # JWT & password management
├── auth_endpoints.py      # Auth routes (signup/login/profile)
├── payment_endpoints.py   # Payment & upgrade routes
├── payment_service.py     # Dummy payment processor
├── subscription_service.py # Plan enforcement logic
├── test_endpoints.py      # Load test management
├── ai_endpoints.py        # Website analyzer
├── database_saas.py       # MongoDB CRUD operations
└── requirements.txt       # Python dependencies
```

### Frontend Structure
```
frontend/src/
├── pages/
│   ├── Login.jsx          # Authentication
│   ├── Signup.jsx         # User registration
│   ├── Dashboard.jsx      # Main dashboard
│   ├── Profile.jsx        # User profile & plan
│   ├── Pricing.jsx        # Plan comparison
│   ├── AIAnalyzer.jsx     # Website analyzer
│   ├── CreateTest.jsx     # Test creation
│   ├── TestDetail.jsx     # Test results
│   └── TestHistory.jsx    # Test history
├── services/
│   ├── api.js             # API client with JWT interceptors
│   └── auth.js            # Auth utilities
├── App.jsx                # Main app with routing
└── App.css                # Styling
```

---

## API Endpoints

### Authentication
```
POST   /api/auth/signup        - Create account
POST   /api/auth/login         - Login
POST   /api/auth/refresh       - Refresh token
GET    /api/auth/profile       - Get profile (protected)
```

### Tests
```
POST   /api/tests              - Create test (subscription-enforced)
GET    /api/tests              - List tests (paginated)
GET    /api/tests/{id}         - Get test details
DELETE /api/tests/{id}         - Delete test
GET    /api/tests/stats/user   - User statistics
WS     /ws/tests/{id}          - WebSocket metrics streaming
```

### AI Analyzer
```
POST   /api/ai/analyze         - Analyze website
GET    /api/ai/analyses        - List analyses
GET    /api/ai/analyses/{id}   - Get analysis details
```

### Payments
```
POST   /api/payment/upgrade    - Upgrade plan (dummy)
GET    /api/payment/pricing    - Get pricing info
GET    /api/payment/transactions - Get user transactions
GET    /api/payment/transactions/{id} - Transaction details
```

---

## Subscription Plans

### Free Plan
```
├─ Daily Tests: 2
├─ Max Concurrency: 10
├─ Export Formats: JSON only
├─ AI Analyzer: ✗
└─ Support: Community
```

### Pro Plan
```
├─ Daily Tests: Unlimited
├─ Max Concurrency: 1000
├─ Export Formats: JSON, CSV, XML, HTML
├─ AI Analyzer: ✓
└─ Support: Priority
```

**Pricing**:
- Monthly: $29.99
- Quarterly: $69.99
- Annual: $199.99

---

## Installation

### Requirements
- Python 3.9+
- Node.js 16+
- MongoDB (local or cloud)

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment** (`.env`):
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DB_NAME=loadtester_pro
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   LOG_LEVEL=INFO
   BACKEND_CALLBACK_URL=http://localhost:8000
   ```

3. **Run backend**:
   ```bash
   python main_saas.py
   ```
   Or with Uvicorn:
   ```bash
   uvicorn main_saas:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment** (`.env.local`):
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

3. **Run frontend**:
   ```bash
   npm run dev
   ```
   Opens at: `http://localhost:5173`

---

## Getting Started

### 1. Create Account
- Visit `http://localhost:5173/signup`
- Enter email, password, and name
- Automatically logged in with JWT token

### 2. Create Load Test
- Go to Dashboard
- Click "Create New Test"
- Add URLs (GET/POST/PUT/DELETE)
- Configure duration, concurrency, ramp-up
- Submit test (respects daily limits)

### 3. View Results
- Tests stream metrics via WebSocket
- View real-time RPS, latency, success rates
- Export results (JSON for Free, more formats for Pro)

### 4. Analyze Website
- Go to "AI Analyzer"
- Enter website URL
- Get instant analysis:
  - Tech stack detection
  - SEO score
  - Performance score
  - Contact emails
  - Social links
  - AI summary

### 5. Upgrade Plan
- Go to "Pricing"
- Select Pro plan and billing cycle
- Use dummy card: `4242 4242 4242 4242`
- Upgrade confirms and updates limits

---

## SaaS Features Implemented

| Feature | Implementation | Status |
|---------|-----------------|---------|
| JWT Auth | 24-hour tokens, Bcrypt hashing | ✅ Complete |
| Subscriptions | Free/Pro tiers, daily limits | ✅ Complete |
| Payment System | Dummy processor, transaction tracking | ✅ Complete |
| Load Testing | Multi-URL, async, metrics streaming | ✅ Complete |
| AI Analysis | Mock Grock integration, tech detection | ✅ Complete |
| Dashboard | Stats, test creation, management | ✅ Complete |
| WebSocket | Real-time metrics streaming | ✅ Complete |
| Database | MongoDB with Motor async driver | ✅ Complete |
| Error Handling | Comprehensive validation & responses | ✅ Complete |
| CORS | Configured for all origins (dev) | ✅ Complete |

---

## Technology Stack

### Backend
- **FastAPI** 0.104.1 - Web framework
- **Pydantic** 2.8.0 - Data validation
- **Motor** 3.3.2 - Async MongoDB driver
- **PyJWT** 2.8.0 - JWT tokens
- **Passlib** - Password hashing
- **Python-jose** - Cryptography

### Frontend
- **React** 18.2 - UI framework
- **Vite** 5.0 - Build tool
- **Axios** - HTTP client
- **Tailwind CSS** 3.3 - Styling
- **React Router** 6 - Routing

### Database
- **MongoDB** - Document database
- **Indexes** on user email, test user/status

---

## Database Schema

### Collections

**users**
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password_hash: String,
  name: String,
  role: "user" | "admin",
  plan: "free" | "pro",
  plan_expires: Date,
  created_at: Date,
  updated_at: Date,
  is_active: Boolean
}
```

**subscriptions**
```javascript
{
  _id: ObjectId,
  user_id: String (unique),
  plan: "free" | "pro",
  tests_used_today: Number,
  last_reset: Date,
  created_at: Date
}
```

**tests**
```javascript
{
  _id: ObjectId,
  user_id: String,
  config: { name, urls[], duration, concurrency, ramp_up },
  status: "pending" | "running" | "completed" | "failed",
  created_at: Date,
  started_at: Date,
  completed_at: Date,
  summary: { total_requests, success_rate, avg_latency, ... },
  per_second_metrics: [ { timestamp, rps, latency_p50, ... } ],
  error_message: String
}
```

**ai_analysis**
```javascript
{
  _id: ObjectId,
  user_id: String,
  url: String,
  tech_stack: String[],
  meta_description: String,
  emails: String[],
  social_links: Object,
  grock_summary: String,
  seo_score: Number,
  performance_score: Number,
  created_at: Date
}
```

---

## Configuration

### Environment Variables
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DB_NAME=loadtester_pro

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256

# Backend
LOG_LEVEL=INFO
BACKEND_CALLBACK_URL=http://localhost:8000

# Logging
LOG_FORMAT=json
```

### Config File (`backend/config.py`)
- Manages all settings
- Validates required env vars
- Provides defaults for development

---

## Security Considerations

### Production Deployment
1. **Generate strong JWT_SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Enable HTTPS**:
   - Reverse proxy (Nginx)
   - SSL certificate (Let's Encrypt)

3. **CORS Configuration**:
   - Restrict to frontend domain
   - Avoid `allow_origins=["*"]`

4. **Payment Integration**:
   - Replace dummy payment with Stripe/Paddle
   - Validate webhook signatures
   - Never log card numbers

5. **Rate Limiting**:
   - Implement on auth endpoints
   - Prevent brute force attacks

6. **Database Security**:
   - Use MongoDB connection string with auth
   - Enable IP whitelisting
   - Regular backups

---

## Testing

### Manual API Testing
```bash
# 1. Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# 2. Create test (with returned token)
curl -X POST http://localhost:8000/api/tests \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Homepage Test",
    "urls": [{"url": "https://example.com", "method": "GET"}],
    "duration": 60,
    "concurrency": 10
  }'

# 3. Upgrade plan
curl -X POST http://localhost:8000/api/payment/upgrade \
  -H "Authorization: Bearer {token}" \
  -d "plan=pro&billing_period=monthly&card_token=4242..."
```

### Frontend Testing
- Create account at `/signup`
- Create test in Dashboard
- View analysis in AI Analyzer
- Upgrade plan at Pricing

---

## Deployment

### Docker Deployment
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main_saas:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
services:
  mongodb:
    image: mongo:latest
    ports: ["27017:27017"]
    volumes: ["mongo-data:/data/db"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      MONGODB_URL: mongodb://mongodb:27017
    depends_on: [mongodb]
  
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    environment:
      VITE_API_URL: http://backend:8000
```

### Vercel/Netlify (Frontend)
```bash
# frontend/vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
```

---

## Performance Optimizations

- **Database Indexes**: Email unique, test user/status
- **Async Processing**: Motor for non-blocking DB ops
- **Connection Pooling**: Reuse MongoDB connections
- **WebSocket**: Real-time updates, reduces polling
- **JWT Caching**: No DB lookup after decode
- **Tailwind CSS**: PurgeCSS in production

---

## Roadmap

| Phase | Feature | Timeline |
|-------|---------|----------|
| ✅ Phase 1 | Core auth, tests, payments | Complete |
| 🔄 Phase 2 | Real Grock integration, advanced AI | Q2 2024 |
| 🔄 Phase 3 | Team collaboration, shared tests | Q3 2024 |
| 🔄 Phase 4 | Advanced scheduling, CI/CD integration | Q4 2024 |
| 🔄 Phase 5 | Mobile app, native push notifications | 2025 |

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **GitHub Issues**: [Create issue]
- **Email Support**: support@loadtesterpro.com

---

## License

MIT License - See LICENSE file

---

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**© 2024 LoadTester Pro. All rights reserved.**

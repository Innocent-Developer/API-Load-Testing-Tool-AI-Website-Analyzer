# LoadTester Pro - Quick Start Guide

## 🚀 Start in 5 Minutes

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB running (local or cloud)

---

## Step 1: Backend Setup (2 min)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
MONGODB_URL=mongodb://localhost:27017
DB_NAME=loadtester_pro
JWT_SECRET_KEY=dev-secret-key-change-in-production
LOG_LEVEL=INFO
BACKEND_CALLBACK_URL=http://localhost:8000
EOF

# Start backend
python main_saas.py
```

✅ Backend running at: `http://localhost:8000`
📚 API docs at: `http://localhost:8000/docs`

---

## Step 2: Frontend Setup (2 min)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF

# Start frontend
npm run dev
```

✅ Frontend running at: `http://localhost:5173`

---

## Step 3: Try It Out! (1 min)

### 1. Sign Up
- Go to `http://localhost:5173/signup`
- Create account: `test@example.com` / `password123`
- Auto-redirected to dashboard

### 2. Create Your First Test
- Dashboard → "Create New Test"
- Name: "My First Test"
- URL: `https://httpbin.org/get`
- Duration: 30 seconds
- Concurrency: 5
- Click "Create Test"

### 3. View Results
- Wait for test to complete
- Click "View" to see metrics
- Watch real-time WebSocket updates

### 4. Try AI Analyzer
- Click "AI Analyzer" in nav
- Enter any URL: `https://github.com`
- See instant analysis: tech stack, SEO score, emails, social links

### 5. Check Pricing
- Click "Pricing" to see plans
- Free: 2 tests/day, 10 users
- Pro: Unlimited tests, 1000 users
- (Demo payment with card `4242 4242 4242 4242`)

---

## Architecture Overview

```
LoadTester Pro
├── Frontend (React + Vite)
│   ├── Login/Signup
│   ├── Dashboard (create tests, stats)
│   ├── AI Analyzer (website analysis)
│   ├── Pricing (upgrade plans)
│   └── Profile (account settings)
│
├── Backend (FastAPI)
│   ├── Auth Service (JWT + Bcrypt)
│   ├── Subscription Service (plan enforcement)
│   ├── Test Engine (async load testing)
│   ├── Payment Service (dummy processor)
│   ├── AI Analyzer (tech detection)
│   └── WebSocket (real-time metrics)
│
└── Database (MongoDB)
    ├── Users (auth)
    ├── Subscriptions (plan limits)
    ├── Tests (results)
    ├── AI Analyses (website data)
    └── Transactions (payments)
```

---

##  Key Features

| Feature | How to Use |
|---------|-----------|
| 🔐 **JWT Auth** | Sign up/login → token stored in localStorage |
| 📊 **Load Tests** | Dashboard → Create test → WebSocket updates |
| 🤖 **AI Analyzer** | Click "AI Analyzer" → Enter URL → Get analysis |
| 💳 **Subscriptions** | Free tier default, upgrade at Pricing page |
| 💰 **Payments** | Demo: use card `4242 4242 4242 4242` |
| 📈 **Stats** | Dashboard shows tests, limits, remaining quota |

---

## API Endpoints Quick Reference

### Auth (No token needed)
```
POST   /api/auth/signup
POST   /api/auth/login
```

### Auth (Token required in `Authorization: Bearer {token}`)
```
GET    /api/auth/profile
POST   /api/auth/refresh
POST   /api/tests
GET    /api/tests
GET    /api/tests/{id}
DELETE /api/tests/{id}
GET    /api/tests/stats/user
POST   /api/ai/analyze
GET    /api/ai/analyses
GET    /api/payment/pricing
POST   /api/payment/upgrade
```

### WebSocket
```
WS     /ws/tests/{test_id}
```

---

## Database Setup

### MongoDB Local
```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Linux
sudo apt-get install mongodb

# Start with connection string
mongod
```

### MongoDB Cloud (Optional)
1. Create cluster at mongodb.com/cloud
2. Get connection string
3. Update `.env`:
   ```env
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
   ```

---

## Troubleshooting

### Backend won't start
```bash
# Check MongoDB is running
mongosh  # try to connect

# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt

# Check port 8000 isn't in use
lsof -i :8000
```

### Frontend not connecting to backend
```bash
# Check VITE_API_URL in .env.local
cat frontend/.env.local

# Test API endpoint
curl http://localhost:8000/health

# Clear browser cache (Ctrl+Shift+Del) and reload
```

### Tests not saving
```bash
# Check MongoDB is running and accessible
mongosh -u admin -p password

# Verify MONGODB_URL in backend/.env
echo $MONGODB_URL
```

---

## Next Steps

### To Customize:

1. **Change JWT Secret**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # Copy output to .env JWT_SECRET_KEY
   ```

2. **Add Real Payment Processing**:
   - Replace `payment_service.py` with Stripe integration
   - Update `payment_endpoints.py` to validate real payments

3. **Integrate Real Grock API**:
   - Get Grock API key
   - Replace `analyze_website()` in `ai_endpoints.py`
   - Make real HTTP calls instead of mock

4. **Deploy to Production**:
   - Use Docker: `docker-compose up`
   - Deploy backend to Heroku/Railway
   - Deploy frontend to Vercel/Netlify
   - Use production MongoDB (Atlas)

---

## File Structure

```
api loadtesting/
├── backend/
│   ├── main_saas.py              ← Start here! Main app
│   ├── auth_endpoints.py          ← Auth routes
│   ├── test_endpoints.py          ← Test creation/management
│   ├── payment_endpoints.py       ← Payment/upgrade routes
│   ├── ai_endpoints.py            ← Website analyzer
│   ├── auth_service.py            ← JWT & password logic
│   ├── subscription_service.py    ← Plan enforcement
│   ├── payment_service.py         ← Dummy payment processor
│   ├── database_saas.py           ← MongoDB operations
│   ├── models_saas.py             ← Pydantic models
│   ├── config.py                  ← Configuration
│   └── requirements.txt           ← Python packages
│
└── frontend/
    ├── src/
    │   ├── App.jsx                ← Main app with routing
    │   ├── pages/
    │   │   ├── Login.jsx          ← Auth page
    │   │   ├── Signup.jsx         ← Registration
    │   │   ├── Dashboard.jsx      ← Main dashboard
    │   │   ├── Profile.jsx        ← User profile
    │   │   ├── Pricing.jsx        ← Plan comparison
    │   │   ├── AIAnalyzer.jsx     ← Website analyzer
    │   │   └── TestDetail.jsx     ← Test results
    │   ├── services/
    │   │   └── api.js             ← API client with JWT
    │   └── App.css                ← Tailwind styles
    └── package.json
```

---

## Performance Tips

1. **Database Indexing**: Automatically created on startup ✓
2. **JWT Caching**: No DB lookup after decode ✓
3. **WebSocket**: Real-time updates, no polling
4. **Async Operations**: Motor for all DB queries
5. **Lazy Loading**: React routes code-split

---

## Example Workflows

### Workflow 1: Free User Testing
1. Sign up → Free plan automatically assigned
2. Create max 2 tests/day
3. Try running test at `https://httpbin.org/get`
4. Export as JSON only

### Workflow 2: Upgrade & Premium Testing
1. Sign up & create 2 tests (hits daily limit)
2. Go to Pricing, click "Upgrade to Pro"
3. Select monthly ($29.99)
4. Use fake card: `4242 4242 4242 4242`
5. Now unlimited tests, 1000 concurrent users, multiple export formats

### Workflow 3: Website Analysis
1. Go to "AI Analyzer" tab
2. Enter any URL: `https://stripe.com`
3. Get instant analysis:
   - ✅ Tech stack: React, Next.js, Stripe.js
   - ✅ SEO: 92%
   - ✅ Performance: 88%
   - ✅ Emails: hello@stripe.com
   - ✅ Social: Twitter, LinkedIn, GitHub

---

## Commands Cheat Sheet

```bash
# Backend
cd backend
pip install -r requirements.txt        # Install deps
python main_saas.py                    # Start server
uvicorn main_saas:app --reload         # Alt: with auto-reload

# Frontend
cd frontend
npm install                            # Install deps
npm run dev                            # Start dev server
npm run build                          # Build for production
npm run preview                        # Preview build

# MongoDB (if local)
mongod                                 # Start server
mongosh                                # Connect to db
```

---

## Support

- 📖 Full docs: [README_SAAS.md](README_SAAS.md)
- 🐛 Issues: Check backend logs in terminal
- 💬 API tests: Visit http://localhost:8000/docs for Swagger UI

---

**Ready to test? Let's go! 🚀**

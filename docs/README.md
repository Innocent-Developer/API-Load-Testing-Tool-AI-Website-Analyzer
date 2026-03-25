# API Testing Tool + AI Website Analyzer

A **production-ready, full-stack API load testing platform** combining the power of k6, Postman, and basic AI analysis.

## 🎯 Features

### Load Testing Engine
- ✅ **Async Load Testing** with asyncio + aiohttp
- ✅ **Multi-URL Support** with weighted traffic distribution  
- ✅ **Configurable Concurrency** (1-1000+ VUs)
- ✅ **Ramp-up Traffic** for gradual load increase
- ✅ **Real-time Per-Second Metrics** (RPS, latency percentiles)
- ✅ **Advanced Latency Tracking** (min, avg, p50, p95, p99, max)
- ✅ **Automatic Retry Mechanism** with exponential backoff
- ✅ **Timeout Handling** per request
- ✅ **CSV + JSON Export** of results

### Backend API
- ✅ **FastAPI** with async support
- ✅ **MongoDB** for data persistence
- ✅ **WebSocket Support** for real-time test updates
- ✅ **JWT Authentication** ready
- ✅ **Queue System** for managing tests
- ✅ **Per-second Metrics Storage** in database

### Frontend Dashboard
- ✅ **React 18** with Vite
- ✅ **Tailwind CSS** for styling
- ✅ **Dark Mode** support
- ✅ **Live Charts** (RPS, Latency, Success Rate)
- ✅ **Recharts** for data visualization
- ✅ **Responsive Design** (mobile-friendly)
- ✅ **Real-time Updates** via Socket.IO/WebSocket

### AI Website Analyzer
- ✅ **Tech Stack Detection** (React, Vue, Angular, Next.js, etc.)
- ✅ **SEO Analysis** (meta tags, title, description)
- ✅ **Performance Hints** (compression, caching, CDN)
- ✅ **Email Extraction** from website HTML
- ✅ **Social Media Links** detection
- ✅ **AI Summary Generation** of website purpose

## 📦 Project Structure

```
api-loadtesting/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app with routes
│   ├── models.py           # Pydantic models
│   ├── database.py         # MongoDB operations
│   ├── config.py           # Configuration
│   ├── worker_client.py    # Worker communication
│   ├── requirements.txt    # Dependencies
│   └── .env.example        # Environment template
│
├── worker/                 # Python load testing worker
│   ├── main.py            # FastAPI worker service
│   ├── load_test_engine.py # Core load testing logic
│   ├── website_analyzer.py # AI website analyzer
│   ├── config.py          # Worker config
│   ├── requirements.txt   # Dependencies
│   └── .env.example       # Environment template
│
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── pages/         # React pages (Dashboard, CreateTest, etc.)
│   │   ├── services/      # API client
│   │   ├── App.jsx        # Main app component
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Tailwind styles
│   ├── index.html         # HTML template
│   ├── tailwind.config.js # Tailwind config
│   ├── vite.config.js     # Vite config
│   ├── package.json       # Dependencies
│   └── postcss.config.js  # PostCSS config
│
├── docs/                  # Documentation
└── docker-compose.yml     # Docker setup (optional)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB 4.0+
- Git

### Step 1: Clone & Setup

```bash
cd "api loadtesting"
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env

# Start MongoDB (using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Run backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend running at: `http://localhost:8000`

### Step 3: Worker Setup

```bash
# Open new terminal, navigate to worker
cd worker

# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env template
cp .env.example .env

# Run worker
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Worker running at: `http://localhost:8001`

### Step 4: Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend running at: `http://localhost:5173`

## 📊 Usage Guide

### Creating a Load Test

1. **Navigate** to "New Test" page
2. **Enter** test name and description
3. **Add URLs** to test (support for GET, POST, PUT, DELETE, PATCH)
4. **Configure Settings**:
   - Duration (10-3600 seconds)
   - Concurrency (1-1000 users)
   - Ramp-up time (gradual user increase)
   - Retry count (0-5 retries)
   - Think time (delay between requests)
5. **Click** "Create & Start Test"

### Viewing Results

- **Real-time Dashboard**: Watch metrics update live
- **Charts**: View RPS, latency trends, and success rate
- **Detailed Metrics**: Per-second breakdown
- **Export**: Download results as JSON

### Performance Metrics Explained

- **RPS**: Requests Per Second
- **Latency**: Time to receive response
  - **p50**: 50th percentile (median)
  - **p95**: 95th percentile (95% of requests faster than this)
  - **p99**: 99th percentile (99% faster)
- **Success Rate**: Percentage of successful requests
- **Error Distribution**: Types and counts of failures

## 🔌 API Endpoints

### Test Management

```
POST   /api/tests              # Create new test
GET    /api/tests              # List all tests (paginated)
GET    /api/tests/{id}         # Get test details
POST   /api/tests/{id}/stop    # Stop running test
DELETE /api/tests/{id}         # Delete test

# Real-time
WS     /ws/tests/{id}          # WebSocket for live updates

# Internal (Worker → Backend)
POST   /api/tests/{id}/metrics # Send per-second metrics
POST   /api/tests/{id}/complete # Report test completion
```

## ⚙️ Configuration

### Backend `.env`

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=api_loadtesting
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
LOG_LEVEL=INFO
WORKER_HOST=http://localhost:8001
FRONTEND_URL=http://localhost:5173
```

### Worker `.env`

```env
WORKER_HOST=0.0.0.0
WORKER_PORT=8001
BACKEND_URL=http://localhost:8000
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 🐳 Docker Setup (Optional)

```bash
# Build and run all services
docker-compose up -d

# Services:
# - Backend: http://localhost:8000
# - Worker: http://localhost:8001  
# - Frontend: http://localhost:5173
# - MongoDB: localhost:27017
```

## 🔒 Security Considerations

- ✅ CORS configured
- ✅ Input validation (Pydantic models)
- ✅ Error handling and logging
- ✅ Environment variable configuration
- ⚠️ **For production**: 
  - Use strong SECRET_KEY
  - Implement JWT authentication
  - Add rate limiting
  - Use HTTPS
  - Configure CORS properly
  - Set up proper MongoDB authentication

## 📈 Load Testing Best Practices

1. **Start Small**: Begin with low concurrency and ramp up
2. **Monitor**: Watch for resource limits on test machine
3. **Realistic Scenarios**: Use weighted URLs to simulate real traffic
4. **Multiple URLs**: Test different endpoints
5. **Think Time**: Add realistic delays between requests
6. **Long Tests**: For production, run tests for 5-30 minutes minimum

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Start MongoDB
docker run -d -p 27017:27017 mongo:latest

# Or if already running
docker start mongodb
```

### Worker Not Connecting
- Ensure worker is running: `http://localhost:8001/health`
- Check `WORKER_HOST` in backend `.env`
- Check network connectivity between services

### WebSocket Connection Issues
- Check browser console for errors
- Ensure WebSocket proxy is configured in Vite
- Test with `http://localhost:8000/health`

### High Memory Usage
- Reduce concurrency
- Reduce test duration
- Check for resource leaks in worker logs

## 💻 Technology Stack

**Backend**
- FastAPI
- Motor (async MongoDB driver)
- PyDantic
- Uvicorn

**Worker**
- Asyncio
- Aiohttp
- BeautifulSoup4

**Frontend**
- React 18
- Vite
- Tailwind CSS
- Recharts
- Axios

**Database**
- MongoDB

**DevOps**
- Docker & Docker Compose
- Python virtual environments

## 📝 Example API Usage

### Create a Load Test

```bash
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Stress Test",
    "description": "Weekly stress test",
    "urls": [
      {
        "url": "https://api.example.com/users",
        "method": "GET",
        "weight": 0.7,
        "timeout": 10
      },
      {
        "url": "https://api.example.com/posts",
        "method": "GET", 
        "weight": 0.3,
        "timeout": 10
      }
    ],
    "duration": 300,
    "concurrency": 50,
    "ramp_up": 30,
    "retry_count": 2
  }'
```

### Get Test Results

```bash
curl http://localhost:8000/api/tests/{test_id}
```

## 📚 Advanced Features

### Weighted URL Distribution
URLs with different weights to simulate realistic distribution:
- 70% requests to main API
- 30% to secondary service

### Per-Second Metrics
Detailed per-second breakdown of:
- Requests sent/succeeded/failed
- RPS, latency percentiles
- Error distribution

### Real-time WebSocket Updates
Frontend receives live metrics as test progresses without polling.

### Exponential Backoff Retry Logic
Automatic retries with increasing delays for transient failures.

## 🤝 Contributing

To extend the platform:

1. **Add new test types**: Extend `load_test_engine.py`
2. **Custom metrics**: Add to `PerSecondMetrics` class
3. **Additional analyzers**: Extend `website_analyzer.py`
4. **Frontend features**: Add new React pages

## 📄 License

MIT License - See LICENSE file

## 🎓 Learning Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- Async Python: https://docs.python.org/3/library/asyncio.html
- React Documentation: https://react.dev/
- MongoDB: https://docs.mongodb.com/
- Tailwind CSS: https://tailwindcss.com/

---

**Built with ❤️ for production-grade load testing**

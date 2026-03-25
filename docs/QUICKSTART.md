# 🚀 Quick Start Guide

Get **LoadTester** running in 15 minutes!

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB 4.0+ (or use Docker)
- ~2GB disk space

## ⚡ Option 1: Docker (Easiest)

```bash
# From project root
docker-compose up -d

# Services start automatically:
# - Backend: http://localhost:8000
# - Worker: http://localhost:8001
# - Frontend: http://localhost:5173
# - MongoDB: localhost:27017
```

All services will be ready in ~30 seconds!

## 🛠️ Option 2: Manual Setup (3 Terminal Windows)

### Terminal 1: Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name loadtesting-mongo mongo:latest

# Or if using local installation
mongod
```

### Terminal 2: Start Backend

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Install & run
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend ready at: **http://localhost:8000**

### Terminal 3: Start Worker

```bash
cd worker

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Install & run
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

✅ Worker ready at: **http://localhost:8001**

### Terminal 4: Start Frontend

```bash
cd frontend

npm install
npm run dev
```

✅ Frontend ready at: **http://localhost:5173**

## 🎬 First Test

1. **Open** http://localhost:5173 in your browser
2. **Click** "New Test" button
3. **Enter** test details:
   ```
   Name: "My First Test"
   URL: https://httpbin.org/get
   Duration: 30 seconds
   Concurrency: 5 users
   ```
4. **Click** "Create & Start Test"
5. **Watch** real-time metrics on the dashboard!

## ✅ Verification

### Check All Services Running

```bash
# Backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# Worker health  
curl http://localhost:8001/health
# Expected: {"status":"healthy",...}

# MongoDB
mongosh mongodb://localhost:27017
# Type: db.collection.find()
```

## 📊 Dashboard Features

- **Dashboard**: Overview of all tests
- **New Test**: Create and configure tests
- **History**: View past test results
- **Live View**: Watch metrics as test runs
- **Export**: Download results as JSON

## 🎯 Example Scenarios

### Scenario 1: Simple GET Request
```
URL: https://api.github.com/users
Method: GET
Duration: 60 seconds
Concurrency: 10
```

### Scenario 2: Multiple Endpoints
```
URL 1: https://api.example.com/users (weight: 0.6)
URL 2: https://api.example.com/posts (weight: 0.4)
Duration: 120 seconds
Concurrency: 20
```

### Scenario 3: Ramp-up Test
```
Duration: 300 seconds
Concurrency: 50
Ramp-up: 60 seconds (gradually increase to 50 users)
```

## 🛑 Stopping Services

### Docker
```bash
docker-compose down
```

### Manual
Press `Ctrl+C` in each terminal

## 📚 Next Steps

- 📖 [Backend Setup Details](./BACKEND_SETUP.md)
- 🔧 [Worker Configuration](./WORKER_SETUP.md)
- 🎨 [Frontend Customization](./FRONTEND_SETUP.md)
- 📖 [Full Documentation](./README.md)

## 🐛 Common Issues

### "Cannot connect to MongoDB"
```bash
# Start MongoDB
docker run -d -p 27017:27017 mongo:latest
```

### "Worker failed to connect"
- Ensure worker is running on port 8001
- Check backend `.env`: `WORKER_HOST=http://localhost:8001`

### "WebSocket connection failed"
- Check browser DevTools console
- Ensure backend is running
- Refresh the page

### Port already in use
```bash
# Kill process using port (e.g., 8000)
lsof -i :8000
kill -9 <pid>

# Or use different port
uvicorn main:app --port 8001
```

## 🎓 Learning the System

1. **Create** → Browse to New Test
2. **Configure** → Set URLs, duration, concurrency
3. **Execute** → Watch in real-time
4. **Analyze** → View results and charts
5. **Export** → Download data for further analysis

## 💡 Tips

- Start with **short tests** (30-60 seconds) to learn
- Use **realistic** URLs and workloads
- Monitor **your machine** resources during testing
- Check **logs** for debugging: search for `ERROR` or `WARNING`
- Use **dark mode** for easier eye strain 👀

## 📞 Support

- 🐛 Check [Troubleshooting](./README.md#-troubleshooting) section
- 📖 Review [Backend Setup](./BACKEND_SETUP.md)
- 🔧 Review [Worker Setup](./WORKER_SETUP.md)
- 🎨 Review [Frontend Setup](./FRONTEND_SETUP.md)

## ✨ You're Ready!

Congratulations! You now have a complete API load testing platform running locally.

**Start building awesome tests! 🚀**

---

**Questions?** Check the [full README](./README.md) for comprehensive documentation.

# Backend Setup Guide

## Prerequisites

- Python 3.9+
- MongoDB 4.0+ (local or Docker)
- pip or poetry

## Installation

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your editor
```

**Important variables:**
- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT secret (change in production)
- `WORKER_HOST`: Where the worker service runs
- `FRONTEND_URL`: Frontend origin for CORS

### 5. Start MongoDB

**Option A: Docker**
```bash
docker run -d -p 27017:27017 --name loadtesting-mongo mongo:latest
```

**Option B: Local Installation**
```bash
# macOS with Homebrew
brew services start mongodb-community

# Ubuntu/Debian
sudo systemctl start mongod
```

### 6. Run Backend Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00.000","environment":"development"}
```

## API Documentation

Once running, visit:
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Initialization

Database collections are created automatically on first request.

To verify MongoDB connection:
```bash
mongosh mongodb://localhost:27017/api_loadtesting
```

Then check collections:
```javascript
db.collection.find()
db.tests.findOne()
```

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # Pydantic data models
├── database.py          # MongoDB operations
├── config.py            # Configuration management
├── worker_client.py     # Worker communication
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── Dockerfile           # Docker image definition
```

## Key Files Explained

### `main.py`
- FastAPI application setup
- Route definitions (/api/tests, WebSocket /ws/tests)
- Request/response handling
- WebSocket connection management

### `models.py`
- Pydantic data models
- Test configuration schema
- Result schema
- Request/response schemas

### `database.py`
- MongoDB connection management
- CRUD operations
- Index creation
- Async helpers

### `config.py`
- Environment variable loading
- Settings management
- Default values

### `worker_client.py`
- Communication with Python worker
- Test submission logic
- Retry mechanism

## API Endpoints

### Test Management
```
POST   /api/tests              # Create new test
GET    /api/tests              # List tests (pagination)
GET    /api/tests/{id}         # Get test details
POST   /api/tests/{id}/stop    # Stop running test
DELETE /api/tests/{id}         # Delete test
```

### Real-time
```
WS     /ws/tests/{id}          # WebSocket connection
```

### Internal (Worker)
```
POST   /api/tests/{id}/metrics # Send metrics
POST   /api/tests/{id}/complete # Test completion
```

## Testing

### Create a Test
```bash
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test API",
    "urls": [
      {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "weight": 1.0,
        "timeout": 10
      }
    ],
    "duration": 30,
    "concurrency": 5,
    "ramp_up": 5
  }'
```

### List Tests
```bash
curl http://localhost:8000/api/tests?page=1&page_size=20
```

### Get Test Details
```bash
curl http://localhost:8000/api/tests/{test_id}
```

## Troubleshooting

### MongoDB Connection Failed
```
Error: Could not connect to MongoDB
```

**Solution:**
1. Ensure MongoDB is running: `docker ps | grep mongo`
2. Check connection string in `.env`
3. Verify network: `telnet localhost 27017`

### Worker Connection Failed
```
Error: Failed to connect to worker
```

**Solution:**
1. Start worker service on port 8001
2. Update `WORKER_HOST` in `.env` if worker is on different host
3. Check network connectivity

### CORS Errors in Frontend
```
Access-Control-Allow-Origin error
```

**Solution:**
1. Check `FRONTEND_URL` in `.env`
2. Ensure URL matches frontend origin exactly
3. Update CORS middleware in `main.py`

### Port Already in Use
```
Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <pid>

# Or use different port
uvicorn main:app --port 8001
```

## Performance Tips

1. **Connection Pooling**: MongoDB driver handles this automatically
2. **Worker Scaling**: Run multiple worker instances
3. **Async Operations**: All I/O is async by default
4. **Logging**: Reduce log level to WARNING in production
5. **Database Indexes**: Already created in `database.py`

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS (configure in reverse proxy)
- [ ] Set `FRONTEND_URL` correctly
- [ ] Implement rate limiting
- [ ] Use database authentication

### Example Production Configuration
```bash
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export WORKER_HOST=https://worker.internal.example.com
```

### Running with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Monitoring

### Check Server Health
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Docker
docker logs loadtesting-backend

# Direct
# Logs output to console
```

### Database Monitoring
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/api_loadtesting

# Check collections
db.tests.count()
db.tests.find().limit(1).pretty()
```

## Next Steps

1. ✅ Start the backend
2. ⏭️  [Frontend Setup](../frontend/SETUP.md)
3. ⏭️  [Worker Setup](../worker/SETUP.md)
4. ⏭️  [Run the application](../docs/QUICKSTART.md)

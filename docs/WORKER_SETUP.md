# Worker Setup Guide

## What is the Worker?

The Worker is a Python service that:
- Executes load tests asynchronously
- Manages virtual users and concurrent connections
- Collects per-second metrics
- Sends real-time updates to the backend
- Handles retry logic and error tracking

## Prerequisites

- Python 3.9+
- Working Backend service (http://localhost:8000)
- pip

## Installation

### 1. Navigate to Worker Directory

```bash
cd worker
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
nano .env
```

**Key variables:**
- `WORKER_HOST`: Interface to bind to (0.0.0.0 for all interfaces)
- `WORKER_PORT`: Port worker listens on (default 8001)
- `BACKEND_URL`: Where the backend service runs
- `ENVIRONMENT`: development or production

### 5. Run Worker Service

```bash
# Development mode (with auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2
```

### 6. Verify Installation

```bash
# Check worker health
curl http://localhost:8001/health

# Expected response:
# {"status":"healthy","timestamp":"...","active_tests":0}
```

## Project Structure

```
worker/
├── main.py                  # FastAPI worker service
├── load_test_engine.py      # Core async load testing logic
├── website_analyzer.py      # AI website analyzer
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── Dockerfile               # Docker image
```

## Core Components

### `load_test_engine.py`

The heart of load testing. Key classes:

**`LoadTestEngine`**
- Orchestrates concurrent load testing
- Manages virtual users
- Collects metrics
- Handles retries and timeouts

**`PerSecondMetrics`**
- Per-second statistics
- RPS, latency percentiles
- Error tracking

**`TestResult`**
- Final test summary
- Aggregate statistics
- Error distribution

**Key Features:**
- Async/await for concurrency
- Configurable concurrency (VUs)
- Ramp-up support
- Weighted URL distribution
- Exponential backoff retries
- Percentile calculations (p50, p95, p99)

### `website_analyzer.py`

Analyzes websites for:
- Tech stack detection
- SEO metrics
- Performance hints
- Email/social extraction
- AI-generated summary

### `main.py`

FastAPI service with endpoints:
- `POST /execute` - Execute load test
- `GET /health` - Health check
- `Background executor loop` - Queue processor

## How It Works

```
Backend sends test job
        ↓
Worker queue
        ↓
Test executor processes
        ↓
LoadTestEngine runs VUs
        ↓
Per-second metrics collected
        ↓
Metrics sent back to backend
        ↓
Test completion callback
```

## API Endpoints

### Worker API

```
GET  /health        # Health check
POST /execute       # Execute test
```

### Execute Test
```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "507f1f77bcf86cd799439011",
    "config": {
      "urls": [...],
      "duration": 60,
      "concurrency": 10,
      ...
    },
    "callback_url": "http://backend:8000/api/tests/507f1f77bcf86cd799439011"
  }'
```

## Load Testing Details

### Virtual User (VU) Model
- Each VU runs independently
- Makes requests in sequence with think time
- Respects ramp-up timing
- Continues until test duration ends

### Concurrency Handling
- Uses `aiohttp` with async connections
- Single event loop for all VUs
- Connection pooling for efficiency
- Configurable max connections

### Metrics Collection

Per-second breakdown:
- Requests sent/succeeded/failed
- RPS (Requests Per Second)
- Min/max latency
- Percentiles: p50, p95, p99
- Error types and counts

### Retry Logic
- Configurable retry count
- Exponential backoff: 0.1s, 0.2s, 0.4s, etc.
- Retries on timeout and connection errors
- Failed requests after retries counted as failures

### Weighted URL Distribution
```python
# Example: 70% to API, 30% to docs
urls = [
    {"url": "https://api.example.com/", "weight": 0.7},
    {"url": "https://docs.example.com/", "weight": 0.3}
]
```

The engine selects URLs based on cumulative weight probability.

## Configuration Options

### Test Configuration

```json
{
  "name": "Test Name",
  "description": "Optional description",
  "urls": [
    {
      "url": "https://api.example.com/endpoint",
      "method": "GET",
      "weight": 1.0,
      "timeout": 10,
      "headers": {"Authorization": "Bearer token"},
      "body": null
    }
  ],
  "duration": 60,           # seconds
  "concurrency": 10,        # virtual users
  "ramp_up": 10,           # seconds to reach full concurrency
  "retry_count": 1,        # retries per request
  "think_time": 0          # seconds between requests
}
```

## Example Scenarios

### Simple API Endpoint
```python
{
  "urls": [
    {"url": "https://api.github.com/users", "method": "GET"}
  ],
  "duration": 60,
  "concurrency": 20
}
```

### Multiple Endpoints
```python
{
  "urls": [
    {"url": "https://api.example.com/users", "method": "GET", "weight": 0.5},
    {"url": "https://api.example.com/posts", "method": "GET", "weight": 0.3},
    {"url": "https://api.example.com/comments", "method": "POST", "weight": 0.2}
  ],
  "duration": 300,
  "concurrency": 50,
  "ramp_up": 30
}
```

### Gradual Ramp-up
```python
{
  "urls": [...],
  "duration": 600,
  "concurrency": 100,
  "ramp_up": 300  # Gradually increase from 0 to 100 VUs over 5 minutes
}
```

## Performance Considerations

### Maximum VUs
- Limited by machine resources (CPU, memory, connections)
- Each VU costs ~1-2KB memory
- Connections pool: `concurrency * 2`
- Typical max: 1000+ on modern machine

### High Concurrency Tips
1. Increase OS file descriptor limit:
   ```bash
   ulimit -n 65536
   ```

2. Monitor worker resource usage
3. Run tests shorter with more VUs than longer with fewer
4. Consider distributed testing (multiple workers)

### Latency Accuracy
- Based on aiohttp request time
- Includes network latency only (not backend processing visible to client)
- Affected by SSL/TLS handshake
- Connection reuse improves consistency

## Troubleshooting

### Worker not connecting to Backend
```
ConnectionError: Failed to connect to backend
```

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `BACKEND_URL` in `.env`
3. Check network connectivity
4. Firewall rules

### High Memory Usage During Test
```
MemoryError or system slowdown
```

**Solution:**
1. Reduce concurrency
2. Reduce test duration
3. Check for resource leaks in logs
4. Monitor: `top` or `htop`

### Requests Timing Out
```
High timeout count in results
```

**Possible Causes:**
1. Target server is slow
2. Network congestion
3. Too many concurrent connections overwhelming target
4. Target rate limiting

**Solution:**
1. Increase `timeout` in URL config
2. Reduce `concurrency`
3. Add `think_time` between requests
4. Check target server logs

### SSL/Certificate Errors
```
ssl.SSLError or certificate verification failed
```

**Solution:**

Worker is configured to skip SSL verification for testing:
```python
ssl=False  # in load_test_engine.py
```

For strict SSL in production, modify `load_test_engine.py`:
```python
async with session.request(..., ssl=True) as response:
```

## Advanced Usage

### Custom Metrics Hook

Extend `load_test_engine.py` to collect custom metrics:

```python
# In LoadTestEngine._make_request()
latency_ms = (time.time() - start) * 1000

# Add to custom metrics
self.custom_metrics.append({
    "url": config.url,
    "latency": latency_ms,
    "status": response.status
})
```

### Distributed Testing

Deploy multiple workers:
```bash
# Worker 1
WORKER_PORT=8001 uvicorn main:app

# Worker 2  
WORKER_PORT=8002 uvicorn main:app

# Backend orchestrates across multiple workers
```

## Monitoring

### Real-time Metrics
Worker sends metrics every second to backend via:
```
POST /api/tests/{id}/metrics
```

### Logs
```bash
# Docker
docker logs loadtesting-worker

# Direct console output with timestamp and level
```

### Health Check
```bash
curl http://localhost:8001/health
# Response: {"status":"healthy","active_tests":1}
```

## Next Steps

1. ✅ Start the worker
2. ⏭️  [Backend Setup](./BACKEND_SETUP.md) (if not done)
3. ⏭️  [Frontend Setup](../frontend/SETUP.md)
4. ⏭️  Run a test!

## References

- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Aiohttp Documentation](https://docs.aiohttp.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

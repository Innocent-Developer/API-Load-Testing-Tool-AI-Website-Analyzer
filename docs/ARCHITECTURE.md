# Architecture & Design

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                      │
│  Dashboard | Create Test | Test Detail | History | Dark Mode    │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTP + WebSocket
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                              │
│  REST API | WebSocket | Manager | Database | Worker Client     │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTP (Queue Jobs)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              Worker (Python Async)                              │
│  Queue Processor | Load Test Engine | Metrics Collection       │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTP (Metrics Update)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MongoDB                                       │
│  Tests Collection | Results | Metrics | Status                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Layer

**Technologies**: React 18, Vite, Tailwind CSS, Recharts

**Responsibilities**:
- User interface
- Test creation form
- Real-time dashboard
- Results visualization
- WebSocket connection management

**State Management**:
- React hooks (useState, useEffect)
- Local component state
- Axios for HTTP requests
- WebSocket for real-time updates

**Key Components**:
```
App
├── Dashboard (Overview & Stats)
├── CreateTest (Form & Configuration)
├── TestDetail (Results & Charts)
└── TestHistory (Test List)
```

### Backend Layer

**Technologies**: FastAPI, Motor (async MongoDB), Pydantic

**Responsibilities**:
- REST API endpoints
- WebSocket connection management
- Request validation
- Test persistence
- Worker orchestration

**Key Features**:
- Async request handling
- CORS support
- Database indexing
- Connection pooling
- Error handling
- Logging

**Endpoints**:
```
POST   /api/tests              → Create test
GET    /api/tests              → List tests
GET    /api/tests/{id}         → Get test detail
POST   /api/tests/{id}/stop    → Stop test
DELETE /api/tests/{id}         → Delete test
WS     /ws/tests/{id}          → Real-time socket
POST   /api/tests/{id}/metrics → Receive metrics
POST   /api/tests/{id}/complete → Test completion
```

### Worker Layer

**Technologies**: Python asyncio, aiohttp, FastAPI

**Responsibilities**:
- Execute load tests
- Manage virtual users
- Collect metrics
- Send results to backend
- Handle errors and retries

**Key Features**:
- Async/concurrent requests
- Per-second metrics collection
- Exponential backoff retry logic
- Weighted URL distribution
- WebFlow to backend

**Process**:
```
Receive Test Job
     ↓
Initialize Load Test Engine
     ↓
Create Virtual Users
     ↓
Execute HTTP Requests
     ↓
Collect Per-Second Metrics
     ↓
Send Metrics to Backend (HTTP)
     ↓
Complete Test & Send Summary
```

### Database Layer

**Technology**: MongoDB

**Collections**:
- `tests`: Test configurations and results
- Indexes on: created_at, status, user_id, worker_id

**Document Schema**:
```javascript
{
  _id: ObjectId,
  config: {
    name: String,
    urls: [URLConfig],
    duration: Number,
    concurrency: Number,
    ...
  },
  status: String,
  created_at: Date,
  started_at: Date,
  completed_at: Date,
  summary: {
    total_requests: Number,
    successful_requests: Number,
    success_rate: Number,
    avg_latency: Number,
    p95_latency: Number,
    p99_latency: Number,
    ...
  },
  per_second_metrics: [PerSecondMetric],
  error_message: String
}
```

## Data Flow

### Creating a Test

```
Frontend
  ├─ User fills form
  ├─ Validates input (client-side)
  ├─ Sends POST /api/tests
  │
Backend
  ├─ Receives request
  ├─ Validates with Pydantic
  ├─ Creates test document in MongoDB
  ├─ Submits test to Worker (background task)
  │
Response
  ├─ Returns test ID immediately
  └─ Status: PENDING
```

### Executing a Test

```
Worker
  ├─ Receives test from queue
  ├─ Changes status to RUNNING
  ├─ Initializes LoadTestEngine
  ├─ Spawns concurrent VU tasks
  ├─ Each VU makes requests
  │
Per-Second
  ├─ Collects metrics every second
  ├─ HTTP POST to backend /api/tests/{id}/metrics
  ├─ Backend broadcasts via WebSocket
  │
Frontend
  ├─ Receives metrics via WebSocket
  ├─ Updates charts in real-time
  └─ Shows live RPS, latency, etc.
```

### Completing a Test

```
Worker
  ├─ Test duration reached
  ├─ All VUs stop
  ├─ Calculates final summary
  ├─ HTTP POST to backend /api/tests/{id}/complete
  │
Backend
  ├─ Receives completion
  ├─ Updates test status to COMPLETED
  ├─ Stores summary in MongoDB
  ├─ Broadcasts to WebSocket clients
  │
Frontend
  ├─ Receives completion event
  ├─ Stops real-time updates
  ├─ Displays final results
  ├─ Shows charts and metrics
  └─ User can export results
```

## Load Test Execution Model

### Virtual User (VU) Lifecycle

```
VU Created
  │
  ├─ Wait for ramp-up (if applicable)
  │
  ├─ LOOP (until test duration)
  │   ├─ Select URL based on weight
  │   ├─ Make HTTP request
  │   ├─ Record latency
  │   ├─ Apply think time
  │   ├─ Retry on failure (exponential backoff)
  │   └─ Update error count
  │
VU Stopped (test duration reached)
```

### Concurrency Model

```
Event Loop (Single-threaded, async)
  │
  ├─ VU 1 (current request)
  ├─ VU 2 (waiting for response)
  ├─ VU 3 (think time)
  └─ ... N VUs multiplexed
```

### Ramp-up Logic

```
Concurrency over time with ramp-up:

Users
  │     ┌─────────────────────────
  │    /
  │   /
  │  /
  │ /
  └─────────────────────────────── Time
    ↑              ↑
   Start        Ramp-up complete
  
Duration: Linear increase from 0 to target concurrency
```

## Metrics Collection

### Per-Second Metrics

For each second of the test:

```
PerSecondMetrics
├─ Timestamp
├─ Requests sent
├─ Requests succeeded
├─ Requests failed
├─ Individual latencies (array)
├─ Error types (dictionary)
│
└─ Calculated stats:
   ├─ RPS (successful requests)
   ├─ Min latency
   ├─ Avg latency
   ├─ P50 latency
   ├─ P95 latency
   ├─ P99 latency
   └─ Max latency
```

### Percentile Calculation

```
Sorted latencies: [10, 15, 20, ..., 45, 50, 52, ..., 100, 105]

P50: 50th percentile (median)
  → ~50% of requests faster, ~50% slower

P95: 95th percentile
  → 95% of requests faster, 5% slower
  → SLA target: ensure P95 < threshold

P99: 99th percentile
  → 99% of requests faster, 1% slower
  → Catches worst-case scenarios
```

## Error Handling

### Retry Mechanism

```
Request fails
  │
  ├─ Attempt count < retry_count?
  │   │
  │   ├─ YES: Exponential backoff
  │   │   ├─ Delay: 0.1 * 2^attempt seconds
  │   │   ├─ Retry request
  │   │   └─ Loop
  │   │
  │   └─ NO: Count as failed
  │       ├─ Record error type
  │       ├─ Update error distribution
  │       └─ Continue to next request
  │
Success or final failure → Continue VU loop
```

### Error Types Tracked

```
- ConnectionError: Failed to connect
- Timeout: Request exceeded timeout
- HTTPError: HTTP error status codes
- SSLError: Certificate verification
- Other: Unexpected failures
```

## Scalability Considerations

### Single Worker Limitations

- **VUs**: ~1000-5000 depending on machine
- **Target Throughput**: ~10,000-50,000 RPS
- **Connections**: Limited by OS file descriptor limit

### Distributed Testing (Future)

```
Backend
  │
  ├─ Worker 1 (50 VUs)
  ├─ Worker 2 (50 VUs)
  ├─ Worker 3 (50 VUs)
  └─ Worker N
  
Aggregated metrics sent back to backend
```

## Security Architecture

### Current Implementation

- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ Error handling (no sensitive info leak)
- ✅ Environment-based config

### Production Enhancement

- 🔒 JWT authentication
- 🔒 Rate limiting
- 🔒 HTTPS enforcement
- 🔒 Database user auth
- 🔒 API key management

## Performance Optimizations

### Backend
- Async/await for all I/O
- Connection pooling (MongoDB)
- Database indexing on frequently queried fields
- Response compression (via reverse proxy)

### Worker
- AsyncIO event loop (single-threaded but concurrent)
- Connection reuse via aiohttp session
- Per-second metric aggregation (avoid per-request overhead)
- Efficient memory usage (~1-2KB per VU)

### Frontend
- Code splitting via Vite
- Lazy component loading
- Responsive Container for charts
- Limited chart data points (~60 seconds)

## Technology Choices

### Why AsyncIO (Python)?
- 100% compatible with waiting I/O (HTTP requests)
- Single-threaded but highly concurrent
- Efficient for thousands of concurrent connections
- Better latency measurement than multithreading

### Why FastAPI?
- Built on Starlette (async ASGI)
- Automatic OpenAPI documentation
- Type hints with Pydantic validation
- High performance
- Excellent for microservices

### Why WebSocket?
- Real-time bidirectional communication
- Lower latency than polling
- Server can push metrics without client requests
- Efficient bandwidth usage

### Why React + Vite?
- Fast development experience (HMR)
- Component reusability
- Rich ecosystem (Recharts, etc.)
- Modern JavaScript features
- Excellent performance

## Deployment Considerations

### Development
- Single machine
- All services locally
- Hot reload enabled
- Debug mode

### Production
- Separate machines (optional)
- Reverse proxy (nginx)
- Load balancing (multiple backends/workers)
- HTTPS/TLS
- Horizontal scaling
- Monitoring & alerting
- Database backups

## Extension Points

### Add Custom Metrics
- Extend `PerSecondMetrics` class
- Add new fields in result summary
- Update frontend charts

### Add Authentication
- Implement JWT in FastAPI
- Store user_id in test document
- Filter tests by user

### Add Distributed Testing
- Deploy multiple workers
- Backend coordinates across workers
- Aggregate metrics

### Add Persistence
- Export results to S3
- Archive old tests
- Backup MongoDB

---

This architecture is designed for **production-grade** performance, reliability, and scalability while remaining simple to understand and extend.

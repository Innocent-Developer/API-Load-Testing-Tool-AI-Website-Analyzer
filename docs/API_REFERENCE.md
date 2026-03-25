# API Reference

Complete API documentation for the LoadTester platform.

## Base URLs

- **Backend**: `http://localhost:8000`
- **Worker**: `http://localhost:8001`
- **WebSocket**: `ws://localhost:8000`

## Authentication

Currently supports anonymous access. Production should implement JWT:

```javascript
// Would add Authorization header
Authorization: Bearer {token}
```

---

## Health & Status

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "environment": "development"
}
```

**Status Codes:**
- `200` - Service healthy
- `503` - Service unavailable

---

## Tests API

### Create Test
```
POST /api/tests
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "API Load Test",
  "description": "Test the API endpoints",
  "urls": [
    {
      "url": "https://api.example.com/users",
      "method": "GET",
      "weight": 0.7,
      "timeout": 10,
      "headers": {
        "Authorization": "Bearer token"
      },
      "body": null
    },
    {
      "url": "https://api.example.com/posts",
      "method": "POST",
      "weight": 0.3,
      "timeout": 15,
      "headers": {},
      "body": "{\"title\": \"test\"}"
    }
  ],
  "duration": 300,
  "concurrency": 50,
  "ramp_up": 30,
  "retry_count": 2,
  "think_time": 0.5
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "status": "pending",
  "message": "Test created and queued for execution"
}
```

**Validation Rules:**
- `name`: 1-255 characters, required
- `urls`: 1+ required
- `url`: Valid URL format, required
- `method`: GET|POST|PUT|DELETE|PATCH|HEAD
- `weight`: 0.1-100
- `timeout`: 1-120 seconds
- `duration`: 10-3600 seconds
- `concurrency`: 1-1000
- `ramp_up`: 0-300 seconds
- `retry_count`: 0-5
- `think_time`: 0-10 seconds

**Status Codes:**
- `201` - Test created
- `400` - Invalid request
- `500` - Server error

---

### List Tests
```
GET /api/tests?page=1&page_size=20&status=completed
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-indexed) |
| page_size | integer | 20 | Results per page (1-100) |
| status | string | null | Filter: pending, running, completed, failed, stopped |

**Response (200):**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "tests": [
    {
      "id": "507f1f77bcf86cd799439011",
      "config": {
        "name": "API Load Test",
        "urls": [...],
        "duration": 300,
        "concurrency": 50
      },
      "status": "completed",
      "created_at": "2024-01-15T10:00:00Z",
      "started_at": "2024-01-15T10:00:05Z",
      "completed_at": "2024-01-15T10:05:05Z",
      "summary": {
        "total_requests": 15000,
        "successful_requests": 14850,
        "failed_requests": 150,
        "success_rate": 99.0,
        "avg_rps": 50.0,
        "peak_rps": 55.2,
        "min_latency": 10.5,
        "avg_latency": 45.3,
        "p50_latency": 42.1,
        "p95_latency": 89.5,
        "p99_latency": 150.2,
        "max_latency": 289.7,
        "error_distribution": {
          "timeout": 100,
          "connection_error": 50
        }
      }
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

---

### Get Test Details
```
GET /api/tests/{test_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| test_id | string | MongoDB ObjectId |

**Response (200):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "config": {...},
  "status": "completed",
  "created_at": "2024-01-15T10:00:00Z",
  "started_at": "2024-01-15T10:00:05Z",
  "completed_at": "2024-01-15T10:05:05Z",
  "summary": {...},
  "per_second_metrics": [
    {
      "timestamp": "2024-01-15T10:00:05Z",
      "requests_sent": 50,
      "requests_succeeded": 49,
      "requests_failed": 1,
      "rps": 49,
      "min_latency": 12.3,
      "avg_latency": 45.6,
      "p50_latency": 43.2,
      "p95_latency": 92.1,
      "p99_latency": 156.3,
      "max_latency": 198.5
    }
  ],
  "error_message": null
}
```

**Status Codes:**
- `200` - Success
- `404` - Test not found
- `500` - Server error

---

### Stop Test
```
POST /api/tests/{test_id}/stop
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "status": "stopped",
  "message": "Test stopped"
}
```

**Status Codes:**
- `200` - Successfully stopped
- `400` - Test not in running state
- `404` - Test not found
- `500` - Server error

---

### Delete Test
```
DELETE /api/tests/{test_id}
```

**Response (200):**
```json
{
  "message": "Test deleted successfully"
}
```

**Status Codes:**
- `200` - Successfully deleted
- `404` - Test not found
- `500` - Server error

---

## WebSocket API

### Connect to Test Stream
```
WS /ws/tests/{test_id}
```

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tests/507f1f77bcf86cd799439011')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log(data)
}
```

**Metrics Update Event:**
```json
{
  "type": "metrics_update",
  "data": {
    "timestamp": "2024-01-15T10:00:05Z",
    "requests_sent": 50,
    "requests_succeeded": 49,
    "requests_failed": 1,
    "rps": 49,
    "min_latency": 12.3,
    "avg_latency": 45.6,
    "p50_latency": 43.2,
    "p95_latency": 92.1,
    "p99_latency": 156.3,
    "max_latency": 198.5
  }
}
```

**Test Complete Event:**
```json
{
  "type": "test_complete",
  "data": {
    "status": "completed",
    "completed_at": "2024-01-15T10:05:05Z",
    "summary": {
      "total_requests": 15000,
      "successful_requests": 14850,
      "success_rate": 99.0,
      "avg_latency": 45.3,
      ...
    }
  }
}
```

**Keep-Alive:**
```javascript
// Client should send ping every 30 seconds
ws.send('ping')

// Server responds with pong
// ws.onmessage = 'pong'
```

**Close Codes:**
- `1000` - Normal closure
- `1002` - Protocol error
- `1011` - Server error

---

## Internal APIs (Worker → Backend)

### Send Test Metrics
```
POST /api/tests/{test_id}/metrics
Content-Type: application/json
```

**Called by:** Worker (internal only)

**Request Body:**
```json
{
  "timestamp": "2024-01-15T10:00:05Z",
  "requests_sent": 50,
  "requests_succeeded": 49,
  "requests_failed": 1,
  "rps": 49,
  "min_latency": 12.3,
  "avg_latency": 45.6,
  "p50_latency": 43.2,
  "p95_latency": 92.1,
  "p99_latency": 156.3,
  "max_latency": 198.5
}
```

**Response (200):**
```json
{
  "status": "received"
}
```

---

### Report Test Completion
```
POST /api/tests/{test_id}/complete
Content-Type: application/json
```

**Called by:** Worker (internal only)

**Request Body:**
```json
{
  "summary": {
    "total_requests": 15000,
    "successful_requests": 14850,
    "failed_requests": 150,
    "success_rate": 99.0,
    "avg_rps": 50.0,
    "peak_rps": 55.2,
    "min_latency": 10.5,
    "avg_latency": 45.3,
    "p50_latency": 42.1,
    "p95_latency": 89.5,
    "p99_latency": 150.2,
    "max_latency": 289.7,
    "error_distribution": {
      "timeout": 100,
      "connection_error": 50
    }
  },
  "error_message": null
}
```

**Response (200):**
```json
{
  "status": "completed"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

### 404 Not Found
```json
{
  "detail": "Test not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Data Types & Formats

### Test Status
```
pending   - Queued, not yet started
running   - Currently executing
completed - Finished successfully
failed    - Error during execution
stopped   - User stopped test
```

### HTTP Methods
```
GET, POST, PUT, DELETE, PATCH, HEAD
```

### Timestamps
ISO 8601 format: `2024-01-15T10:00:00Z`

### IDs
MongoDB ObjectId (24-character hex): `507f1f77bcf86cd799439011`

### Latencies & Durations
Milliseconds as floating point numbers: `45.3`, `10.5`

### Percentages
0-100 as floating point: `99.5`, `45.2`

---

## Rate Limiting

Currently disabled. Production should implement:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1610700000
```

---

## CORS Headers

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Example Workflows

### Full Test Lifecycle

```bash
# 1. Create test
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","urls":[...],...}'
# Returns: {"id":"507f1f77bcf86cd799439011","status":"pending"}

# 2. Monitor via WebSocket
ws = new WebSocket('ws://localhost:8000/ws/tests/507f1f77bcf86cd799439011')
# Receives metrics updates

# 3. Get details
curl http://localhost:8000/api/tests/507f1f77bcf86cd799439011
# Returns: full test with results

# 4. List all
curl http://localhost:8000/api/tests?status=completed
# Returns: paginated list

# 5. Delete when done
curl -X DELETE http://localhost:8000/api/tests/507f1f77bcf86cd799439011
```

### Using cURL for Testing

```bash
# Create test
TEST_ID=$(curl -s -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Test",
    "urls": [{"url": "https://httpbin.org/get"}],
    "duration": 30,
    "concurrency": 5
  }' | jq -r '.id')

# Monitor status
curl http://localhost:8000/api/tests/$TEST_ID | jq '.status'

# Wait for completion
while [ "$(curl -s http://localhost:8000/api/tests/$TEST_ID | jq -r '.status')" != "completed" ]; do
  sleep 2
done

# View results
curl http://localhost:8000/api/tests/$TEST_ID | jq '.summary'
```

---

## OpenAPI/Swagger

Full interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Versioning

API version: `v1.0.0`

Future versions will maintain backward compatibility with deprecation warnings.

---

For more information, see [README.md](./README.md) and [ARCHITECTURE.md](./ARCHITECTURE.md)

# Complete Project File Listing

## Backend Files

### `backend/main.py` (800+ lines)
**Main FastAPI application**
- FastAPI app initialization
- CORS middleware
- WebSocket connection manager
- Route definitions:
  - `POST /api/tests` - Create test
  - `GET /api/tests` - List tests
  - `GET /api/tests/{id}` - Get test details
  - `POST /api/tests/{id}/stop` - Stop test
  - `DELETE /api/tests/{id}` - Delete test
  - `WS /ws/tests/{id}` - WebSocket endpoint
  - `POST /api/tests/{id}/metrics` - Receive metrics
  - `POST /api/tests/{id}/complete` - Test completion
- Health check endpoint
- Error handlers
- Lifecycle hooks

### `backend/models.py` (200+ lines)
**Pydantic data models**
- `TestStatus` enum (pending, running, completed, failed, stopped)
- `HTTPMethod` enum (GET, POST, PUT, DELETE, PATCH, HEAD)
- `URLConfig` - Single URL configuration
- `LoadTestConfig` - Full test configuration
- `PerSecondMetrics` - Per-second statistics
- `TestResultSummary` - Final test summary
- `LoadTest` - Main test document
- `TestData` - Database model
- Request/response models
- `WebsiteAnalysisResult` - Analyzer output

### `backend/database.py` (150+ lines)
**MongoDB operations**
- Connection management
- Index creation
- CRUD helpers:
  - `insert_test()` - Create test
  - `get_test_by_id()` - Fetch test
  - `list_tests()` - Paginated list
  - `update_test_status()` - Update status
  - `update_test_with_results()` - Store results
  - `append_per_second_metrics()` - Add metrics
  - `get_tests_by_status()` - Filter tests
  - `delete_test()` - Remove test

### `backend/config.py` (50 lines)
**Environment configuration**
- Settings class with Pydantic
- Environment variable loading
- Default values
- Database URL
- Security settings
- Service URLs

### `backend/worker_client.py` (80 lines)
**Worker communication**
- `submit_test_to_worker()` - Queue test with retries
- Exponential backoff logic
- Error handling
- Status management

### `backend/Dockerfile`
**Docker image for backend**
- Python 3.11 slim base
- Dependencies installation
- Port 8000 exposure

### `backend/requirements.txt`
**Python dependencies**
- fastapi
- uvicorn
- pydantic
- motor (async MongoDB)
- pymongo
- python-dotenv
- aiohttp
- websockets
- And more...

### `backend/.env.example`
**Environment template**
- MongoDB connection
- Database name
- Security keys
- Service URLs
- Environment configuration

---

## Worker Files

### `worker/main.py` (300+ lines)
**Worker FastAPI service**
- FastAPI app initialization
- Background test executor loop
- Test queue management
- Health check endpoint
- `POST /execute` - Execute test
- Test execution logic
- Performance metrics callback
- Completion notification
- Error handling

### `worker/load_test_engine.py` (600+ lines)
**Core async load testing engine**
- `HTTPMethod` enum
- `RequestConfig` - Configuration for URL
- `PerSecondMetrics` - Per-second statistics with calculation
- `TestResult` - Final results and summary
- `LoadTestEngine` main class:
  - `__init__()` - Initialize with config
  - `run()` - Execute test
  - `_run_virtual_user()` - Individual VU logic
  - `_select_config()` - Weighted URL selection
  - `_make_request()` - HTTP request with retries
- Percentile calculation
- Exponential backoff retry logic
- Concurrent connection management
- Latency tracking
- Error collection

### `worker/website_analyzer.py` (500+ lines)
**AI website analyzer**
- `WebsiteAnalyzer` main class
- Tech stack signatures dictionary
- Email extraction patterns
- Social media patterns
- `analyze()` - Main analysis method
- `_fetch_html()` - Fetch website content
- `_extract_title()` - Extract page title
- `_extract_description()` - Extract meta description
- `_detect_tech_stack()` - Tech detection
- `_extract_emails()` - Email extraction
- `_extract_social_links()` - Social media detection
- `_extract_scripts()` - Script extraction
- `_analyze_performance()` - Performance hints
- `_generate_ai_summary()` - AI summary generation
- Error handling and validation

### `worker/config.py` (40 lines)
**Worker configuration**
- WorkerSettings class
- Environment variables
- Worker ID
- Default timeouts
- Environment setup

### `worker/Dockerfile`
**Docker image for worker**
- Python 3.11 slim
- XML/XSLT libraries for BeautifulSoup
- Dependencies installation
- Port 8001 exposure

### `worker/requirements.txt`
**Python dependencies**
- asyncio
- aiohttp
- httpx
- pydantic
- beautifulsoup4
- lxml
- aiofiles
- And more...

### `worker/.env.example`
**Environment template**
- Worker host/port
- Backend URL
- Environment configuration

---

## Frontend Files

### `frontend/src/App.jsx` (150+ lines)
**Main application component**
- Router setup
- Navigation bar
- Dark mode toggle
- Mobile menu
- Route definitions
- Layout wrapper
- Footer

### `frontend/src/main.jsx`
**React entry point**
- React DOM initialization
- App component rendering
- CSS import

### `frontend/src/index.css` (100+ lines)
**Tailwind styles**
- Global styles
- Component classes:
  - btn-primary, btn-secondary, btn-danger
  - card
  - input-field
  - metric-badge
- Chart container styles
- Custom utilities

### `frontend/src/pages/Dashboard.jsx` (150+ lines)
**Main dashboard page**
- Statistics cards
- Pie chart (test distribution)
- Recent tests list
- Auto-refresh (5 seconds)
- Loading state
- StatCard component

### `frontend/src/pages/CreateTest.jsx` (200+ lines)
**Test creation form**
- Test name/description input
- Dynamic URL configuration
- Add/remove URLs
- Test settings (duration, concurrency, etc.)
- Form validation
- Error handling
- Submit logic

### `frontend/src/pages/TestDetail.jsx` (250+ lines)
**Test results and monitoring**
- Test header with status
- Configuration summary
- Results metrics cards
- Real-time charts (RPS, latency)
- WebSocket integration
- Export functionality
- Stop test button
- Target URLs display
- ResultCard component

### `frontend/src/pages/TestHistory.jsx` (150+ lines)
**Test history and list**
- Paginated test table
- Status filtering
- Test deletion
- Results summary
- Quick view links
- Sorting and filtering
- Pagination controls

### `frontend/src/services/api.js` (70 lines)
**API client and WebSocket helper**
- Axios instance configuration
- testsAPI object:
  - create()
  - get()
  - list()
  - stop()
  - delete()
- `connectWebSocket()` function
- Error handling

### `frontend/vite.config.js`
**Vite configuration**
- React plugin
- Dev server settings
- Proxy configuration (API + WebSocket)

### `frontend/tailwind.config.js`
**Tailwind CSS configuration**
- Dark mode class strategy
- Custom colors
- Theme extensions
- Responsive breakpoints

### `frontend/postcss.config.js`
**PostCSS configuration**
- Tailwind CSS plugin
- Autoprefixer

### `frontend/index.html`
**HTML template**
- Meta tags
- Root div
- Script import

### `frontend/package.json`
**NPM dependencies and scripts**
- Dependencies: React, Vite, Tailwind, Recharts, etc.
- Scripts: dev, build, preview, lint
- Dev dependencies for building

### `frontend/Dockerfile`
**Docker image for frontend**
- Node.js 18
- Dependencies installation
- Build step
- Port 5173 exposure

---

## Documentation Files

### `docs/README.md`
**Main documentation**
- Project overview
- Features list
- Technology stack
- Quick start guide
- Usage instructions
- API endpoints
- Configuration
- Best practices
- Troubleshooting
- Learning resources

### `docs/QUICKSTART.md`
**Quick start guide**
- Prerequisites
- Docker setup (easiest)
- Manual setup (3-4 terminals)
- First test walkthrough
- Verification steps
- Troubleshooting
- Tips and tricks

### `docs/BACKEND_SETUP.md`
**Backend installation guide**
- Prerequisites
- Installation steps
- Environment setup
- MongoDB setup
- Running the server
- Verification
- Project structure explanation
- File descriptions
- API endpoints enumeration
- Testing examples
- Troubleshooting
- Production tips

### `docs/WORKER_SETUP.md`
**Worker setup guide**
- What is the worker
- Prerequisites
- Installation steps
- Environment setup
- Project structure
- Component explanations
- How it works diagram
- Configuration options
- Example scenarios
- Performance considerations
- Troubleshooting
- Advanced usage

### `docs/FRONTEND_SETUP.md`
**Frontend setup guide**
- What is the frontend
- Prerequisites
- Installation steps
- Project structure
- Key files explained
- UI components
- Technologies used
- Styling and dark mode
- API integration
- Vite configuration
- Development workflow
- Performance optimization
- Troubleshooting
- Production deployment

### `docs/ARCHITECTURE.md`
**System architecture**
- System overview diagram
- Component architecture
- Data flow diagrams
- Load test execution model
- Virtual user lifecycle
- Concurrency model
- Ramp-up logic
- Metrics collection
- Percentile calculation
- Error handling
- Retry mechanism
- Scalability considerations
- Security architecture
- Performance optimizations
- Technology choices explained
- Deployment considerations
- Extension points

### `docs/API_REFERENCE.md`
**Complete API documentation**
- Base URLs
- Authentication
- Health/status endpoints
- Test management endpoints
- WebSocket API
- Internal APIs
- Error responses
- Data types and formats
- Rate limiting
- CORS headers
- Example workflows
- cURL examples
- OpenAPI/Swagger info
- Versioning

### `docs/PROJECT_COMPLETE.md`
**Project completion summary**
- Deliverables summary
- Feature checklist
- Complete file structure
- Quick start options
- Key features implemented
- Statistics
- Technology stack
- Performance characteristics
- Production readiness
- Architecture highlights
- Next steps
- Documentation index
- Code quality
- System requirements
- Extension points
- Security checklist
- Success metrics

---

## Configuration & Setup Files

### `docker-compose.yml`
**Docker Compose orchestration**
- MongoDB service
- Backend service
- Worker service
- Frontend service
- Volume management
- Network setup
- Environment variables
- Health checks
- Dependencies between services

### `.gitignore`
**Git ignore rules**
- Python: venv, __pycache__, .pyc
- Backend: .env, logs
- Worker: .env, logs
- Frontend: node_modules, dist, .env.local
- IDE: .vscode, .idea
- OS: .DS_Store, Thumbs.db

### `backend/Dockerfile`
**Backend Docker image**
- Python 3.11 slim base
- Build dependencies
- Requirements installation
- Port exposure

### `worker/Dockerfile`
**Worker Docker image**
- Python 3.11 slim base
- XML libraries
- Requirements installation
- Port exposure

### `frontend/Dockerfile`
**Frontend Docker image**
- Node.js 18 base
- Dependencies installation
- Build step
- Dev server start

### `backend/.env.example`
**Backend environment template**

### `worker/.env.example`
**Worker environment template**

---

## Statistics

**Total Project:**
- Backend: 5 files, ~1,300 lines of code
- Worker: 3 files, ~1,400 lines of code
- Frontend: 7 files, ~1,000 lines of code
- Documentation: 9 files, ~2,000+ lines
- Configuration: 6 files

**Total: 30+ files, 5,000+ lines of code**

---

## File Dependencies

```
Frontend (React)
  ├─ Calls → Backend API
  ├─ Connects → WebSocket (Backend)
  └─ Uses → Recharts, Tailwind, Axios

Backend (FastAPI)
  ├─ Connects to → MongoDB
  ├─ Queues work to → Worker
  ├─ Connects from → Frontend (WebSocket)
  └─ Updates ← Worker (HTTP)

Worker (Python)
  ├─ Receives from → Backend
  ├─ Connects to → Target URLs (HTTP)
  ├─ Sends to → Backend (HTTP)
  └─ Uses → LoadTestEngine, WebsiteAnalyzer

MongoDB
  ├─ Stores ← Backend (Tests)
  └─ Queries ← Backend (Results)
```

---

## How to Navigate

1. **Start Here**: `docs/QUICKSTART.md`
2. **Understand System**: `docs/ARCHITECTURE.md`
3. **Setup Backend**: `docs/BACKEND_SETUP.md` → run `backend/main.py`
4. **Setup Worker**: `docs/WORKER_SETUP.md` → run `worker/main.py`
5. **Setup Frontend**: `docs/FRONTEND_SETUP.md` → run `frontend/`
6. **Use Platform**: Open `http://localhost:5173`
7. **API Docs**: See `docs/API_REFERENCE.md`
8. **Full Docs**: See `docs/README.md`

---

## Quick Reference

| Component | Language | Port | Start Command |
|-----------|----------|------|---|
| Frontend | JavaScript | 5173 | `npm run dev` |
| Backend | Python | 8000 | `uvicorn main:app --port 8000` |
| Worker | Python | 8001 | `uvicorn main:app --port 8001` |
| Database | - | 27017 | `docker run -p 27017:27017 mongo` |

---

All files are production-ready and fully documented!

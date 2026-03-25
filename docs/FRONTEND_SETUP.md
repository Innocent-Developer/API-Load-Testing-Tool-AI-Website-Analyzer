# Frontend Setup Guide

## What is the Frontend?

The Frontend is a **React + Vite + Tailwind CSS** dashboard that provides:
- Real-time test creation interface
- Live metrics visualization
- Test history and analytics
- Dark mode support
- WebSocket-powered real-time updates
- Responsive mobile-friendly design

## Prerequisites

- Node.js 16+
- npm or yarn
- Running Backend (http://localhost:8000)

## Installation

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Configure Environment

The frontend uses Vite's environment variables:

```bash
# Copy template if provided
cp .env.example .env.local
```

Vite will automatically proxy API calls based on `vite.config.js`:
- `/api/*` → http://localhost:8000/api
- `/ws/*` → ws://localhost:8000/ws

### 4. Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### 5. Verify Installation

1. Open http://localhost:5173 in browser
2. You should see the LoadTester dashboard
3. Click "New Test" to create a test
4. Dashboard should load without errors

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx       # Main dashboard view
│   │   ├── CreateTest.jsx      # Test creation form
│   │   ├── TestDetail.jsx      # Test results & charts
│   │   └── TestHistory.jsx     # Test list & history
│   ├── services/
│   │   └── api.js              # API client & WebSocket
│   ├── App.jsx                 # Main App component
│   ├── main.jsx                # React entry point
│   └── index.css               # Tailwind styles
├── index.html                  # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS configuration
├── package.json                # Dependencies
└── Dockerfile                  # Docker image
```

## Key Files Explained

### `src/App.jsx`
- Main application component
- Navigation setup
- Dark mode toggle
- Route definitions
- Layout wrapper

### `src/pages/Dashboard.jsx`
- Dashboard overview
- Statistics cards
- Recent tests
- Pie chart for status distribution
- Auto-refreshes every 5 seconds

### `src/pages/CreateTest.jsx`
- Test configuration form
- URL management (add/remove)
- Test settings (duration, concurrency, etc.)
- Form validation
- Submission to backend

### `src/pages/TestDetail.jsx`
- Test results display
- Live charts (RPS, latency)
- Test status and metrics
- Export functionality
- WebSocket connection for real-time updates

### `src/pages/TestHistory.jsx`
- Paginated test list
- Status filtering
- Test deletion
- Results summary

### `src/services/api.js`
- Axios instance for HTTP requests
- WebSocket connection helper
- API endpoints abstraction
- Error handling

## UI Components

### Pages

#### Dashboard
- **Statistics Cards**: Total tests, RPS, success rate, requests
- **Test Distribution Pie Chart**: Completed, running, failed breakdown
- **Recent Tests List**: Latest 10 tests with quick status

#### Create Test
- **Test Information**: Name and description
- **URL Configuration**: Dynamic URL addition with method, weight, timeout
- **Test Settings**: Duration, concurrency, ramp-up, retry count, think time
- **Form Validation**: Ensures required fields before submission

#### Test Detail
- **Status Display**: Current test status badge
- **Metrics Cards**: Total requests, success rate, latency percentiles
- **Line Charts**: RPS and latency trends over time
- **Target URLs**: List of tested endpoints
- **Export**: Download results as JSON

#### History
- **Test Table**: All tests with pagination
- **Status Filter**: Filter by completed, running, failed
- **Quick Actions**: View detail or delete test
- **Pagination**: Navigate through results

## Key Technologies

### React 18
- Modern React with hooks
- Functional components
- State management with useState

### Vite
- Lightning-fast build tool
- Native ES modules
- Hot module replacement (HMR)

### Tailwind CSS
- Utility-first CSS framework
- Dark mode support
- Responsive design

### Recharts
- React charting library
- LineChart, AreaChart, PieChart
- Responsive containers

### Axios
- HTTP client library
- Built-in interceptors
- Promise-based

### Socket.IO Client
- Real-time bidirectional communication
- Automatic reconnection

### Lucide React
- Modern icon library
- Tree-shakeable
- Optimized SVGs

## Styling

### Tailwind CSS Setup
- Configured in `tailwind.config.js`
- Dark mode: `class` strategy
- Custom components in `src/index.css`

### Custom CSS Classes
```css
.btn-primary       /* Primary button */
.btn-secondary     /* Secondary button */
.btn-danger        /* Danger button */
.card              /* Card container */
.input-field       /* Form input */
.metric-badge      /* Status badge */
```

### Dark Mode
- Toggle in navbar
- Applies `dark` class to document root
- All components support dark mode

## API Integration

### Service Layer (`src/services/api.js`)

```javascript
// Create test
await testsAPI.create(testConfig)

// Get test
await testsAPI.get(testId)

// List tests
await testsAPI.list(page, pageSize, status)

// Stop test
await testsAPI.stop(testId)

// Delete test
await testsAPI.delete(testId)

// WebSocket connection
connectWebSocket(testId, onMessage, onError)
```

### WebSocket Events

```javascript
// Metrics update
{
  "type": "metrics_update",
  "data": {
    "rps": 100,
    "avg_latency": 45.2,
    ...
  }
}

// Test completion
{
  "type": "test_complete",
  "data": {
    "status": "completed",
    "summary": {...}
  }
}
```

## Vite Configuration

### Proxy Setup
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
  '/ws': {
    target: 'ws://localhost:8000',
    ws: true
  }
}
```

This automatically routes:
- API calls to backend
- WebSocket to backend

## Development Workflow

### Local Development
```bash
npm run dev
```

Vite provides:
- Fast HMR (Hot Module Replacement)
- ES module-based development
- Instant feedback

### Build for Production
```bash
npm run build
# Outputs to dist/
```

### Preview Production Build
```bash
npm run preview
```

## Performance Optimization

### Image Optimization
- Use lazy loading: `loading="lazy"`
- Consider webp format

### Bundle Size
- Tree-shakeable imports
- Recharts auto-optimizes included components

### Charts Performance
- Responsive containers
- Limited data points for large tests
- Pagination for lists

## Troubleshooting

### API Connection Issues
```
Cannot reach http://localhost:8000
```

**Solution:**
1. Verify backend is running
2. Check `vite.config.js` proxy settings
3. Check browser DevTools Network tab
4. Check CORS settings on backend

### WebSocket Connection Failed
```
WebSocket connection error
```

**Solution:**
1. Verify backend is running
2. Check test ID is correct
3. Check browser console for details
4. Ensure test exists in database

### Chart Not Displaying
```
Recharts not rendering
```

**Solution:**
1. Check console for JavaScript errors
2. Ensure data is properly formatted
3. Verify ResponsiveContainer has parent height
4. Check browser console for warnings

### Form Validation Issues
```
Form won't submit despite being filled
```

**Solution:**
1. Check browser console for validation errors
2. Ensure all required fields are filled
3. Verify URLs are valid
4. Check concurrency/duration values

### Dark Mode Not Working
```
Dark mode toggle doesn't apply
```

**Solution:**
1. Verify Tailwind dark mode config
2. Check if TailwindCSS is loading
3. Clear browser cache
4. Check for conflicting CSS

### Slow Performance
```
Dashboard or charts rendering slowly
```

**Solution:**
1. Reduce chart data points
2. Paginate large lists
3. Use browser DevTools to profile
4. Check network requests

## Production Deployment

### Build Configuration
```bash
npm run build
```

Produces optimized build in `dist/` directory.

### Deployment Options

#### Static Hosting (GitHub Pages, Netlify, Vercel)
```bash
npm run build
# Deploy dist/ folder
```

#### Docker
```bash
docker build -t loadtester-frontend .
docker run -p 3000:3000 loadtester-frontend
```

#### Behind Reverse Proxy (nginx)
```nginx
location / {
  proxy_pass http://localhost:5173;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection 'upgrade';
  proxy_set_header Host $host;
  proxy_cache_bypass $http_upgrade;
}
```

### Environment Configuration
Set backend URL for production:
```javascript
// src/services/api.js
const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000/api'
```

## Browser Support

- Chrome/Chromium 90+
- Firefox 89+
- Safari 14+
- Edge 90+

Modern browsers with ES2020+ support.

## Accessibility

- Semantic HTML
- ARIA labels where needed
- Keyboard navigation
- Color contrast (WCAG AA compliant)

## Next Steps

1. ✅ Start the frontend
2. ⏭️  [Backend Setup](./BACKEND_SETUP.md)
3. ⏭️  [Worker Setup](./WORKER_SETUP.md)
4. ⏭️  Create and run a test!

## Resources

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)
- [Axios](https://axios-http.com/)

## Tips

1. **Hot Module Replacement**: Changes save automatically without full page reload
2. **Fast Refresh**: React components update without losing state
3. **Network Inspector**: Use browser DevTools to debug API calls
4. **Responsive Testing**: Test on mobile using device emulation
5. **Performance**: Use Lighthouse in DevTools to audit

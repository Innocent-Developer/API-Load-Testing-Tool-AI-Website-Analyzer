import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}`
  : 'http://localhost:8000'

const WS_BASE = import.meta.env.VITE_WS_URL
  ? import.meta.env.VITE_WS_URL
  : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000`

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Tests API
export const testsAPI = {
  create: (data) => api.post('/api/tests', data),
  get: (id) => api.get(`/api/tests/${id}`),
  list: (page = 1, pageSize = 20, status = null) => {
    let url = `/api/tests?page=${page}&page_size=${pageSize}`
    if (status) url += `&status=${status}`
    return api.get(url)
  },
  stop: (id) => api.post(`/api/tests/${id}/stop`),
  delete: (id) => api.delete(`/api/tests/${id}`)
}

export const connectWebSocket = (testId, onMessage, onError) => {
  const wsUrl = `${WS_BASE}/ws/tests/${testId}`
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('WebSocket connected:', testId)
    // Send keep-alive
    setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 30000)
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    if (onError) onError(error)
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected')
  }

  return ws
}

export default api

import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Tests API
export const testsAPI = {
  create: (data) => api.post('/tests', data),
  get: (id) => api.get(`/tests/${id}`),
  list: (page = 1, pageSize = 20, status = null) => {
    let url = `/tests?page=${page}&page_size=${pageSize}`
    if (status) url += `&status=${status}`
    return api.get(url)
  },
  stop: (id) => api.post(`/tests/${id}/stop`),
  delete: (id) => api.delete(`/tests/${id}`)
}

export const connectWebSocket = (testId, onMessage, onError) => {
  const wsUrl = `ws://localhost:8000/ws/tests/${testId}`
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

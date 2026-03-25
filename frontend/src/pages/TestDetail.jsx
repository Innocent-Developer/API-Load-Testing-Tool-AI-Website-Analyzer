import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Play, Pause, Download, ArrowLeft } from 'lucide-react'
import { testsAPI, connectWebSocket } from '../services/api'

export default function TestDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [test, setTest] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [ws, setWs] = useState(null)

  useEffect(() => {
    fetchTest()
    const interval = setInterval(fetchTest, 2000)
    return () => clearInterval(interval)
  }, [id])

  useEffect(() => {
    if (test && (test.status === 'running' || test.status === 'pending')) {
      const webSocket = connectWebSocket(
        id,
        (data) => {
          if (data.type === 'metrics_update') {
            setMetrics(prev => [...prev.slice(-59), data.data])
          }
        },
        (error) => console.error('WebSocket error:', error)
      )
      setWs(webSocket)

      return () => {
        if (webSocket) webSocket.close()
      }
    }
  }, [test?.status, id])

  const fetchTest = async () => {
    try {
      const response = await testsAPI.get(id)
      setTest(response.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to fetch test details')
      setLoading(false)
    }
  }

  const handleStop = async () => {
    try {
      await testsAPI.stop(id)
      fetchTest()
    } catch (err) {
      setError('Failed to stop test')
    }
  }

  const handleExport = () => {
    const data = JSON.stringify({ test, metrics }, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test-${id}-${new Date().getTime()}.json`
    link.click()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-lg text-gray-500">Loading test details...</div>
      </div>
    )
  }

  if (!test) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-lg text-gray-500">Test not found</div>
      </div>
    )
  }

  const summary = test.summary || {}
  const isRunning = test.status === 'running'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div onClick={() => navigate(-1)} className="cursor-pointer flex items-center space-x-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
        <ArrowLeft size={20} />
        <span>Back</span>
      </div>

      {/* Test Info */}
      <div className="card">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">{test.config.name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{test.config.description}</p>
            <div className="flex items-center space-x-4 mt-4">
              <span className={`metric-badge ${
                test.status === 'completed' ? 'success' : 
                test.status === 'failed' ? 'error' : 'warning'
              }`}>
                {test.status.toUpperCase()}
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Created: {new Date(test.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            {isRunning && (
              <button onClick={handleStop} className="btn-danger flex items-center space-x-2">
                <Pause size={18} /> Stop Test
              </button>
            )}
            <button onClick={handleExport} className="btn-secondary flex items-center space-x-2">
              <Download size={18} /> Export
            </button>
          </div>
        </div>
      </div>

      {/* Config Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">URLs</p>
          <p className="text-2xl font-bold">{test.config.urls.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Concurrency</p>
          <p className="text-2xl font-bold">{test.config.concurrency}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Duration</p>
          <p className="text-2xl font-bold">{test.config.duration}s</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 dark:text-gray-400">Ramp-up</p>
          <p className="text-2xl font-bold">{test.config.ramp_up}s</p>
        </div>
      </div>

      {/* Results */}
      {summary && Object.keys(summary).length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ResultCard label="Total Requests" value={summary.total_requests} />
          <ResultCard label="Success Rate" value={`${summary.success_rate}%`} color="green" />
          <ResultCard label="Avg Latency" value={`${summary.avg_latency?.toFixed(2)}ms`} />
          <ResultCard label="P95 Latency" value={`${summary.p95_latency?.toFixed(2)}ms`} />
          <ResultCard label="P99 Latency" value={`${summary.p99_latency?.toFixed(2)}ms`} />
          <ResultCard label="Peak RPS" value={summary.peak_rps?.toFixed(2)} />
        </div>
      )}

      {/* Charts */}
      {metrics.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">RPS Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="rps" stroke="#3b82f6" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Latency Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="avg_latency" stroke="#10b981" fill="#d1fae5" />
                <Area type="monotone" dataKey="p95_latency" stroke="#f59e0b" fill="#fef3c7" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Target URLs */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Target URLs</h3>
        <div className="space-y-3">
          {test.config.urls.map((url, index) => (
            <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium text-sm">{url.method} {url.url}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400">Weight: {url.weight} | Timeout: {url.timeout}s</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ResultCard({ label, value, color = 'blue' }) {
  const colorClasses = {
    blue: 'border-blue-200 dark:border-blue-700',
    green: 'border-green-200 dark:border-green-700',
    red: 'border-red-200 dark:border-red-700'
  }

  return (
    <div className={`card border-l-4 ${colorClasses[color]}`}>
      <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
      <p className="text-2xl font-bold mt-2">{value}</p>
    </div>
  )
}

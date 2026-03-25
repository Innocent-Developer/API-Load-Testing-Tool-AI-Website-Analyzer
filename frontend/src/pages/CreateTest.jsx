import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, AlertCircle } from 'lucide-react'
import { testsAPI } from '../services/api'

export default function CreateTest() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    name: '',
    description: '',
    urls: [{ url: '', method: 'GET', weight: 1.0, timeout: 10 }],
    duration: 60,
    concurrency: 10,
    ramp_up: 10,
    retry_count: 1,
    think_time: 0
  })

  const handleFormChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({
      ...prev,
      [name]: name === 'duration' || name === 'concurrency' || name === 'ramp_up' || name === 'retry_count'
        ? parseInt(value) || 0
        : parseFloat(value) || value
    }))
  }

  const handleUrlChange = (index, field, value) => {
    setForm(prev => {
      const urls = [...prev.urls]
      if (field === 'weight' || field === 'timeout') {
        urls[index][field] = parseFloat(value) || 0
      } else {
        urls[index][field] = value
      }
      return { ...prev, urls }
    })
  }

  const addUrl = () => {
    setForm(prev => ({
      ...prev,
      urls: [...prev.urls, { url: '', method: 'GET', weight: 1.0, timeout: 10 }]
    }))
  }

  const removeUrl = (index) => {
    setForm(prev => ({
      ...prev,
      urls: prev.urls.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validation
      if (!form.name.trim()) {
        throw new Error('Test name is required')
      }
      if (form.urls.length === 0) {
        throw new Error('At least one URL is required')
      }
      if (form.urls.some(u => !u.url.trim())) {
        throw new Error('All URLs must be filled')
      }

      const response = await testsAPI.create(form)
      const testId = response.data.id

      // Redirect to test detail
      navigate(`/test/${testId}`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create test')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">Create New Load Test</h1>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg flex items-start space-x-3">
            <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Test Information</h2>

            <div>
              <label className="block text-sm font-medium mb-2">Test Name *</label>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleFormChange}
                className="input-field"
                placeholder="e.g., API v1 Load Test"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleFormChange}
                className="input-field"
                rows="3"
                placeholder="Optional description"
              />
            </div>
          </div>

          {/* URLs */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Target URLs</h2>
              <button
                type="button"
                onClick={addUrl}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus size={18} /> Add URL
              </button>
            </div>

            {form.urls.map((url, index) => (
              <div key={index} className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg space-y-3">
                <div className="flex justify-between">
                  <h3 className="font-medium">URL {index + 1}</h3>
                  {form.urls.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeUrl(index)}
                      className="text-red-600 dark:text-red-400 hover:text-red-700 flex items-center space-x-1"
                    >
                      <Trash2 size={16} /> Remove
                    </button>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">URL *</label>
                  <input
                    type="url"
                    value={url.url}
                    onChange={(e) => handleUrlChange(index, 'url', e.target.value)}
                    className="input-field"
                    placeholder="https://api.example.com/endpoint"
                    required
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Method</label>
                    <select
                      value={url.method}
                      onChange={(e) => handleUrlChange(index, 'method', e.target.value)}
                      className="input-field"
                    >
                      <option>GET</option>
                      <option>POST</option>
                      <option>PUT</option>
                      <option>DELETE</option>
                      <option>PATCH</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Weight</label>
                    <input
                      type="number"
                      value={url.weight}
                      onChange={(e) => handleUrlChange(index, 'weight', e.target.value)}
                      min="0.1"
                      max="100"
                      step="0.1"
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Timeout (s)</label>
                    <input
                      type="number"
                      value={url.timeout}
                      onChange={(e) => handleUrlChange(index, 'timeout', e.target.value)}
                      min="1"
                      max="120"
                      className="input-field"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Test Settings */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Test Settings</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
                <input
                  type="number"
                  name="duration"
                  value={form.duration}
                  onChange={handleFormChange}
                  min="10"
                  max="3600"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Concurrency</label>
                <input
                  type="number"
                  name="concurrency"
                  value={form.concurrency}
                  onChange={handleFormChange}
                  min="1"
                  max="1000"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Ramp-up Time (seconds)</label>
                <input
                  type="number"
                  name="ramp_up"
                  value={form.ramp_up}
                  onChange={handleFormChange}
                  min="0"
                  max="300"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Retry Count</label>
                <input
                  type="number"
                  name="retry_count"
                  value={form.retry_count}
                  onChange={handleFormChange}
                  min="0"
                  max="5"
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Think Time (seconds)</label>
              <input
                type="number"
                name="think_time"
                value={form.think_time}
                onChange={handleFormChange}
                min="0"
                max="10"
                step="0.1"
                className="input-field"
              />
            </div>
          </div>

          {/* Submit */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Test...' : 'Create & Start Test'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

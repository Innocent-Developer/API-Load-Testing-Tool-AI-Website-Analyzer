import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [testsRes, statsRes] = await Promise.all([
        api.get('/api/tests'),
        api.get('/api/tests/stats/user')
      ]);
      setTests(testsRes.data || []);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      // Validate at least one URL
      if (!formData.urls.some(u => u.url.trim())) {
        setError('Please enter at least one URL');
        return;
      }

      const payload = {
        name: formData.name || 'Unnamed Test',
        urls: formData.urls.filter(u => u.url.trim()),
        duration: parseInt(formData.duration) || 60,
        concurrency: parseInt(formData.concurrency) || 10,
        ramp_up: parseInt(formData.ramp_up) || 0
      };
      
      const response = await api.post('/api/tests', payload);
      setTests([response.data, ...tests]);
      setShowCreateForm(false);
      setSuccess('✓ Test created successfully! It will start running shortly.');
      setFormData({
        name: '',
        urls: [{ url: '', method: 'GET' }],
        duration: 60,
        concurrency: 10,
        ramp_up: 0
      });
      await fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to create test';
      setError(`❌ Error: ${errorMsg}`);
      console.error('Test creation error:', err);
    }
  };

  const handleUrlChange = (index, field, value) => {
    const newUrls = [...formData.urls];
    newUrls[index][field] = value;
    setFormData({ ...formData, urls: newUrls });
  };

  const addUrl = () => {
    setFormData({
      ...formData,
      urls: [...formData.urls, { url: '', method: 'GET' }]
    });
  };

  const removeUrl = (index) => {
    setFormData({
      ...formData,
      urls: formData.urls.filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={() => navigate('/profile')}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
          >
            Profile
          </button>
        </div>

        {/* Error and Success Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
            {success}
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-600 text-sm">Total Tests</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total_tests}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-600 text-sm">Tests Today</div>
              <div className="text-3xl font-bold text-gray-900">{stats.tests_today}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-600 text-sm">Plan</div>
              <div className="text-3xl font-bold text-indigo-600 capitalize">{stats.plan}</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-gray-600 text-sm">Remaining Tests</div>
              <div className="text-3xl font-bold text-green-600">{stats.remaining_tests}</div>
            </div>
          </div>
        )}

        {/* Create Test Button */}
        <div className="mb-8">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-medium"
          >
            {showCreateForm ? 'Cancel' : 'Create New Test'}
          </button>
        </div>

        {/* Create Test Form */}
        {showCreateForm && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-2xl font-bold mb-4">Create Load Test</h2>
            <form onSubmit={handleCreateTest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Test Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Homepage Load Test"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">URLs to Test</label>
                {formData.urls.map((url, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="url"
                      required
                      value={url.url}
                      onChange={(e) => handleUrlChange(index, 'url', e.target.value)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                      placeholder="https://example.com"
                    />
                    <select
                      value={url.method}
                      onChange={(e) => handleUrlChange(index, 'method', e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg"
                    >
                      <option>GET</option>
                      <option>POST</option>
                      <option>PUT</option>
                      <option>DELETE</option>
                    </select>
                    {formData.urls.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeUrl(index)}
                        className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addUrl}
                  className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  + Add URL
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium">Duration (seconds)</label>
                  <input
                    type="number"
                    value={formData.duration}
                    onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
                    className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Concurrency</label>
                  <input
                    type="number"
                    value={formData.concurrency}
                    onChange={(e) => setFormData({ ...formData, concurrency: parseInt(e.target.value) })}
                    className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Ramp-up (seconds)</label>
                  <input
                    type="number"
                    value={formData.ramp_up}
                    onChange={(e) => setFormData({ ...formData, ramp_up: parseInt(e.target.value) })}
                    className="w-full mt-1 px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 font-medium"
              >
                Create Test
              </button>
            </form>
          </div>
        )}

        {/* Tests List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-2xl font-bold">Recent Tests</h2>
          </div>
          {tests.length === 0 ? (
            <div className="p-6 text-center text-gray-600">
              No tests yet. Create your first test to get started!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Created</th>
                    <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.map((test) => (
                    <tr key={test.id} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-3 text-sm">{test.name}</td>
                      <td className="px-6 py-3 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          test.status === 'completed' ? 'bg-green-100 text-green-800' :
                          test.status === 'failed' ? 'bg-red-100 text-red-800' :
                          test.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          test.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {test.status || 'pending'}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-sm">{new Date(test.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-3 text-sm">
                        <button
                          onClick={() => navigate(`/test/${test.id}`)}
                          className="text-indigo-600 hover:text-indigo-700 font-medium"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

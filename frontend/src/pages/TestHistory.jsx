import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Trash2, ExternalLink } from 'lucide-react'
import { testsAPI } from '../services/api'

export default function TestHistory() {
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    fetchTests()
  }, [page, statusFilter])

  const fetchTests = async () => {
    try {
      setLoading(true)
      const response = await testsAPI.list(page, 20, statusFilter || undefined)
      setTests(response.data.tests)
      setTotalPages(Math.ceil(response.data.total / response.data.page_size))
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch tests:', error)
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this test?')) return

    try {
      await testsAPI.delete(id)
      fetchTests()
    } catch (error) {
      console.error('Failed to delete test:', error)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Test History</h1>

      {/* Filter */}
      <div className="flex gap-2">
        {['', 'completed', 'running', 'failed'].map(status => (
          <button
            key={status}
            onClick={() => {
              setStatusFilter(status)
              setPage(1)
            }}
            className={`px-4 py-2 rounded-lg transition-colors ${
              statusFilter === status
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {status || 'All'}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-x-auto">
        {loading ? (
          <div className="text-center py-8">Loading tests...</div>
        ) : tests.length === 0 ? (
          <div className="text-center py-8 text-gray-600 dark:text-gray-400">
            No tests found
          </div>
        ) : (
          <>
            <table className="w-full">
              <thead className="border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="text-left py-3 px-4 font-semibold">Test Name</th>
                  <th className="text-left py-3 px-4 font-semibold">Status</th>
                  <th className="text-left py-3 px-4 font-semibold">Created</th>
                  <th className="text-left py-3 px-4 font-semibold">Success Rate</th>
                  <th className="text-left py-3 px-4 font-semibold">Requests</th>
                  <th className="text-left py-3 px-4 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tests.map((test) => (
                  <tr key={test.id} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="py-3 px-4">
                      <Link to={`/test/${test.id}`} className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
                        {test.config.name}
                      </Link>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`metric-badge ${
                        test.status === 'completed' ? 'success' :
                        test.status === 'failed' ? 'error' : 'warning'
                      }`}>
                        {test.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {new Date(test.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      {test.summary ? (
                        <span className="font-medium text-green-600 dark:text-green-400">
                          {test.summary.success_rate}%
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {test.summary?.total_requests || '-'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Link
                          to={`/test/${test.id}`}
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                        >
                          <ExternalLink size={18} />
                        </Link>
                        <button
                          onClick={() => handleDelete(test.id)}
                          className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

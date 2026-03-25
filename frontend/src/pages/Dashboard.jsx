import React, { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Activity, Users, TrendingUp, Zap } from 'lucide-react'
import { testsAPI } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalTests: 0,
    avgRps: 0,
    avgSuccessRate: 0,
    totalRequests: 0
  })
  const [recentTests, setRecentTests] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await testsAPI.list(1, 100)
      const tests = response.data.tests

      // Calculate stats
      let totalTests = tests.length
      let totalRps = 0
      let totalSuccessRate = 0
      let totalRequests = 0
      let count = 0

      tests.forEach((test) => {
        if (test.summary) {
          totalRps += test.summary.avg_rps || 0
          totalSuccessRate += test.summary.success_rate || 0
          totalRequests += test.summary.total_requests || 0
          count++
        }
      })

      setStats({
        totalTests,
        avgRps: count > 0 ? (totalRps / count).toFixed(2) : 0,
        avgSuccessRate: count > 0 ? (totalSuccessRate / count).toFixed(2) : 0,
        totalRequests
      })

      setRecentTests(tests.slice(0, 10))
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-lg text-gray-500 dark:text-gray-400">Loading dashboard...</div>
      </div>
    )
  }

  const chartData = [
    { name: 'Completed', value: recentTests.filter(t => t.status === 'completed').length },
    { name: 'Running', value: recentTests.filter(t => t.status === 'running').length },
    { name: 'Failed', value: recentTests.filter(t => t.status === 'failed').length }
  ]

  const COLORS = ['#10b981', '#f59e0b', '#ef4444']

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Activity size={24} />}
          title="Total Tests"
          value={stats.totalTests}
          color="blue"
        />
        <StatCard
          icon={<Zap size={24} />}
          title="Avg RPS"
          value={parseFloat(stats.avgRps).toFixed(1)}
          color="yellow"
        />
        <StatCard
          icon={<TrendingUp size={24} />}
          title="Avg Success Rate"
          value={`${parseFloat(stats.avgSuccessRate).toFixed(1)}%`}
          color="green"
        />
        <StatCard
          icon={<Users size={24} />}
          title="Total Requests"
          value={stats.totalRequests.toLocaleString()}
          color="purple"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Status Distribution */}
        <div className="card lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4">Test Status Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Tests Summary */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Recent Tests</h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentTests.map((test) => (
              <div key={test.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium">{test.config.name}</h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(test.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`metric-badge ${
                    test.status === 'completed' ? 'success' : 
                    test.status === 'failed' ? 'error' : 'warning'
                  }`}>
                    {test.status}
                  </span>
                  {test.summary && (
                    <span className="text-sm font-medium text-green-600 dark:text-green-400">
                      {test.summary.success_rate}%
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, title, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-700',
    yellow: 'bg-yellow-50 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-700',
    green: 'bg-green-50 dark:bg-green-900 text-green-600 dark:text-green-400 border-green-200 dark:border-green-700',
    purple: 'bg-purple-50 dark:bg-purple-900 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-700'
  }

  return (
    <div className={`card border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-2xl opacity-60">{icon}</div>
      </div>
    </div>
  )
}

import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { Moon, Sun, Menu, X, LogOut } from 'lucide-react'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Pricing from './pages/Pricing'
import AIAnalyzer from './pages/AIAnalyzer'
import CreateTest from './pages/CreateTest'
import TestDetail from './pages/TestDetail'
import TestHistory from './pages/TestHistory'

import './App.css'

// Protected Route Component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" />
}

export default function App() {
  const [isDark, setIsDark] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null

  React.useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  // Public Layout (for login/signup)
  if (!token) {
    return (
      <Router>
        <div className={isDark ? 'dark' : ''}>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
          </div>
        </div>
      </Router>
    )
  }

  // Authenticated Layout
  return (
    <Router>
      <div className={isDark ? 'dark' : ''}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
          {/* Navigation */}
          <nav className="bg-white dark:bg-gray-800 shadow-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                {/* Logo */}
                <Link to="/" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">⚡</span>
                  </div>
                  <span className="font-bold text-lg hidden sm:inline">LoadTester Pro</span>
                </Link>

                {/* Desktop Menu */}
                <div className="hidden md:flex space-x-8">
                  <Link to="/dashboard" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/analyzer" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    AI Analyzer
                  </Link>
                  <Link to="/pricing" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    Pricing
                  </Link>
                </div>

                {/* Controls */}
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setIsDark(!isDark)}
                    className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    {isDark ? <Sun size={20} /> : <Moon size={20} />}
                  </button>

                  {/* User Menu */}
                  <Link
                    to="/profile"
                    className="hidden sm:block px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    {user?.email?.split('@')[0]}
                  </Link>

                  <button
                    onClick={handleLogout}
                    className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 transition-colors"
                  >
                    <LogOut size={20} />
                  </button>

                  {/* Mobile Menu Button */}
                  <button
                    className="md:hidden p-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  >
                    {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                  </button>
                </div>
              </div>

              {/* Mobile Menu */}
              {mobileMenuOpen && (
                <div className="md:hidden pb-4 space-y-2">
                  <Link
                    to="/dashboard"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/analyzer"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    AI Analyzer
                  </Link>
                  <Link
                    to="/pricing"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Pricing
                  </Link>
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Profile
                  </Link>
                </div>
              )}
            </div>
          </nav>

          {/* Routes */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/pricing" element={<ProtectedRoute><Pricing /></ProtectedRoute>} />
              <Route path="/analyzer" element={<ProtectedRoute><AIAnalyzer /></ProtectedRoute>} />
              <Route path="/create" element={<ProtectedRoute><CreateTest /></ProtectedRoute>} />
              <Route path="/test/:id" element={<ProtectedRoute><TestDetail /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><TestHistory /></ProtectedRoute>} />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-gray-200 dark:border-gray-700 mt-12 py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 dark:text-gray-400">
              <p>© 2024 LoadTester Pro. Production-ready API testing & website analysis platform.</p>
            </div>
          </footer>
        </div>
      </div>
    </Router>
  )
}

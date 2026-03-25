import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Moon, Sun, Menu, X } from 'lucide-react'

import Dashboard from './pages/Dashboard'
import CreateTest from './pages/CreateTest'
import TestDetail from './pages/TestDetail'
import TestHistory from './pages/TestHistory'

import './App.css'

export default function App() {
  const [isDark, setIsDark] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  React.useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

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
                  <span className="font-bold text-lg hidden sm:inline">LoadTester</span>
                </Link>

                {/* Desktop Menu */}
                <div className="hidden md:flex space-x-8">
                  <Link to="/" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/create" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    New Test
                  </Link>
                  <Link to="/history" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                    History
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
                    to="/"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/create"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    New Test
                  </Link>
                  <Link
                    to="/history"
                    className="block px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    History
                  </Link>
                </div>
              )}
            </div>
          </nav>

          {/* Routes */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/create" element={<CreateTest />} />
              <Route path="/test/:id" element={<TestDetail />} />
              <Route path="/history" element={<TestHistory />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-gray-200 dark:border-gray-700 mt-12 py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 dark:text-gray-400">
              <p>© 2024 LoadTester. Production-ready API testing platform.</p>
            </div>
          </footer>
        </div>
      </div>
    </Router>
  )
}

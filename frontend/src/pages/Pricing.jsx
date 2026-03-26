import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Pricing() {
  const navigate = useNavigate();
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState('monthly');

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await api.get('/api/payment/pricing');
      setPricing(response.data);
    } catch (err) {
      console.error('Failed to fetch pricing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan, billingPeriod) => {
    try {
      // For demo: use dummy card token
      const cardToken = '4242424242424242';
      
      const response = await api.post('/api/payment/upgrade', null, {
        params: {
          plan,
          billing_period: billingPeriod,
          card_token: cardToken
        }
      });

      if (response.data.success) {
        alert('Plan upgraded successfully!');
        navigate('/dashboard');
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Upgrade failed');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!pricing) {
    return <div className="flex items-center justify-center min-h-screen">Pricing not available</div>;
  }

  const free = pricing.free;
  const pro = pricing.pro;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">Simple, Transparent Pricing</h1>
          <p className="text-gray-600 mt-4">Choose the plan that fits your load testing needs</p>
        </div>

        {/* Billing Period Toggle */}
        <div className="flex justify-center mb-12">
          <div className="bg-white rounded-lg p-1 inline-flex">
            {['monthly', 'quarterly', 'annual'].map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPlan(period)}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  selectedPlan === period
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Free Plan */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Free</h2>
            <p className="text-gray-600 mb-6">Perfect for testing</p>
            
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">$0</span>
              <span className="text-gray-600 ml-2">Forever</span>
            </div>

            <ul className="space-y-4 mb-8">
              <li className="flex items-center">
                <span className="text-green-600 mr-3">✓</span>
                <span>2 tests per day</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-600 mr-3">✓</span>
                <span>Up to 10 concurrent users</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-600 mr-3">✓</span>
                <span>JSON export only</span>
              </li>
              <li className="flex items-center">
                <span className="text-gray-300 mr-3">✗</span>
                <span className="text-gray-500">AI Website Analyzer</span>
              </li>
              <li className="flex items-center">
                <span className="text-gray-300 mr-3">✗</span>
                <span className="text-gray-500">Priority support</span>
              </li>
            </ul>

            <button
              disabled
              className="w-full bg-gray-200 text-gray-400 py-2 rounded-lg font-medium cursor-default"
            >
              Current Plan
            </button>
          </div>

          {/* Pro Plan */}
          <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg shadow-lg p-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-yellow-400 text-gray-900 px-4 py-1 m-4 rounded-full text-sm font-bold">
              POPULAR
            </div>
            
            <h2 className="text-2xl font-bold text-white mb-2">Pro</h2>
            <p className="text-indigo-100 mb-6">For professional teams</p>
            
            <div className="mb-6">
              <span className="text-4xl font-bold text-white">
                ${pro?.pricing?.[selectedPlan] || 29.99}
              </span>
              <span className="text-indigo-100 ml-2 capitalize">{selectedPlan}</span>
            </div>

            <ul className="space-y-4 mb-8">
              <li className="flex items-center text-white">
                <span className="text-yellow-300 mr-3">✓</span>
                <span>Unlimited tests</span>
              </li>
              <li className="flex items-center text-white">
                <span className="text-yellow-300 mr-3">✓</span>
                <span>Up to 1000 concurrent users</span>
              </li>
              <li className="flex items-center text-white">
                <span className="text-yellow-300 mr-3">✓</span>
                <span>JSON, CSV, XML exports</span>
              </li>
              <li className="flex items-center text-white">
                <span className="text-yellow-300 mr-3">✓</span>
                <span>AI Website Analyzer</span>
              </li>
              <li className="flex items-center text-white">
                <span className="text-yellow-300 mr-3">✓</span>
                <span>Priority support</span>
              </li>
            </ul>

            <button
              onClick={() => handleUpgrade('pro', selectedPlan)}
              className="w-full bg-yellow-400 text-gray-900 py-2 rounded-lg font-bold hover:bg-yellow-300 transition"
            >
              Upgrade to Pro
            </button>
          </div>
        </div>

        {/* Features Comparison */}
        <div className="mt-16 bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold mb-8 text-center">Feature Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Feature</th>
                  <th className="text-center py-3 px-4 font-medium">Free</th>
                  <th className="text-center py-3 px-4 font-medium">Pro</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">Daily Tests</td>
                  <td className="text-center py-3 px-4">2</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">Concurrent Users</td>
                  <td className="text-center py-3 px-4">10</td>
                  <td className="text-center py-3 px-4">1000</td>
                </tr>
                <tr className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">Export Formats</td>
                  <td className="text-center py-3 px-4">JSON</td>
                  <td className="text-center py-3 px-4">JSON, CSV, XML</td>
                </tr>
                <tr className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">AI Analyzer</td>
                  <td className="text-center py-3 px-4">
                    <span className="text-red-600">✗</span>
                  </td>
                  <td className="text-center py-3 px-4">
                    <span className="text-green-600">✓</span>
                  </td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="py-3 px-4">Support</td>
                  <td className="text-center py-3 px-4">Community</td>
                  <td className="text-center py-3 px-4">Priority</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="text-center mt-12">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

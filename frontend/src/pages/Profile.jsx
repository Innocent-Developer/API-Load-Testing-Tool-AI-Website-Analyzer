import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [planDetails, setPlanDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const profileRes = await api.get('/api/auth/profile');
      setProfile(profileRes.data);
      
      const infoRes = await api.get('/api/api/info');
      setPlanDetails(infoRes.data.plan);
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!profile) {
    return <div className="flex items-center justify-center min-h-screen">Profile not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Profile</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Profile Card */}
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <h2 className="text-2xl font-bold mb-6">Account Information</h2>
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <p className="mt-1 text-lg text-gray-900">{profile.name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <p className="mt-1 text-lg text-gray-900">{profile.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <p className="mt-1 text-lg text-gray-900 capitalize">{profile.role}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Member Since</label>
              <p className="mt-1 text-lg text-gray-900">
                {new Date(profile.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Plan Card */}
        {planDetails && (
          <div className="bg-white rounded-lg shadow p-8 mb-6">
            <h2 className="text-2xl font-bold mb-6">Plan Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Current Plan</label>
                <p className="mt-1 text-2xl font-bold text-indigo-600 capitalize">
                  {planDetails.plan}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Daily Test Limit</label>
                <p className="mt-1 text-2xl font-bold text-gray-900">
                  {planDetails.daily_test_limit === 999999 ? 'Unlimited' : planDetails.daily_test_limit}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Max Concurrency</label>
                <p className="mt-1 text-2xl font-bold text-gray-900">
                  {planDetails.max_concurrency}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Remaining Tests Today</label>
                <p className="mt-1 text-2xl font-bold text-green-600">
                  {planDetails.remaining_tests}
                </p>
              </div>
            </div>

            {planDetails.plan === 'free' && (
              <button
                onClick={() => navigate('/pricing')}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 font-medium"
              >
                Upgrade to Pro
              </button>
            )}
          </div>
        )}

        {/* Tests Used */}
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <h2 className="text-2xl font-bold mb-6">Usage</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Tests Used Today</label>
              <p className="mt-1 text-2xl font-bold text-gray-900">{profile.tests_used_today}</p>
            </div>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 font-medium"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}

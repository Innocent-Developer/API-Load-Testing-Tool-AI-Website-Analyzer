import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function AIAnalyzer() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const response = await api.get('/api/ai/analyses');
      setAnalyses(response.data.analyses || []);
    } catch (err) {
      console.error('Failed to fetch analyses:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!url) return;

    setAnalyzing(true);

    try {
      const response = await api.post('/api/ai/analyze', { url });
      setAnalyses([response.data, ...analyses]);
      setSelectedAnalysis(response.data);
      setUrl('');
    } catch (err) {
      alert(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">AI Website Analyzer</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Analysis Form */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6">Analyze a Website</h2>
          <form onSubmit={handleAnalyze} className="flex gap-2">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={analyzing}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {analyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Analyses List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b bg-gray-50">
                <h3 className="font-bold">Recent Analyses</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {analyses.length === 0 ? (
                  <div className="p-6 text-center text-gray-600">No analyses yet</div>
                ) : (
                  analyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      onClick={() => setSelectedAnalysis(analysis)}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                        selectedAnalysis?.id === analysis.id ? 'bg-indigo-50' : ''
                      }`}
                    >
                      <div className="font-medium text-sm truncate">{analysis.url}</div>
                      <div className="text-xs text-gray-600 mt-1">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex gap-2 mt-2">
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                          SEO: {analysis.seo_score}
                        </span>
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          Perf: {analysis.performance_score}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Analysis Details */}
          <div className="lg:col-span-2">
            {selectedAnalysis ? (
              <div className="space-y-6">
                {/* URL */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold mb-4">Website URL</h3>
                  <a
                    href={selectedAnalysis.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-indigo-600 hover:text-indigo-700 break-all"
                  >
                    {selectedAnalysis.url}
                  </a>
                </div>

                {/* Scores */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="font-bold mb-2">SEO Score</h3>
                    <div className="text-4xl font-bold text-blue-600">
                      {selectedAnalysis.seo_score}%
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="font-bold mb-2">Performance Score</h3>
                    <div className="text-4xl font-bold text-green-600">
                      {selectedAnalysis.performance_score}%
                    </div>
                  </div>
                </div>

                {/* Tech Stack */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold mb-4">Tech Stack</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedAnalysis.tech_stack.map((tech) => (
                      <span
                        key={tech}
                        className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* AI Summary */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold mb-4">AI Summary</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {selectedAnalysis.grock_summary}
                  </p>
                </div>

                {/* Contact Information */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="font-bold mb-4">Contact Information</h3>
                  
                  {selectedAnalysis.emails.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-sm mb-2">Emails:</h4>
                      <ul className="space-y-1">
                        {selectedAnalysis.emails.map((email) => (
                          <li key={email} className="text-sm text-indigo-600">
                            {email}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {Object.keys(selectedAnalysis.social_links).length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm mb-2">Social Links:</h4>
                      <div className="space-y-1">
                        {Object.entries(selectedAnalysis.social_links).map(
                          ([platform, link]) => (
                            <a
                              key={platform}
                              href={link}
                              target="_blank"
                              rel="noreferrer"
                              className="text-sm text-indigo-600 hover:text-indigo-700 block capitalize"
                            >
                              {platform}
                            </a>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Meta Description */}
                {selectedAnalysis.meta_description && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="font-bold mb-4">Meta Description</h3>
                    <p className="text-gray-700 text-sm">
                      {selectedAnalysis.meta_description}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-gray-500 text-lg">
                  Select an analysis or analyze a new website to see details
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

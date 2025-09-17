import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';

const History = () => {
  const { token } = useContext(AuthContext);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/resume/history`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setHistory(response.data);
      } catch (err) {
        console.error('History fetch error:', err);
        setError('Failed to load resume history');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-600 text-lg">Loading history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500 text-lg">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Resume Analysis History</h2>

      {history.length === 0 ? (
        <p className="text-gray-600">No history found.</p>
      ) : (
        history.map((entry) => (
          <div key={entry.id} className="mb-6 border-b pb-4">
            <p className="text-gray-700"><strong>Date:</strong> {new Date(entry.created_at).toLocaleString()}</p>
            <p className="text-gray-700"><strong>Score:</strong> {entry.score}</p>

            <div className="mt-2">
              <p className="font-medium text-gray-700">Skills:</p>
              <ul className="list-disc list-inside text-gray-600">
                {JSON.parse(entry.skills || '[]').map((skill, idx) => (
                  <li key={idx}>{skill}</li>
                ))}
              </ul>
            </div>

            <div className="mt-2">
              <p className="font-medium text-gray-700">Missing Keywords:</p>
              <ul className="list-disc list-inside text-red-600">
                {JSON.parse(entry.missing_keywords || '[]').map((kw, idx) => (
                  <li key={idx}>{kw}</li>
                ))}
              </ul>
            </div>

            <div className="mt-2">
              <p className="font-medium text-gray-700">Suggestions:</p>
              <ul className="list-disc list-inside text-blue-600">
                {JSON.parse(entry.suggestions || '[]').map((sugg, idx) => (
                  <li key={idx}>{sugg}</li>
                ))}
              </ul>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default History; 

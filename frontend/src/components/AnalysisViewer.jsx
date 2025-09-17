import React, { useState } from 'react';
import axios from 'axios';

const AnalysisViewer = ({ analysis }) => {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  const handleDownloadPDF = async () => {
    setDownloading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/resume/download-pdf`,
        { analysis },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob',
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'resume_report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('PDF download error:', err);
      setError('Failed to download PDF');
    } finally {
      setDownloading(false);
    }
  };

  if (!analysis) return null;

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mt-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Resume Analysis</h2>

      <div className="mb-4">
        <p className="text-gray-700"><strong>Score:</strong> {analysis.score}</p>
      </div>

      <div className="mb-4">
        <p className="text-gray-700 font-medium">Skills Extracted:</p>
        <ul className="list-disc list-inside text-gray-600">
          {analysis.skills.map((skill, idx) => (
            <li key={idx}>{skill}</li>
          ))}
        </ul>
      </div>

      <div className="mb-4">
        <p className="text-gray-700 font-medium">Missing Keywords:</p>
        <ul className="list-disc list-inside text-red-600">
          {analysis.missingKeywords.map((keyword, idx) => (
            <li key={idx}>{keyword}</li>
          ))}
        </ul>
      </div>

      <div className="mb-4">
        <p className="text-gray-700 font-medium">Suggestions:</p>
        <ul className="list-disc list-inside text-blue-600">
          {analysis.suggestions.map((suggestion, idx) => (
            <li key={idx}>{suggestion}</li>
          ))}
        </ul>
      </div>

      {error && <p className="text-red-500 mb-2">{error}</p>}

      <button
        onClick={handleDownloadPDF}
        disabled={downloading}
        className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition"
      >
        {downloading ? 'Downloading...' : 'Download PDF Report'}
      </button>
    </div>
  );
};

export default AnalysisViewer;
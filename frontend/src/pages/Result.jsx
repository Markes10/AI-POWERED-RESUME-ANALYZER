import React from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import AnalysisViewer from '../components/AnalysisViewer';

const Result = () => {
  const location = useLocation();
  const analysis = location.state?.analysis;

  if (!analysis) {
    return <Navigate to="/upload" replace />;
  }

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Analysis Result</h2>
      <AnalysisViewer analysis={analysis} />
    </div>
  );
};

export default Result; 

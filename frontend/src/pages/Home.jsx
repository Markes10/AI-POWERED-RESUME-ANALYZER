import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Home = () => {
  const { token } = useContext(AuthContext);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-6">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-indigo-700 mb-4">AI-Powered Resume Analyzer</h1>
        <p className="text-gray-700 text-lg mb-6">
          Upload your resume and job description to get instant feedback, keyword suggestions, and a match score.
          Perfect your resume for every application with intelligent insights.
        </p>

        {token ? (
          <Link
            to="/upload"
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
          >
            Upload Resume
          </Link>
        ) : (
          <div className="space-x-4">
            <Link
              to="/login"
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="bg-gray-200 text-indigo-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 

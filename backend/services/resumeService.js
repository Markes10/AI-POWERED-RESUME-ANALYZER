const axios = require('axios');
require('dotenv').config();

const NLP_URL = process.env.NLP_SERVICE_URL || 'http://localhost:8000';

exports.parseResume = async (resumeText, jobDescription) => {
  try {
    // 1. Extract entities from resume
    const extractRes = await axios.post(`${NLP_URL}/extract`, {
      text: resumeText,
    });
    const skills = extractRes.data.skills || [];

    // 2. Match resume to job description
    const matchRes = await axios.post(`${NLP_URL}/match`, {
      resume_text: resumeText,
      jd_text: jobDescription,
    });
    const score = matchRes.data.score || 0;

    // 3. Generate feedback suggestions
    const feedbackRes = await axios.post(`${NLP_URL}/feedback`, {
      resume_text: resumeText,
      jd_text: jobDescription,
    });

    const missingKeywords = feedbackRes.data.missing_keywords || [];
    const suggestions = feedbackRes.data.suggestions || [];

    // Final analysis object
    return {
      score,
      skills,
      missingKeywords,
      suggestions,
    };
  } catch (err) {
    console.error('NLP service error:', err.message);
    throw new Error('Failed to analyze resume using NLP service');
  }
};
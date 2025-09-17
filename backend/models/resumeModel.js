const db = require('../config/db');

// Save resume analysis to history table
exports.saveResumeAnalysis = async (userId, resumeText, jobDescription, analysis) => {
  const query = `
    INSERT INTO resume_history (
      user_id,
      resume_text,
      job_description,
      score,
      skills,
      missing_keywords,
      suggestions
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `;

  const values = [
    userId,
    resumeText,
    jobDescription,
    analysis.score,
    JSON.stringify(analysis.skills),
    JSON.stringify(analysis.missingKeywords),
    JSON.stringify(analysis.suggestions),
  ];

  try {
    await db.execute(query, values);
  } catch (err) {
    console.error('Error saving resume analysis:', err);
    throw err;
  }
};

// Fetch resume history for a user
exports.getResumeHistory = async (userId) => {
  const query = `
    SELECT id, resume_text, job_description, score, skills, missing_keywords, suggestions, created_at
    FROM resume_history
    WHERE user_id = ?
    ORDER BY created_at DESC
  `;

  try {
    const [rows] = await db.execute(query, [userId]);
    return rows;
  } catch (err) {
    console.error('Error fetching resume history:', err);
    throw err;
  }
};
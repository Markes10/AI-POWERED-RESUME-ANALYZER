const extractTextFromFile = require('../utils/fileParser');
const { parseResume } = require('../services/resumeService');
const { saveResumeAnalysis, getResumeHistory } = require('../models/resumeModel');
const { generatePDF } = require('../utils/pdfGenerator');

// Upload resume, analyze, and store history
exports.uploadResume = async (req, res, next) => {
  try {
    const userId = req.userId;
    const resumeBuffer = req.file.buffer;
    const jobDescription = req.body.jobDescription;
    const resumeText = await extractTextFromFile(resumeBuffer, req.file.originalname);

    const analysis = await parseResume(resumeText, jobDescription);
    await saveResumeAnalysis(userId, resumeText, jobDescription, analysis);

    res.status(200).json(analysis);
  } catch (err) {
    console.error('Upload error:', err);
    next(err);
  }
};

// Fetch resume analysis history for logged-in user
exports.getHistory = async (req, res, next) => {
  try {
    const userId = req.userId;
    const history = await getResumeHistory(userId);
    res.status(200).json(history);
  } catch (err) {
    console.error('History fetch error:', err);
    next(err);
  }
};

// Generate downloadable PDF report from analysis
exports.downloadPDF = async (req, res, next) => {
  try {
    const analysis = req.body.analysis;
    const pdfBuffer = await generatePDF(analysis);

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename=resume_report.pdf');
    res.send(pdfBuffer);
  } catch (err) {
    console.error('PDF generation error:', err);
    next(err);
  }
};
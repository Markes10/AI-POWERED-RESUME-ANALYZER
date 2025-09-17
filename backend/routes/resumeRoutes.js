const express = require('express');
const multer = require('multer');
const {
  uploadResume,
  getHistory,
  downloadPDF,
} = require('../controllers/resumeController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

// Configure multer for in-memory file upload
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Upload resume and analyze
router.post('/upload', authMiddleware, upload.single('resume'), uploadResume);

// Get resume analysis history
router.get('/history', authMiddleware, getHistory);

// Generate downloadable PDF report
router.post('/download-pdf', authMiddleware, downloadPDF);

module.exports = router; 

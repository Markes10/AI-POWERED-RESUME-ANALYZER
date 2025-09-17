const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const authRoutes = require('./routes/authRoutes');
const resumeRoutes = require('./routes/resumeRoutes');
const { errorHandler } = require('./middleware/errorHandler');

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/auth', authRoutes);
app.use('/resume', resumeRoutes);

// Health check
app.get('/', (req, res) => {
  res.send('Resume Analyzer API is running');
});

// Error handler
app.use(errorHandler);

module.exports = app; 
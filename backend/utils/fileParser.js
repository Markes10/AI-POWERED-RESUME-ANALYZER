const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const path = require('path');

const extractTextFromFile = async (buffer, filename) => {
  const ext = path.extname(filename).toLowerCase();

  try {
    if (ext === '.pdf') {
      const data = await pdfParse(buffer);
      return data.text;
    }

    if (ext === '.docx') {
      const result = await mammoth.extractRawText({ buffer });
      return result.value;
    }

    throw new Error('Unsupported file format. Please upload a .pdf or .docx file.');
  } catch (err) {
    console.error('File parsing error:', err.message);
    throw new Error('Failed to extract text from resume file');
  }
};

module.exports = extractTextFromFile;
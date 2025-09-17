const errorHandler = (err, req, res, next) => {
  console.error(`[ERROR] ${err.message}`);

  // Default to 500 if no status code is set
  const statusCode = res.statusCode && res.statusCode !== 200 ? res.statusCode : 500;

  res.status(statusCode).json({
    success: false,
    error: err.message || 'Internal Server Error',
  });
};

module.exports = { errorHandler }; 

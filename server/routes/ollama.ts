import { RequestHandler } from "express";

/**
 * Proxy health check to the Python FastAPI backend.
 * Returns the Ollama status reported by the Python server.
 */
export const handleOllamaStatus: RequestHandler = async (_req, res) => {
  const pythonApiUrl = process.env.PYTHON_API_URL || "http://localhost:8000";
  try {
    const response = await fetch(`${pythonApiUrl}/ollama/status`);
    if (response.ok) {
      const data = await response.json();
      res.json(data);
    } else {
      res.status(503).json({
        status: "error",
        message: "Python backend unavailable",
        models: [],
        current_model: "mistral",
        endpoint: "http://localhost:11434/api",
      });
    }
  } catch {
    // Python server not running — check Ollama directly
    try {
      const ollamaRes = await fetch("http://localhost:11434/api/tags");
      if (ollamaRes.ok) {
        const data = await ollamaRes.json();
        const models = (data.models || []).map((m: { name: string }) => m.name);
        res.json({
          status: "ok",
          models,
          current_model: process.env.OLLAMA_MODEL || "mistral",
          endpoint: "http://localhost:11434/api",
          message: `Ollama is running. ${models.length} model(s) available.`,
        });
      } else {
        throw new Error("Ollama returned non-200");
      }
    } catch {
      res.status(503).json({
        status: "error",
        models: [],
        current_model: "mistral",
        endpoint: "http://localhost:11434/api",
        message:
          "Ollama is not running. Install from https://ollama.ai and run: ollama serve && ollama pull mistral",
      });
    }
  }
};

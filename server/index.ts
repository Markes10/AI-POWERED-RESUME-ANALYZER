import "dotenv/config";
import express from "express";
import cors from "cors";
import { handleDemo } from "./routes/demo";
import { handleOllamaStatus } from "./routes/ollama";
import {
  handleAnalyzeSkills,
  handleOllamaModels,
  handleModelRecommendation,
} from "./routes/llm-orchestrator";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });

  app.get("/api/demo", handleDemo);

  // Ollama status check (checks both Python backend and direct Ollama)
  app.get("/api/ollama/status", handleOllamaStatus);

  // Free local LLM orchestration via Ollama
  app.post("/api/analyze/skills", handleAnalyzeSkills);
  app.get("/api/ollama/models", handleOllamaModels);
  app.get("/api/ollama/recommendation", handleModelRecommendation);

  return app;
}

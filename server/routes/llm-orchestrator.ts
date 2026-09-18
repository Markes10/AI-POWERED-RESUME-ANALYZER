import { RequestHandler, Response } from "express";

const MODEL_CHAIN = [
  { name: "phi3", priority: 1, description: "Lightweight, 3B parameters, fast", minVramGb: 3 },
  { name: "mistral", priority: 2, description: "General purpose, 7B parameters", minVramGb: 4 },
  { name: "llama3", priority: 3, description: "High quality, 8B parameters, best free option", minVramGb: 8 },
  { name: "nemotron", priority: 4, description: "NVIDIA model, 8B parameters", minVramGb: 6 },
] as const;

type ModelName = typeof MODEL_CHAIN[number]["name"];

export interface SystemInfo {
  totalMemoryGb: number;
  availableVramGb: number;
  cpuCores: number;
  modelRecommendation: ModelName;
}

export interface AnalyzeSkillsRequest {
  resumeText: string;
  targetRole?: string;
  extractor?: "skills" | "education" | "experience";
}

export interface AnalyzeSkillsResponse {
  success: boolean;
  model: ModelName;
  data: any;
  error?: string;
  estimatedTime: string;
}

/**
 * Check system information to determine available resources.
 * In a browser environment, returns default conservative values.
 * In Node.js environment, checks actual system resources.
 */
function getSystemInfo(): SystemInfo {
  let totalMemoryGb = 8;
  let availableVramGb = 0;
  let cpuCores = 4;

  if (typeof navigator === "undefined" && typeof process !== "undefined") {
    // Node.js environment
    const os = require("os");
    totalMemoryGb = Math.round(os.totalmem() / 1024 / 1024 / 1024);
    cpuCores = os.cpus().length || 4;
    // Check for GPU (simplified - would need nvidia-smi or similar in production)
    availableVramGb = 0;
  }

  // Determine model based on available VRAM
  let modelRecommendation: ModelName = "phi3"; // most conservative

  for (const model of MODEL_CHAIN) {
    if (availableVramGb >= model.minVramGb) {
      modelRecommendation = model.name;
      break;
    }
  }

  return {
    totalMemoryGb,
    availableVramGb: Math.round(availableVramGb * 10) / 10, // round to 1 decimal
    cpuCores,
    modelRecommendation,
  };
}

/**
 * Analyze skills from resume text using a free local LLM via Ollama.
 * Tries models in priority order, starting with system-appropriate model.
 */
export const handleAnalyzeSkills: RequestHandler = async (
  req,
  res
): Promise<Response> => {
  const { resumeText, targetRole = "software engineer", extractor = "skills" } =
    req.body;

  // Get system info for model selection
  const systemInfo = getSystemInfo();

  if (!resumeText || resumeText.trim().length === 0) {
    return res.status(400).json({
      success: false,
      model: "none" as ModelName,
      data: {},
      error: "Resume text is required",
      estimatedTime: "0ms",
      systemInfo,
    });
  }

  // Construct prompt based on extractor type
  let prompt = "";
  switch (extractor) {
    case "skills":
      prompt = `Extract all technical and soft skills from this resume. For each skill, provide:
- skill name
- proficiency level (Beginner, Intermediate, Advanced, Expert)
- years of experience if mentioned
- category (Technical, Soft, Language, Certification)

Target role: ${targetRole}

Resume text:
${resumeText}

Return as JSON array with: name, level, yearsExperience?, category.`;

      break;
    case "education":
      prompt = `Extract education information from this resume:
- Degree(s) obtained
- Institution(s)
- Graduation year(s)
- Any honors or awards

Target role: ${targetRole}

Resume text:
${resumeText}

Return as JSON array with: degree, institution, graduationYear, honors.`;

      break;
    case "experience":
      prompt = `Extract work experience from this resume:
- Job titles
- Companies
- Employment dates
- Key responsibilities and achievements

Target role: ${targetRole}

Resume text:
${resumeText}

Return as JSON array with: title, company, startDate, endDate, current?, responsibilities[].`;

      break;
    default:
      prompt = `Extract skills from this resume for ${targetRole} role.`;

  }

  // Start with the system-recommended model, then fall back through the chain
  const recommendedModel = MODEL_CHAIN.find(m => m.name === systemInfo.modelRecommendation) || MODEL_CHAIN[0];
  const modelOrder = [
    recommendedModel,
    ...MODEL_CHAIN.filter(m => m.name !== systemInfo.modelRecommendation),
  ];

  // Try each model in the order
  for (const modelConfig of modelOrder) {
    try {
      const ollamaResponse = await fetch("http://localhost:11434/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: modelConfig.name,
          messages: [
            {
              role: "user",
              content: prompt,
            },
          ],
          stream: false,
          options: {
            temperature: 0.3,
            num_ctx: 4096,
          },
        }),
      });

      if (!ollamaResponse.ok) {
        const errorText = await ollamaResponse.text();
        throw new Error(`Model ${modelConfig.name} failed: ${errorText}`);
      }

      const result = await ollamaResponse.json();
      const content = result.message?.content || "";

      if (!content) {
        continue; // Try next model
      }

      // Try to parse as JSON
      let parsed: any;
      try {
        parsed = JSON.parse(content);
      } catch {
        // If not valid JSON, return raw text
        parsed = { rawOutput: content };
      }

      return res.status(200).json({
        success: true,
        model: modelConfig.name,
        data: parsed,
        estimatedTime: `${modelConfig.priority * 2}s approx`,
        systemInfo,
      });
    } catch (error) {
      console.log(`Model ${modelConfig.name} unavailable, trying next...`);
      continue; // Try next model in chain
    }
  }

  // All models failed
  return res.status(503).json({
    success: false,
    model: "none" as ModelName,
    data: {},
    error: "All free local models unavailable. Please ensure Ollama is running with at least one model installed.",
    estimatedTime: "0ms",
    systemInfo,
  });
};

/**
 * Check which Ollama models are available and healthy.
 */
export const handleOllamaModels: RequestHandler = async (_req, res) => {
  try {
    const response = await fetch("http://localhost:11434/api/tags", {
      method: "GET",
    });

    if (!response.ok) {
      return res.status(503).json({
        ollamaRunning: false,
        message: "Ollama server not accessible at localhost:11434",
      });
    }

    const data = await response.json();
    const models = (data.models || []).map(
      (m: { name: string }) => m.name
    );

    // Check which models from our chain are available
    const availableModels = MODEL_CHAIN
      .filter((model) => models.includes(model.name))
      .map((model) => ({
        ...model,
        available: true,
      }));

    const unavailableModels = MODEL_CHAIN
      .filter((model) => !models.includes(model.name))
      .map((model) => ({
        ...model,
        available: false,
      }));

    // Get system info for recommendation
    const systemInfo = getSystemInfo();

    return res.status(200).json({
      ollamaRunning: true,
      systemInfo,
      modelsList: models,
      chain: {
        available: availableModels,
        unavailable: unavailableModels,
        recommended:
          availableModels.find((m) => m.name === "llama3") ||
          availableModels.find((m) => m.name === "mistral") ||
          availableModels.find((m) => m.name === systemInfo.modelRecommendation) ||
          availableModels[0],
      },
    });
  } catch (error) {
    return res.status(503).json({
      ollamaRunning: false,
      message: "Ollama connection error",
      error: error instanceof Error ? error.message : String(error),
    });
  }
};

/**
 * Get model recommendation based on task complexity and system info.
 */
export const handleModelRecommendation: RequestHandler = (
  req,
  res
) => {
  const complexity = (req.query.complexity as "simple" | "medium" | "complex") ||
    "medium";

  const systemInfo = getSystemInfo();

  const recommendations = {
    simple: {
      primary: "phi3",
      fallback: "mistral",
      reason: "Fastest, good for basic skill extraction",
      estimatedCost: "$0/month (free local)",
      requiresVramGb: 3,
    },
    medium: {
      primary: systemInfo.availableVramGb >= 8 ? "llama3" : "mistral",
      fallback: "phi3",
      reason: systemInfo.availableVramGb >= 8
        ? "Good balance of speed and quality for skill gap analysis"
        : "Good balance for systems with limited VRAM",
      estimatedCost: "$0/month (free local)",
      requiresVramGb: systemInfo.availableVramGb >= 8 ? 8 : 4,
    },
    complex: {
      primary: systemInfo.availableVramGb >= 8 ? "llama3" : "nemotron",
      fallback: "mistral",
      reason: systemInfo.availableVramGb >= 8
        ? "Best quality for roadmap generation and complex analysis"
        : "Best available for system VRAM capacity",
      estimatedCost: "$0/month (free local)",
      requiresVramGb: systemInfo.availableVramGb >= 8 ? 8 : 6,
    },
  };

  const rec = recommendations[complexity] || recommendations.medium;

  return res.status(200).json({
    complexity,
    systemInfo,
    ...rec,
    fullChain: MODEL_CHAIN.map((m) => ({
      name: m.name,
      priority: m.priority,
      description: m.description,
      minVramGb: m.minVramGb,
    })),
  });
};
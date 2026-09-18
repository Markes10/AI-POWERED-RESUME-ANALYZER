"""
LLM utilities for interacting with Ollama running Mistral model.

- Generate text completions using Mistral
- Supports async calls with httpx
- Free and open source
- Health check endpoint for frontend status polling
"""

import os
import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# -------------------------------
# Config
# -------------------------------
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")
TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))


# -------------------------------
# Health Check
# -------------------------------
async def health_check() -> Dict[str, Any]:
    """
    Check if Ollama server is running and which models are available.
    Returns: {"status": "ok"|"error", "models": [...], "message": "..."}
    """
    base_url = OLLAMA_ENDPOINT.rstrip("/api").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "status": "ok",
                    "models": models,
                    "current_model": MODEL_NAME,
                    "endpoint": OLLAMA_ENDPOINT,
                    "message": f"Ollama is running. {len(models)} model(s) available."
                }
            else:
                return {
                    "status": "error",
                    "models": [],
                    "current_model": MODEL_NAME,
                    "endpoint": OLLAMA_ENDPOINT,
                    "message": f"Ollama responded with status {resp.status_code}"
                }
    except httpx.ConnectError:
        return {
            "status": "error",
            "models": [],
            "current_model": MODEL_NAME,
            "endpoint": OLLAMA_ENDPOINT,
            "message": (
                f"Cannot connect to Ollama at {OLLAMA_ENDPOINT}. "
                "Please install and start Ollama: https://ollama.ai"
            )
        }
    except Exception as e:
        return {
            "status": "error",
            "models": [],
            "current_model": MODEL_NAME,
            "endpoint": OLLAMA_ENDPOINT,
            "message": f"Ollama health check failed: {str(e)}"
        }


# -------------------------------
# LLM Client
# -------------------------------
async def generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: Optional[str] = None
) -> str:
    """
    Call Ollama server to generate text using the configured model.
    Uses /api/generate endpoint (best for single-turn prompts).
    """
    use_model = model or MODEL_NAME
    payload = {
        "model": use_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        }
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.post(f"{OLLAMA_ENDPOINT}/generate", json=payload)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
            return data.get("response", "").strip()
        except httpx.ConnectError:
            msg = (
                f"[Ollama Unavailable] Cannot connect to Ollama at {OLLAMA_ENDPOINT}. "
                "Please run: ollama serve"
            )
            logger.warning(msg)
            return msg
        except httpx.TimeoutException:
            msg = (
                f"[Ollama Timeout] The model '{use_model}' took too long to respond. "
                "Try running: ollama pull mistral"
            )
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"[Ollama Error] {str(e)}"
            logger.exception("Ollama generate call failed")
            return msg


async def chat(
    messages: List[Dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.7,
    model: Optional[str] = None
) -> str:
    """
    Call Ollama server with chat-style interface.
    Expects messages: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    Uses /api/chat endpoint with correct Ollama message format.
    """
    use_model = model or MODEL_NAME

    # Ollama /api/chat expects: {"model": "...", "messages": [...], "stream": false}
    payload = {
        "model": use_model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        }
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.post(f"{OLLAMA_ENDPOINT}/chat", json=payload)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
            # Ollama chat response: {"message": {"role": "assistant", "content": "..."}}
            message = data.get("message", {})
            if isinstance(message, dict):
                return message.get("content", "").strip()
            return str(data.get("response", "")).strip()
        except httpx.ConnectError:
            msg = (
                f"[Ollama Unavailable] Cannot connect to Ollama at {OLLAMA_ENDPOINT}. "
                "Please run: ollama serve"
            )
            logger.warning(msg)
            return msg
        except httpx.TimeoutException:
            msg = (
                f"[Ollama Timeout] The model '{use_model}' took too long to respond. "
                "Try running: ollama pull mistral"
            )
            logger.warning(msg)
            return msg
        except Exception as e:
            msg = f"[Ollama Error] {str(e)}"
            logger.exception("Ollama chat call failed")
            return msg


# -------------------------------
# Specialized HR Functions
# -------------------------------

async def analyze_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    AI Resume-Job Fit Analysis using Ollama (Mistral)
    """
    prompt = f"""Analyze the fit between this resume and job description.

Resume:
{resume_text[:3000]}

Job Description:
{job_description[:2000]}

Provide a structured analysis with:
1. Match Score (0-100)
2. Key Skills Match (list matched skills)
3. Experience Alignment (brief description)
4. Missing Skills (list gaps)
5. Recommendations (3-5 actionable items)

Format your response clearly with each section labeled."""

    response = await generate(prompt, max_tokens=800)
    return {
        "analysis": response,
        "model": MODEL_NAME
    }


async def predict_turnover_risk(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predictive Turnover Analysis using Ollama (Mistral)
    """
    prompt = f"""Analyze turnover risk for this employee profile:
{str(employee_data)}

Provide:
1. Risk Level (Low/Medium/High)
2. Key Risk Factors (bullet points)
3. Retention Recommendations (3-5 specific actions)

Be concise and actionable."""

    response = await generate(prompt, max_tokens=600)
    return {
        "analysis": response,
        "model": MODEL_NAME
    }


async def generate_interview_questions(job_title: str, skills: List[str]) -> Dict[str, Any]:
    """
    AI Interview Question Generator using Ollama (Mistral)
    """
    prompt = f"""Generate interview questions for:
Position: {job_title}
Required Skills: {', '.join(skills[:10])}

Provide:
1. Technical Questions (3-5 questions)
2. Behavioral Questions (3-5 questions)
3. Situational Questions (2-3 questions)
4. Follow-up Prompts for each

Format clearly with numbered questions."""

    response = await generate(prompt, max_tokens=800)
    return {
        "questions": response,
        "model": MODEL_NAME
    }


async def create_onboarding_plan(role: str, department: str) -> Dict[str, Any]:
    """
    Onboarding Journey Generator using Ollama (Mistral)
    """
    prompt = f"""Create a 30-60-90 day onboarding plan for:
Role: {role}
Department: {department}

Include:
1. Week 1: First week schedule and priorities
2. Month 1: Key learning objectives
3. Months 2-3: Growth milestones
4. Required Resources and Tools
5. Success Metrics

Be specific and actionable."""

    response = await generate(prompt, max_tokens=800)
    return {
        "plan": response,
        "model": MODEL_NAME
    }


async def generate_performance_feedback(performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performance Feedback Generator using Ollama (Mistral)
    """
    prompt = f"""Generate constructive performance feedback based on:
{str(performance_data)}

Include:
1. Key Achievements (specific examples)
2. Areas for Improvement (constructive, not critical)
3. Development Goals (SMART goals)
4. Action Items (specific next steps)

Use professional, supportive tone."""

    response = await generate(prompt, max_tokens=700)
    return {
        "feedback": response,
        "model": MODEL_NAME
    }


async def analyze_compensation_fairness(compensation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compensation Fairness Analysis using Ollama (Mistral)
    """
    prompt = f"""Analyze compensation fairness across these records:
{str(compensation_data[:20])}

Provide:
1. Pay Equity Analysis (any disparities found)
2. Market Comparison (general assessment)
3. Internal Fairness (relative assessment)
4. Recommendations (specific actions to address gaps)

Focus on objective metrics."""

    response = await generate(prompt, max_tokens=700)
    return {
        "analysis": response,
        "model": MODEL_NAME
    }


async def recommend_learning_path(employee_profile: Dict[str, Any], career_goals: str) -> Dict[str, Any]:
    """
    Learning Path Recommender using Ollama (Mistral)
    """
    prompt = f"""Recommend a learning path for:
Profile: {str(employee_profile)}
Career Goals: {career_goals}

Provide:
1. Top 5 Recommended Courses (with why each matters)
2. Skill Development Priority Order
3. Timeline (realistic, 6-12 months)
4. Free and Paid Resources
5. Success Metrics

Be specific with course/certification names."""

    response = await generate(prompt, max_tokens=800)
    return {
        "recommendations": response,
        "model": MODEL_NAME
    }


async def detect_attendance_anomalies(attendance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Attendance Anomaly Detection using Ollama (Mistral)
    """
    prompt = f"""Analyze these attendance records for anomalies:
{str(attendance_data[:30])}

Identify:
1. Unusual Patterns (specific dates/times)
2. Potential Issues (absenteeism, lateness trends)
3. Risk Assessment (low/medium/high)
4. Recommended Actions

Be specific about what constitutes an anomaly."""

    response = await generate(prompt, max_tokens=600)
    return {
        "analysis": response,
        "model": MODEL_NAME
    }


async def analyze_diversity_inclusion(workforce_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Diversity & Inclusion Analytics using Ollama (Mistral)
    """
    prompt = f"""Analyze diversity and inclusion metrics:
{str(workforce_data)}

Provide:
1. Diversity Metrics Summary (representation across groups)
2. Inclusion Indicators (based on available data)
3. Gap Analysis (where improvement is needed)
4. Specific Recommendations (5 actionable items)

Use objective, data-driven language."""

    response = await generate(prompt, max_tokens=700)
    return {
        "analysis": response,
        "model": MODEL_NAME
    }


async def chat_with_resume(resume_text: str, question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Chat about a specific resume using Ollama.
    Supports conversation history for multi-turn dialogue.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert HR assistant analyzing a candidate's resume. "
                "Answer questions about the resume accurately and helpfully. "
                "If something is not in the resume, say so clearly.\n\n"
                f"Resume Content:\n{resume_text[:4000]}"
            )
        }
    ]

    # Add conversation history
    if history:
        messages.extend(history[-10:])  # Keep last 10 messages for context

    # Add current question
    messages.append({"role": "user", "content": question})

    return await chat(messages, max_tokens=500)

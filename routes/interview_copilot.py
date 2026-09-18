from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any, List
from services import vllm_client, stt_utils, sentiment_utils


def generate_questions(job_role: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate interview questions from a job-role dictionary."""
    title = job_role.get("title", "Position")
    requirements = job_role.get("requirements", []) or []
    responsibilities = job_role.get("responsibilities", []) or []

    questions: List[Dict[str, str]] = []

    for idx, requirement in enumerate(requirements[:3], start=1):
        questions.append({
            "category": "technical",
            "question": f"Can you walk me through your experience with {requirement}?"
        })

    for idx, responsibility in enumerate(responsibilities[:2], start=1):
        questions.append({
            "category": "behavioral",
            "question": f"Describe a time you handled a situation involving {responsibility}."
        })

    questions.extend([
        {
            "category": "technical",
            "question": f"How would you approach building and scaling a solution for {title}?"
        },
        {
            "category": "behavioral",
            "question": "Tell me about a time you mentored a teammate or handled conflict on a project."
        },
        {
            "category": "situational",
            "question": "What would you do if a critical deadline shifted while your team was mid-delivery?"
        },
    ])

    return questions[:6]


def analyze_feedback(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a lightweight hiring recommendation from interview feedback."""
    technical_scores = feedback.get("technical_skills", {}) or {}
    soft_scores = feedback.get("soft_skills", {}) or {}

    technical_values = list(technical_scores.values())
    soft_values = list(soft_scores.values())

    all_scores = technical_values + soft_values
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

    strengths = []
    for skill, score in sorted(technical_scores.items(), key=lambda item: item[1], reverse=True)[:2]:
        strengths.append(f"Strong {skill} capability (score {score}/5)")
    for skill, score in sorted(soft_scores.items(), key=lambda item: item[1], reverse=True)[:2]:
        strengths.append(f"Good {skill} skills (score {score}/5)")

    areas_for_improvement = []
    for skill, score in sorted({**technical_scores, **soft_scores}.items(), key=lambda item: item[1]):
        if score < 3:
            areas_for_improvement.append(f"Improve {skill}")

    if overall_score >= 4.0:
        hiring_recommendation = "strong_hire"
    elif overall_score >= 3.0:
        hiring_recommendation = "consider"
    else:
        hiring_recommendation = "reject"

    return {
        "overall_score": round(overall_score, 2),
        "strengths": strengths[:4],
        "areas_for_improvement": areas_for_improvement[:4],
        "hiring_recommendation": hiring_recommendation,
    }

router = APIRouter(prefix="/interview", tags=["Interview Co-pilot"])


@router.post("/chat")
async def interview_chat(prompt: str):
    reply = await vllm_client.chat_completion([{"role": "user", "content": prompt}])
    return {"reply": reply}


@router.post("/stt/stream")
async def stt_stream(file: UploadFile = File(...)) -> Dict[str, Any]:
    audio_bytes = await file.read()
    transcript = stt_utils.transcribe(audio_bytes)
    return transcript


@router.post("/sentiment")
def sentiment_analysis(payload: Dict[str, str]):
    text = payload.get("text", "")
    result = sentiment_utils.analyze_sentiment(text)
    return result

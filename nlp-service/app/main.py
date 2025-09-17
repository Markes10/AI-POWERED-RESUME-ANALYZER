from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import extract, match, feedback

app = FastAPI(
    title="Resume Analyzer NLP Service",
    description="API for analyzing resumes, computing match scores, and collecting feedback",
    version="1.0.0"
)

# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(extract.router, prefix="/resume", tags=["Analysis"])
app.include_router(match.router, prefix="/resume", tags=["Matching"])
app.include_router(feedback.router, prefix="/resume", tags=["Feedback"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "NLP service is running"}
import pytest
from app.services.matcher import compute_match_score

def test_match_score_basic():
    resume = "Experienced Python developer with knowledge of APIs and cloud deployment."
    job = "Looking for a Python developer skilled in cloud infrastructure and REST APIs."
    score = compute_match_score(resume, job)
    assert 0.0 <= score <= 1.0
    assert score > 0.3  # Expect some semantic overlap 
    
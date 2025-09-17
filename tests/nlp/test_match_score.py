import pytest
from app.services.matcher import compute_match_score

def test_score_with_similar_texts():
    resume = "Experienced backend developer with Python and Docker skills."
    job = "Looking for a Python backend developer familiar with Docker."
    score = compute_match_score(resume, job)
    assert 0.0 <= score <= 1.0
    assert score > 0.5

def test_score_with_dissimilar_texts():
    resume = "Graphic designer with Adobe Photoshop experience."
    job = "Seeking a backend engineer with Python and cloud skills."
    score = compute_match_score(resume, job)
    assert score < 0.3 
    
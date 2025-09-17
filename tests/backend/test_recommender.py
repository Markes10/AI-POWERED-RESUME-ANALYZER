from app.services.recommender import find_missing_keywords, generate_suggestions

def test_missing_keywords_detection():
    resume = "Python developer with cloud experience"
    job = "Python developer with cloud and API experience"
    missing = find_missing_keywords(resume, job)
    assert "api" in missing

def test_suggestions_generation():
    missing = ["api", "docker"]
    suggestions = generate_suggestions(missing)
    assert len(suggestions) == 2
    assert "Consider including the keyword 'api'" in suggestions[0].lower() 
    
from app.services.recommender import find_missing_keywords, generate_suggestions

def test_missing_keywords_logic():
    resume = "Python developer with cloud experience"
    job = "Python developer with cloud, API, and CI/CD experience"
    missing = find_missing_keywords(resume, job)
    assert "api" in missing
    assert "ci/cd" not in missing  # Should be normalized

def test_suggestion_generation():
    missing = ["api", "docker"]
    suggestions = generate_suggestions(missing)
    assert len(suggestions) == 2
    assert "Consider including the keyword 'api'" in suggestions[0] 
    assert "Consider including the keyword 'docker'" in suggestions[1]
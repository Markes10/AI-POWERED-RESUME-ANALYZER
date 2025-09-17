import pytest

@pytest.fixture(scope="session")
def sample_resume_text():
    return "Skilled in Python, Docker, and cloud deployment."

@pytest.fixture(scope="session")
def sample_job_description():
    return "We need a backend engineer with Python, Docker, and API experience." 

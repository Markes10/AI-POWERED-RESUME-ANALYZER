"""
Tests for ML/AI features including skill extraction and job matching
"""
import pytest
import numpy as np
from services.skill_extractor import extract_skills
from services.embedding_service import embed_text, calculate_similarity
from services.nlp_service import preprocess_text, extract_entities

@pytest.fixture
def sample_job_descriptions():
    return [
        """
        Senior ML Engineer
        Requirements:
        - 5+ years experience in ML/AI
        - Expert in Python, PyTorch, TensorFlow
        - Experience with NLP and computer vision
        - Strong mathematical background
        """,
        """
        Frontend Developer
        Requirements:
        - 3+ years experience in web development
        - Expert in React, TypeScript, and Redux
        - Experience with UI/UX design
        - Knowledge of responsive design
        """
    ]

def test_skill_extraction_advanced(sample_resume_text):
    """Test advanced skill extraction features"""
    skills = extract_skills(sample_resume_text)
    
    # Check technical skills
    tech_skills = [s for s in skills if s in ["Python", "React", "FastAPI", "SQL"]]
    assert len(tech_skills) >= 3
    
    # Check soft skills
    soft_skills = [s for s in skills if s in ["Leadership", "Communication", "Team Management"]]
    assert len(soft_skills) > 0

def test_text_embedding():
    """Test text embedding functionality"""
    text1 = "Python developer with ML experience"
    text2 = "Machine learning engineer proficient in Python"
    
    # Generate embeddings
    embedding1 = embed_text(text1)
    embedding2 = embed_text(text2)
    
    # Check embedding properties
    assert isinstance(embedding1, list)
    assert isinstance(embedding2, list)
    assert len(embedding1) == len(embedding2)
    
    # Check similarity
    similarity = calculate_similarity(embedding1, embedding2)
    assert 0 <= similarity <= 1
    assert similarity > 0.5  # Should be relatively similar

def test_job_matching_similarity(sample_resume_text, sample_job_descriptions):
    """Test job matching similarity calculations"""
    resume_embedding = embed_text(sample_resume_text)
    
    similarities = []
    for job_desc in sample_job_descriptions:
        job_embedding = embed_text(job_desc)
        similarity = calculate_similarity(resume_embedding, job_embedding)
        similarities.append(similarity)
    
    # Check that similarities are valid
    assert all(0 <= s <= 1 for s in similarities)
    
    # Check that different job descriptions have different similarities
    assert len(set(similarities)) > 1

@pytest.mark.parametrize("text,expected_entities", [
    (
        "Senior Python Developer at Google with 5 years experience",
        {"job_title": "Senior Python Developer", "company": "Google", "years": "5"}
    ),
    (
        "Machine Learning Engineer with PhD in Computer Science",
        {"job_title": "Machine Learning Engineer", "education": "PhD", "field": "Computer Science"}
    )
])
def test_entity_extraction(text, expected_entities):
    """Test named entity extraction from text"""
    entities = extract_entities(text)
    for key, value in expected_entities.items():
        assert key in entities
        assert entities[key] == value

def test_text_preprocessing():
    """Test text preprocessing pipeline"""
    raw_text = """
    SENIOR SOFTWARE ENGINEER
    
    * Python development
    * Cloud platforms (AWS)
    * Email: test@example.com
    * Phone: (123) 456-7890
    """
    
    processed_text = preprocess_text(raw_text)
    
    # Check text cleaning
    assert "EMAIL:" not in processed_text
    assert "PHONE:" not in processed_text
    assert "software engineer" in processed_text.lower()
    assert "python" in processed_text.lower()

def test_skill_matching_with_variants():
    """Test skill matching with different variations"""
    variants = [
        ("Python programming", ["Python"]),
        ("ReactJS and React Native", ["React", "React Native"]),
        ("AWS (Amazon Web Services)", ["AWS"]),
        ("ML/AI experience", ["Machine Learning", "Artificial Intelligence"]),
        ("REST APIs", ["REST", "API"]),
    ]
    
    for input_text, expected_skills in variants:
        skills = extract_skills(input_text)
        for skill in expected_skills:
            assert any(s.lower() == skill.lower() for s in skills)
import re
from typing import List


def clean_and_tokenize(text: str) -> List[str]:
    """
    Lowercase, remove punctuation, and split into words.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    return list(set(tokens))  # Remove duplicates


def find_missing_keywords(resume_text: str, job_description: str) -> List[str]:
    """
    Identify keywords from the job description that are missing in the resume.
    """
    resume_tokens = clean_and_tokenize(resume_text)
    job_tokens = clean_and_tokenize(job_description)

    missing = [word for word in job_tokens if word not in resume_tokens and len(word) > 3]
    return missing


def generate_suggestions(missing_keywords: List[str]) -> List[str]:
    """
    Generate improvement suggestions based on missing keywords.
    """
    suggestions = []
    for keyword in missing_keywords:
        suggestions.append(f"Consider including the keyword '{keyword}' if relevant to your experience.")
    return suggestions
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def preprocess(text: str) -> str:
    """
    Basic text preprocessing: lowercase, remove non-alphanumeric, collapse whitespace.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Compute semantic similarity score between resume and job description using TF-IDF + cosine similarity.
    Returns a float between 0 and 1.
    """
    resume_clean = preprocess(resume_text)
    job_clean = preprocess(job_description)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity), 4) 

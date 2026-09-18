import re
import numpy as np
from typing import List, Dict, Any


def preprocess_text(text: str) -> str:
    """Clean raw text for downstream NLP and skill extraction."""
    if not text:
        return ""

    cleaned = text.replace("\r", " ")
    cleaned = re.sub(r"\bEMAIL:\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bPHONE:\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\b(?:email|phone)\s*:\s*[^\n]+", " ", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned


def extract_entities(text: str) -> Dict[str, Any]:
    """Best-effort entity extraction used by tests and lightweight features."""
    if not text:
        return {}

    normalized = preprocess_text(text)
    entities: Dict[str, Any] = {}

    title_patterns = [
        r"([A-Z][A-Za-z0-9&./+-]*(?:\s+[A-Z][A-Za-z0-9&./+-]*)*\s+(?:Developer|Engineer|Analyst|Manager|Scientist|Architect|Lead))",
        r"([A-Z][A-Za-z0-9&./+-]*(?:\s+[A-Z][A-Za-z0-9&./+-]*)*\s+(?:Developer|Engineer|Analyst|Manager|Scientist|Architect|Lead)(?:\s+at)? )"
    ]

    title_match = None
    for pattern in title_patterns:
        title_match = re.search(pattern, normalized)
        if title_match:
            break

    if title_match:
        entities["job_title"] = title_match.group(1).strip()

    company_match = re.search(r"\bat\s+([A-Z][A-Za-z0-9&.-]+)", normalized, flags=re.IGNORECASE)
    if company_match:
        entities["company"] = company_match.group(1).strip()

    years_match = re.search(r"(\d+)\s+years?", normalized, flags=re.IGNORECASE)
    if years_match:
        entities["years"] = years_match.group(1)

    education_match = re.search(r"\b(PhD|Master|Bachelor|B\.S\.|M\.S\.|MBA)\b", normalized, flags=re.IGNORECASE)
    if education_match:
        entities["education"] = education_match.group(1).strip()

    field_match = re.search(r"\b(?:in|of)\s+([A-Z][A-Za-z\s&]+)", normalized)
    if field_match and not entities.get("company"):
        entities["field"] = field_match.group(1).strip()

    return entities


class NLPService:
    """
    Provides NLP capabilities including:
    - Text classification
    - Named Entity Recognition
    - Sentiment Analysis
    - Text Embeddings
    - Question Answering
    """
    def __init__(self):
        # Keep attributes None until used; heavy imports happen in getters
        self.sentiment_analyzer = None
        self.ner_pipeline = None
        self.qa_pipeline = None
        self.text_classifier = None
        self.embedding_model = None

    def _get_pipeline(self, task: str):
        """Return a transformers pipeline for the given task, lazily importing transformers."""
        try:
            from transformers import pipeline  # type: ignore
        except Exception:
            return None
        try:
            return pipeline(task)
        except Exception:
            return None

    def _get_embedding_model(self):
        """Lazily load and return a SentenceTransformer model or None."""
        if self.embedding_model is not None:
            return self.embedding_model
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception:
            return None
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.embedding_model = None
        return self.embedding_model
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        if self.sentiment_analyzer is None:
            self.sentiment_analyzer = self._get_pipeline("sentiment-analysis")
        if self.sentiment_analyzer is None:
            return {"label": "neutral", "score": 0.0}
        result = self.sentiment_analyzer(text)[0]
        return {
            'label': result['label'],
            'score': result['score']
        }
        
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from .text"""
        if self.ner_pipeline is None:
            self.ner_pipeline = self._get_pipeline("ner")
        if self.ner_pipeline is None:
            return []
        return self.ner_pipeline(text)
        
    def get_embedding(self, text: str) -> np.ndarray:
        """Get text embeddings"""
        model = self._get_embedding_model()
        if model is None:
            return np.zeros(384)
        return model.encode(text)
        
    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        """Answer questions based on context"""
        if self.qa_pipeline is None:
            self.qa_pipeline = self._get_pipeline("question-answering")
        if self.qa_pipeline is None:
            return {"answer": "", "score": 0.0, "start": 0, "end": 0}
        result = self.qa_pipeline(question=question, context=context)
        return {
            'answer': result['answer'],
            'score': result['score'],
            'start': result['start'],
            'end': result['end']
        }
        
    def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify text into predefined categories"""
        if self.text_classifier is None:
            self.text_classifier = self._get_pipeline("text-classification")
        if self.text_classifier is None:
            return {"label": "unknown", "score": 0.0}
        result = self.text_classifier(text)[0]
        return {
            'label': result['label'],
            'score': result['score']
        }

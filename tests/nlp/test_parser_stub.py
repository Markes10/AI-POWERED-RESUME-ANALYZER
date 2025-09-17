import os
from app.services.parser import extract_text_from_pdf, extract_text_from_docx

def test_pdf_parser_stub():
    path = "tests/nlp/sample_resume.pdf"
    if os.path.exists(path):
        text = extract_text_from_pdf(path)
        assert isinstance(text, str)
        assert len(text) > 20

def test_docx_parser_stub():
    path = "tests/nlp/sample_resume.docx"
    if os.path.exists(path):
        text = extract_text_from_docx(path)
        assert isinstance(text, str)
        assert len(text) > 20
        assert "python" in text.lower()
        assert "docker" in text.lower()
import os
from app.services.parser import extract_text_from_pdf, extract_text_from_docx

def test_pdf_extraction():
    sample_pdf = "tests/backend/sample_resume.pdf"
    if os.path.exists(sample_pdf):
        text = extract_text_from_pdf(sample_pdf)
        assert isinstance(text, str)
        assert len(text) > 20

def test_docx_extraction():
    sample_docx = "tests/backend/sample_resume.docx"
    if os.path.exists(sample_docx):
        text = extract_text_from_docx(sample_docx)
        assert isinstance(text, str)
        assert len(text) > 20 
        
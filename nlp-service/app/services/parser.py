import os
import docx2txt
import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[parser] PDF extraction failed: {e}")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using docx2txt.
    """
    try:
        text = docx2txt.process(file_path)
        return text.strip()
    except Exception as e:
        print(f"[parser] DOCX extraction failed: {e}")
        return ""


def extract_resume_text(file_path: str) -> str:
    """
    Determines file type and extracts resume text accordingly.
    Supports PDF and DOCX formats.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}") 
    
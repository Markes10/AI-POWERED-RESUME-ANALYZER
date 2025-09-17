from app.utils.text import normalize_text, tokenize

def test_normalize_text():
    raw = "Python, Docker & APIs!"
    clean = normalize_text(raw)
    assert clean == "python docker apis"

def test_tokenize_output():
    text = "Python developer with Python and Docker experience"
    tokens = tokenize(text)
    assert "python" in tokens
    assert "docker" in tokens
    assert len(tokens) >= 3 
    assert all(isinstance(token, str) for token in tokens) 
    assert all(token.islower() for token in tokens) 
    assert all(token.isalpha() for token in tokens) 
    assert len(set(tokens)) == len(tokens) 
    assert tokens == list(dict.fromkeys(tokens)) 
    assert len(tokens) == len(text.split()) - 2  # "with" and "and" are removed 
    assert "developer" in tokens 
    assert "experience" in tokens 
    assert "with" not in tokens 
    assert "and" not in tokens 
    assert "python" in tokens  # Check for duplicates removal 
    assert tokens.count("python") == 1  # Ensure "python" appears only once 
    assert all(len(token) > 1 for token in tokens)  # No single-character tokens 
    assert all(token not in ["the", "is", "at", "which", "on"] for token in tokens)  # Common stop words removed
    assert all(token.isascii() for token in tokens)  # All tokens are ASCII
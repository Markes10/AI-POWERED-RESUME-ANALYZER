"""
LLM wrapper with support for Ollama (primary), OpenAI and Gemini (fallbacks).

Priority order:
1. Ollama (local, free) — uses OLLAMA_ENDPOINT env var
2. OpenAI — uses OPENAI_API_KEY env var
3. Gemini — uses GEMINI_API_KEY + GEMINI_ENDPOINT env vars
"""
import os
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    openai = None


def _is_ollama_available() -> bool:
    """Quick synchronous check if Ollama endpoint is reachable."""
    endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api")
    base_url = endpoint.rstrip("/api").rstrip("/")
    try:
        import urllib.request
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.getcode() == 200
    except Exception:
        return False


def call_llm(prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> str:
    """Call a configured LLM and return text response.

    Priority:
    1. Ollama (if OLLAMA_ENDPOINT is set and server is reachable)
    2. OpenAI (if OPENAI_API_KEY is set)
    3. Gemini (if GEMINI_API_KEY and GEMINI_ENDPOINT are set)
    """

    # -------------------------------------------------------
    # 1. Try Ollama first (local, free, no API key required)
    # -------------------------------------------------------
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api")
    ollama_model = model or os.getenv("OLLAMA_MODEL", "mistral")

    if ollama_endpoint:
        try:
            import httpx
            payload = {
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2"))
                }
            }
            timeout = float(os.getenv("OLLAMA_TIMEOUT", "60"))
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(f"{ollama_endpoint}/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data.get("response", "").strip()
                    if text:
                        logger.info("LLM call succeeded via Ollama (%s)", ollama_model)
                        return text
        except Exception as e:
            logger.debug("Ollama unavailable, trying next backend: %s", e)

    # -------------------------------------------------------
    # 2. Try OpenAI
    # -------------------------------------------------------
    if os.getenv("OPENAI_API_KEY") and _OPENAI_AVAILABLE:
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            resp = openai.ChatCompletion.create(
                model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            logger.info("LLM call succeeded via OpenAI")
            return resp.choices[0].message.content
        except Exception:
            logger.exception("OpenAI call failed")

    # -------------------------------------------------------
    # 3. Try Gemini via REST API
    # -------------------------------------------------------
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_endpoint = os.getenv("GEMINI_ENDPOINT")
    gemini_model = model or os.getenv("GEMINI_MODEL", "gemini-pro")

    if gemini_key and gemini_endpoint:
        payload = {
            "model": gemini_model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2"))
        }
        headers = {
            "Authorization": f"Bearer {gemini_key}",
            "Content-Type": "application/json"
        }
        try:
            import httpx
            with httpx.Client(timeout=30.0) as client:
                r = client.post(gemini_endpoint, json=payload, headers=headers)
                if r.status_code < 400:
                    data = r.json()
                    # Parse common Gemini/PaLM response shapes
                    if isinstance(data, dict):
                        if "candidates" in data:
                            for c in data["candidates"]:
                                for key in ("content", "text", "message", "output"):
                                    if key in c and c[key]:
                                        v = c[key]
                                        if isinstance(v, dict) and "text" in v:
                                            return v["text"]
                                        return str(v)
                        for key in ("text", "output", "response", "content"):
                            if key in data and data[key]:
                                return str(data[key])
                    logger.info("LLM call succeeded via Gemini")
                    return str(data)
        except Exception:
            logger.exception("Gemini call failed")

    raise RuntimeError(
        "No LLM backend available. "
        "Please either:\n"
        "  1. Install Ollama (https://ollama.ai) and run: ollama serve && ollama pull mistral\n"
        "  2. Set OPENAI_API_KEY in .env\n"
        "  3. Set GEMINI_API_KEY + GEMINI_ENDPOINT in .env"
    )


async def call_llm_async(prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> str:
    """Async wrapper for call_llm. Tries Ollama first via httpx async."""
    from services.llm_utils import generate as ollama_generate
    return await ollama_generate(prompt, max_tokens=max_tokens, model=model)

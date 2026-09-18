"""
Speecfrom typing import Dict, Any

# Whisper
try:
    import whisper
    _whisper_available = True
except ImportError:
    _whisper_available = False

# Vosk
try:
    from vosk import Model as VoskModel, KaldiRecognizer
    import wave, json as jsonlib
    _vosk_available = True) utilities for Interview Co-pilot.

- Uses OpenAI Whisper if available (pip install openai-whisper)
- Falls back to Vosk (pip install vosk) if Whisper not available
- Final fallback: stub transcript
"""

import os
import io
from typing import Dict, Any

# Whisper
try:
    import whisper
    _whisper_available = True
except ImportError:
    _whisper_available = False

# Vosk
try:
    from .vosk import Model as VoskModel, KaldiRecognizer
    import wave, json as jsonlib
    _vosk_available = True
except ImportError:
    _vosk_available = False


# -------------------------------
# Whisper Model (lazy load)
# -------------------------------
_whisper_model = None
def _load_whisper():
    global _whisper_model
    if _whisper_available and _whisper_model is None:
        _whisper_model = whisper.load_model(os.getenv("WHISPER_MODEL", "base"))
    return _whisper_model


# -------------------------------
# Vosk Model (lazy load)
# -------------------------------
_vosk_model = None
def _load_vosk():
    global _vosk_model
    if _vosk_available and _vosk_model is None:
        model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
        if os.path.exists(model_path):
            _vosk_model = VoskModel(model_path)
    return _vosk_model


# -------------------------------
# Core STT Function
# -------------------------------
def transcribe(audio_bytes: bytes, use: str = "auto") -> Dict[str, Any]:
    """
    Transcribe audio bytes into text.
    Args:
        audio_bytes: raw audio file content
        use: "whisper" | "vosk" | "auto"
    """
    if not audio_bytes:
        return {"text": "", "engine": "none"}

    # Try Whisper first
    if use in ("whisper", "auto") and _whisper_available:
        model = _load_whisper()
        if model:
            try:
                # Write to temp file
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio_bytes)
                result = model.transcribe("temp_audio.wav")
                return {"text": result.get("text", "").strip(), "engine": "whisper"}
            except Exception as e:
                return {"text": f"[Whisper error: {str(e)}]", "engine": "whisper"}

    # Try Vosk second
    if use in ("vosk", "auto") and _vosk_available:
        model = _load_vosk()
        if model:
            try:
                wf = wave.open(io.BytesIO(audio_bytes), "rb")
                rec = KaldiRecognizer(model, wf.getframerate())
                rec.SetWords(True)
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        results.append(jsonlib.loads(rec.Result()))
                results.append(jsonlib.loads(rec.FinalResult()))
                transcript = " ".join(r.get("text", "") for r in results)
                return {"text": transcript.strip(), "engine": "vosk"}
            except Exception as e:
                return {"text": f"[Vosk error: {str(e)}]", "engine": "vosk"}

    # Fallback stub
    return {"text": "[Stub transcript] This is a placeholder transcription.", "engine": "stub"}

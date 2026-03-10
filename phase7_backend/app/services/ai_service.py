import os
from dotenv import load_dotenv
import google.generativeai as genai

FRIENDLY_ERROR_MESSAGE = "Assistant temporarily unavailable. Please try again."

_MODEL_PRIMARY = "gemini-1.5-flash"
_MODEL_FALLBACK = "gemini-1.5-pro"

_CONFIGURED = False
_CONFIGURED_KEY = None


def _get_api_key() -> str:
    load_dotenv()
    return os.getenv("GEMINI_API_KEY", "").strip()


def _ensure_configured() -> None:
    global _CONFIGURED, _CONFIGURED_KEY
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    if _CONFIGURED and _CONFIGURED_KEY == api_key:
        return
    genai.configure(api_key=api_key)
    _CONFIGURED = True
    _CONFIGURED_KEY = api_key


def generate_text(prompt: str) -> str:
    _ensure_configured()

    try:
        model = genai.GenerativeModel(_MODEL_PRIMARY)
    except Exception:
        model = genai.GenerativeModel(_MODEL_FALLBACK)

    response = model.generate_content(prompt)
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    return text

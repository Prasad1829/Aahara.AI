import os
from dotenv import load_dotenv
from groq import Groq

FRIENDLY_ERROR_MESSAGE = "Assistant temporarily unavailable. Please try again."

_CLIENT = None

def _get_client():
    global _CLIENT
    if _CLIENT:
        return _CLIENT
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    _CLIENT = Groq(api_key=api_key)
    return _CLIENT

def generate_text(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    text = response.choices[0].message.content.strip()
    if not text:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    return text
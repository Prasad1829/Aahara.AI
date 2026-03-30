import os
from typing import Any

import requests
from dotenv import load_dotenv

FRIENDLY_ERROR_MESSAGE = "Assistant temporarily unavailable. Please try again."
_TIMEOUT_SECONDS = 45


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SECONDS)
    if not response.ok:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    data = response.json()
    if not isinstance(data, dict):
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    return data


def _generate_with_openai(api_key: str, prompt: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000,
        },
    )
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    message = choices[0].get("message") or {}
    text = (message.get("content") or "").strip()
    if not text:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    return text


def _generate_with_groq(api_key: str, prompt: str) -> str:
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip() or "llama-3.3-70b-versatile"
    data = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000,
        },
    )
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    message = choices[0].get("message") or {}
    text = (message.get("content") or "").strip()
    if not text:
        raise RuntimeError(FRIENDLY_ERROR_MESSAGE)
    return text


def generate_text(prompt: str) -> str:
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_api_key:
        return _generate_with_openai(openai_api_key, prompt)

    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_api_key:
        return _generate_with_groq(groq_api_key, prompt)

    raise RuntimeError(FRIENDLY_ERROR_MESSAGE)

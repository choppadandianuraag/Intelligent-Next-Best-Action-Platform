"""
Shared LLM client for Meridian agents.

Uses Groq API directly via the Groq Python SDK.
Model: llama-3.3-70b-versatile (configurable via GROQ_MODEL env var).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _get_client() -> Groq:
    """Create and return a Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please set it in your environment or .env file."
        )
    return Groq(api_key=api_key)


def _get_model() -> str:
    """Return the model name from env or default."""
    return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def call_llm(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0,
    json_mode: bool = False,
) -> str:
    """
    Call the Groq LLM and return the raw response text.

    Args:
        prompt: The full prompt to send to the model.
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature (0 = deterministic).
        json_mode: If True, uses response_format=json_object.

    Returns:
        The raw response text from the model.

    Raises:
        RuntimeError: If GROQ_API_KEY is missing.
        Exception: Re-raises API errors for the caller to handle.
    """
    client = _get_client()
    model = _get_model()

    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""

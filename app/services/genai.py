"""
genai.py
- Lightweight wrapper to call OpenAI Chat Completions for resume improvement
- Expects OPENAI_API_KEY env var to be set
"""
import os
import time

OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)
_HAVE_OPENAI = False
_client = None

if OPENAI_KEY:
    try:
        import openai
        openai.api_key = OPENAI_KEY
        _client = openai
        _HAVE_OPENAI = True
    except Exception:
        _HAVE_OPENAI = False

def suggest_improvements(resume_text: str, max_tokens: int = 400) -> str:
    if not _HAVE_OPENAI:
        return "OpenAI API key not configured. Set OPENAI_API_KEY to get suggestions."
    prompt = (
        "You are an expert resume coach. Given the resume text below, "
        "provide concise, actionable improvements: summary improvements, bullet re-writes, "
        "skill suggestions and headline/objective rewrite.\n\n"
        f"Resume:\n{resume_text}\n\nSuggestions:\n"
    )
    try:
        # Use ChatCompletion or create as per your OpenAI library version.
        # Here we use a standard ChatCompletion call that should work with most SDKs.
        resp = _client.ChatCompletion.create(
            model="gpt-4o-mini",  # change to a model you have access to
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        text = resp["choices"][0]["message"]["content"]
        return text
    except Exception as e:
        return f"Failed to call OpenAI: {str(e)}"

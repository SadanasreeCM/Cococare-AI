"""
CoconutCare Chatbot Service — Groq-powered multilingual assistant.

Supports English, Tamil, Hindi by prompting Groq with a language-specific system instruction.
"""

import os
import traceback
from groq import Groq
from backend.config import settings

# ---------------------------------------------------------------------------
# Language Code → Full Name Mapping
# ---------------------------------------------------------------------------
LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
}

SUPPORTED_LANGUAGES = list(LANGUAGE_MAP.keys())

# Candidate model list for resilient fallback
MODELS_TO_TRY = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]


def _get_groq_client() -> Groq:
    """Retrieve initialized Groq client using settings or os.environ."""
    api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing or empty.")
    return Groq(api_key=api_key)


def get_chat_response(
    user_message: str = "",
    chat_history: list[dict] | None = None,
    user_context: str | None = None,
    language: str = "en",
    message: str | None = None,
    history: list[dict] | None = None,
) -> str:
    """
    Send a user message to Groq and return the assistant response.

    Parameters
    ----------
    user_message : str
        The latest user message.
    chat_history : list[dict] | None
        Prior conversation turns in the form [{"role": "user"|"assistant", "content": "text"}, ...].
    user_context : str | None
        Optional scan context (e.g. recent disease detection result).
    language : str
        Language code (e.g. "en", "ta", "hi").
    """
    # Normalize input parameters
    user_msg = user_message or message or ""
    history_list = chat_history if chat_history is not None else (history or [])
    if language not in LANGUAGE_MAP:
        language = "en"

    language_names = {"en": "English", "ta": "Tamil", "hi": "Hindi"}
    lang_name = language_names.get(language, "English")

    system_prompt = (
        f"You are CoconutCare Assistant, a helpful expert on coconut tree health, "
        f"common diseases (leaf blight, bud rot, lethal yellowing, leaf rot, stem bleeding, "
        f"nutrient deficiencies), treatment recommendations, and general coconut farming advice. "
        f"Keep answers concise, practical, and farmer-friendly. "
        f"Respond ONLY in {lang_name}, regardless of what language the user writes in. "
        f"If asked something unrelated to coconuts/farming, politely redirect to relevant topics.\n\n"
        f"STRICT SAFETY & ANTI-HALLUCINATION RULES:\n"
        f"1. NEVER generate, invent, or estimate exact numeric fertilizer dosages, pesticide/chemical quantities (e.g. in grams, kg, ml), or irrigation liters.\n"
        f"2. If asked for exact dosage or chemical amounts, provide general agronomic principles, advise consulting local agricultural extension services or doing a soil test, and ALWAYS include the disclaimer:\n"
        f"'General guidance only — confirm with local agricultural extension services or a soil test before applying.'"
    )

    if user_context:
        system_prompt += f"\n\nFARMER & PLANTATION CONTEXT:\n{user_context}"


    messages = [{"role": "system", "content": system_prompt}]

    # Format history turns to OpenAI / Groq standard
    for turn in history_list:
        role = turn.get("role", "user")
        if role == "model":
            role = "assistant"
        
        content = turn.get("content")
        if content is None and "parts" in turn:
            parts = turn["parts"]
            content = " ".join(parts) if isinstance(parts, list) else str(parts)

        if content and role in ("user", "assistant"):
            messages.append({"role": role, "content": str(content)})

    messages.append({"role": "user", "content": user_msg})

    client = _get_groq_client()
    last_exception = None

    for model_name in MODELS_TO_TRY:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_exception = e
            # If model is not available for this key/account, try next candidate
            err_str = str(e).lower()
            if "model_not_found" in err_str or "does not exist" in err_str or "404" in err_str:
                continue
            else:
                # Break and log for other errors
                break

    print("\n" + "=" * 70)
    print("[chatbot.py] GROQ API CALL FAILED — FULL TRACEBACK:")
    print("=" * 70)
    if last_exception:
        traceback.print_exception(type(last_exception), last_exception, last_exception.__traceback__)
    print("=" * 70 + "\n")
    return "Sorry, something went wrong. Please try again."

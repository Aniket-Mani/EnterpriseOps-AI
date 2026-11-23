
from google import genai

from app.config import settings


client = genai.Client(api_key=settings.gemini_api_key)

MODEL_CHAINS = {
    "routine": [
        settings.gemini_routine_model,
        settings.gemini_complex_model,
        settings.gemini_fallback_model,
    ],
    "complex": [
        settings.gemini_complex_model,
        settings.gemini_fallback_model,
    ],
}


def is_temporary_error(exc: Exception) -> bool:
    error = str(exc).upper()
    return any(
        marker in error
        for marker in (
            "503",
            "UNAVAILABLE",
            "429",
            "RESOURCE_EXHAUSTED",
            "500",
            "504",
            "INTERNAL",
        )
    )


def generate_response(prompt: str, task_type: str = "routine") -> dict:
    if task_type not in MODEL_CHAINS:
        raise ValueError(f"Unsupported task type: {task_type}")

    last_error = None

    for model_name in MODEL_CHAINS[task_type]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            return {
                "success": True,
                "model": model_name,
                "fallback_used": model_name != MODEL_CHAINS[task_type][0],
                "text": response.text,
            }

        except Exception as exc:
            last_error = exc

            if not is_temporary_error(exc):
                raise

    raise RuntimeError(
        f"All models failed for {task_type} tasks. "
        f"Last error: {last_error}"
    ) from last_error

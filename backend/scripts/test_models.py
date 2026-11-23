from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

models = {
    "Routine": settings.gemini_routine_model,
    "Complex": settings.gemini_complex_model,
    "Fallback": settings.gemini_fallback_model,
}

def test_model(label:str, model_name:str):
    print(f"\nTesting {label}: {model_name}")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: MODEL_OK",
        )
        print("Status: SUCCESS")
        print("Response: ", response.text)
    except Exception as exc:
        print("Status: FAILED")
        print("Error type:", type(exc).__name__)
        print("Error:", str(exc)[:500])

if __name__=="__main__":
    for label, model_name in models.items():
        test_model(label, model_name)
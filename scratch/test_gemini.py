import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

models = [
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-pro"
]

for model in models:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Hello"
        )
        print(f"Success with {model}:", response.text.strip())
        break
    except Exception as e:
        print(f"Error with {model}:", type(e).__name__, str(e))






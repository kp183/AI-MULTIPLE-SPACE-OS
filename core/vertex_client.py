# core/vertex_client.py
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Gemini model once
vertexai.init(project="your-gcp-project-id", location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

def get_vertex_response(user_text: str) -> str:
    """
    Calls Gemini and returns a short response.
    """
    try:
        response = model.generate_content(user_text)
        return response.text.strip()
    except Exception as e:
        return f"(Gemini error: {e})"

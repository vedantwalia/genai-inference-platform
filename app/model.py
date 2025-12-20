import os
import logging
import requests

logger = logging.getLogger(__name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "distilbert/distilgpt2"

HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json",
}

def generate_response(prompt: str) -> str:
    """
    Call Hugging Face Inference API directly (REST).
    This avoids InferenceClient provider bugs.
    """
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        # distilgpt2 returns a list of generated texts
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]

        # fallback (defensive)
        return str(data)

    except Exception:
        logger.exception("HF inference failed")
        raise
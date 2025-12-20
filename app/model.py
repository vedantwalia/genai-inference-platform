import os
import logging
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

client = InferenceClient(
    model="google/flan-t5-base",
    token=os.getenv("HF_API_TOKEN"),
)

def generate_response(prompt: str) -> str:
    """
    Synchronous Hugging Face inference.
    FastAPI will run this in a threadpool automatically.
    """
    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=128,
        )
        return response.strip()

    except Exception:
        logger.exception("HF inference failed")
        raise
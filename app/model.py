import asyncio
import logging
import os
from openai import OpenAI, RateLimitError

logger = logging.getLogger(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_response(prompt: str) -> str:
    """
    Generate a response from the LLM.
    Runs blocking SDK call in a thread to avoid blocking the event loop.
    """

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    except RateLimitError:
        logger.warning("OpenAI quota exhausted")
        raise

    except Exception:
        logger.exception("LLM inference failed")
        raise
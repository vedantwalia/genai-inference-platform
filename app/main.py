from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from prometheus_client import generate_latest
from starlette.responses import Response, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
import asyncio
import logging
import os
import time
from openai import RateLimitError
from app.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
    REQUEST_COST_USD
)
from app.model import generate_response

# --------------------------------------------------
# App setup
# --------------------------------------------------
app = FastAPI(title="GenAI Inference Platform")

# CORS (development only – restrict origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Models
# --------------------------------------------------
class PredictRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 4000:
            raise ValueError("Text too long")
        return v


class PredictResponse(BaseModel):
    output: str


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    REQUEST_COUNT.inc()
    start_time = time.time()

    try:
        output = await generate_response(req.text)

        # Rough cost estimation (demo purpose)
        REQUEST_COST_USD.inc(0.002)

        return {"output": output}

    except RateLimitError:
        ERROR_COUNT.inc()
        logger.warning("LLM quota exceeded")
        raise HTTPException(
            status_code=429,
            detail="LLM quota exceeded. Try again later."
        )

    except Exception:
        ERROR_COUNT.inc()
        logger.exception("Inference failed")
        raise HTTPException(status_code=500, detail="Inference failed")

    finally:
        REQUEST_LATENCY.observe(max(0.0, time.time() - start_time))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


@app.get("/", response_class=HTMLResponse)
def index():
    html = """
    <html>
      <head><title>GenAI Inference Platform</title></head>
      <body>
        <h1>GenAI Inference Platform</h1>
        <ul>
          <li><a href="/docs">Swagger UI</a></li>
          <li><a href="/redoc">ReDoc</a></li>
          <li><a href="/health">Health</a></li>
          <li><a href="/metrics">Metrics</a></li>
        </ul>
        <p>POST /predict with JSON: {"text": "hello"}</p>
      </body>
    </html>
    """
    return HTMLResponse(html)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response, HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from openai import OpenAI
import asyncio
import logging
import os
import time

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
# Prometheus metrics (best-practice naming)
# --------------------------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests"
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds"
)

ERROR_COUNT = Counter(
    "http_request_errors_total",
    "Total number of failed HTTP requests"
)

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
# OpenAI client
# --------------------------------------------------
logger.info(f"OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    REQUEST_COUNT.inc()
    start_time = time.time()

    try:
        # Run blocking OpenAI call in thread to avoid blocking event loop
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": req.text}],
        )

        output = response.choices[0].message.content
        return {"output": output}

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
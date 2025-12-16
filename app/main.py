from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI(title="GenAI Platform Starter")

REQUEST_COUNT = Counter("request_count", "Total requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")
ERROR_COUNT = Counter("error_count", "Total errors")

class Request(BaseModel):
    text: str

class ResponseModel(BaseModel):
    output: str

@app.post("/predict", response_model=ResponseModel)
@REQUEST_LATENCY.time()
def predict(req: Request):
    REQUEST_COUNT.inc()
    try:
        # Dummy model logic (replace with OpenAI / HF later)
        output = req.text[::-1]
        return {"output": output}
    except Exception:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=500, detail="Inference failed")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
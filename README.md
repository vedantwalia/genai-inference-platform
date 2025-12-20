# genai-inference-platform

**Overview**
- Small starter FastAPI app that exposes an inference endpoint (`/predict`), a health check (`/health`), and Prometheus metrics (`/metrics`). The project includes a `Dockerfile` so you can build and run the service in a container.

**Prerequisites**
- Python 3.10+
- Docker (or Colima + Docker CLI) for running in containers
- (Optional) Homebrew on macOS for installing Docker/Colima

**Files of interest**
- `Dockerfile` — builds the container image and runs `uvicorn app.main:app` on port 8000
- `requirements.txt` — Python dependencies
- `app/main.py` — FastAPI app and endpoints

**Environment**
- `HF_API_TOKEN` — Hugging Face API token (set in your environment for private models). Optional for public models.
- `HF_MODEL` — (optional) model repo id to use, e.g. `google/flan-t5-base`. Defaults to `google/flan-t5-base`.

**Local (dev) quickstart**
1. Create and activate a virtualenv (optional):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Verify:

```bash
curl -i http://localhost:8000/health
open http://localhost:8000/docs
```

**Docker (recommended)**
1. Build the image:

```bash
docker build -t genai-platform .
```

2. Run the container (maps container port 8000 to host 8000):

```bash
docker run -p 8000:8000 genai-platform
```

3. In another terminal verify the service:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/docs
```

Notes:
- If `docker info` or `docker run` fail with "Cannot connect to the Docker daemon" on macOS, start Docker Desktop or use Colima (`brew install colima docker && colima start`).
- Use the modern Compose syntax: `docker compose up --build` (space). If `docker-compose` is missing, prefer `docker compose` or install the standalone `docker-compose` via Homebrew only if necessary.

**API usage examples**
- Health check

```bash
curl -sS http://localhost:8000/health
# {"status":"ok"}
```

- Predict (JSON POST)

```bash
curl -sS -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"hello world"}'
```

Response example

```json
{"output":"dlrow olleh"}
```

**Metrics**
- Prometheus-compatible metrics are exposed at `/metrics`.

**Troubleshooting**
- Blank browser / cannot reach service: ensure container is running and port is published: `docker ps` and verify `0.0.0.0:8000->8000/tcp` is present.
- If the container starts then exits, fetch logs: `docker ps -a` then `docker logs <container-id>`.
- If `docker-compose` command not found, use `docker compose` (space) after starting Docker daemon or install the plugin.

**Next steps / suggestions**
- Pin dependency versions in `requirements.txt` for reproducible builds.
- Add basic logging around external API calls for easier debugging.
- Add unit tests for the endpoints.

---
If you want, I can add a short example `docker-compose.yml` or pin dependency versions next. Tell me which you'd prefer.

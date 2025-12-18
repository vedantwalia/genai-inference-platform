from prometheus_client import Counter, Histogram

# Total HTTP requests
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests"
)

# Request latency in seconds
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds"
)

# Total failed requests
ERROR_COUNT = Counter(
    "http_request_errors_total",
    "Total number of failed HTTP requests"
)

# Optional: estimated cost tracking (GenAI platform signal)
REQUEST_COST_USD = Counter(
    "llm_request_cost_usd_total",
    "Estimated LLM request cost in USD"
)
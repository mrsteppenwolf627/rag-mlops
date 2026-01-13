from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# --- Definición de Métricas para Prometheus ---

REQUEST_COUNT = Counter(
    "rag_requests_total", 
    "Total number of RAG requests",
    ["endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total tokens consumed",
    ["model", "type"]
)

LLM_COST = Counter(
    "llm_cost_usd_total",
    "Total cost in USD"
)

ACTIVE_REQUESTS = Gauge(
    "rag_active_requests",
    "Number of requests currently being processed"
)

APP_INFO = Info("rag_app", "RAG application info")

def init_metrics():
    """Inicializa metadata de la app."""
    APP_INFO.info({"version": "1.0.0", "name": "RAG-MLOps"})

def track_request_metrics(endpoint: str):
    """Decorador para medir tiempo y éxito de endpoints."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.inc()
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise e
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
                ACTIVE_REQUESTS.dec()
        return wrapper
    return decorator

def track_llm_metrics(model: str, input_tokens: int, output_tokens: int, cost: float):
    """Registra consumo de LLM en Prometheus."""
    LLM_TOKENS.labels(model=model, type="input").inc(input_tokens)
    LLM_TOKENS.labels(model=model, type="output").inc(output_tokens)
    LLM_COST.inc(cost)

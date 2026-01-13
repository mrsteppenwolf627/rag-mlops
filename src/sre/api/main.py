from fastapi import FastAPI
from prometheus_client import make_asgi_app
from src.sre.monitoring.metrics import init_metrics
from src.sre.api.routes import router

app = FastAPI(title="RAG MLOps API", version="1.0.0")

# Inicializar métricas
init_metrics()

# Endpoint /metrics para Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Rutas de la app
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "RAG MLOps API is running "}

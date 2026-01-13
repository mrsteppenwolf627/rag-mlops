from src.sre.monitoring.logger import get_logger

# Simulamos que estamos en la API
logger = get_logger("src.api.routes")

print("--- Probando Log Normal ---")
logger.info("Iniciando servicio RAG", version="1.0.0")

print("\n--- Probando Log de Evento RAG ---")
# Esto es lo que usaremos para medir costes y uso
logger.info(
    "query_processed",
    user_id="user_123",
    query="Que es el CTE?",
    latency_ms=450,
    cost_usd=0.024,
    model="gpt-4"
)

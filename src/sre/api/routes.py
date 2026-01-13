from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from prometheus_client import Counter

from src.sre.generation.llm_client import RAGModel # Importamos la clase directamente para instanciar según toque
from src.sre.monitoring.metrics import track_request_metrics, track_llm_metrics
from src.sre.monitoring.logger import get_logger
from src.sre.utils.cache import get_cache
from src.sre.generation.model_router import get_model_router # <--- NUEVO IMPORT

router = APIRouter()
logger = get_logger("src.api.routes")
cache = get_cache()
model_router = get_model_router() # <--- Instanciamos el router

# Métricas
CACHE_HITS = Counter('rag_cache_hits_total', 'Number of cache hits')
CACHE_MISSES = Counter('rag_cache_misses_total', 'Number of cache misses')
MODEL_ROUTING = Counter('model_routing_total', 'Model routing decisions', ['model']) # <--- NUEVA MÉTRICA

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

@router.post("/query", response_model=QueryResponse)
@track_request_metrics(endpoint="query")
async def query_rag(request: QueryRequest):
    logger.info("request_received", query=request.query)
    
    try:
        context_chunks = [
            "DB-SI 4: Los extintores se colocan a 1.20m de altura.",
            "DB-SI 4: Deben estar señalizados con carteles fotoluminiscentes."
        ]

        # 1. CACHÉ
        cached_response = cache.get(request.query, context_chunks)
        if cached_response:
            CACHE_HITS.inc()
            logger.info("cache_hit", query=request.query)
            cached_response["metadata"]["source"] = "cache"
            return QueryResponse(**cached_response)

        CACHE_MISSES.inc()

        # 2. MODEL ROUTING (AQUÍ ESTÁ LA MAGIA) 🧙‍♂️
        selected_model_name = model_router.route(request.query, context_chunks)
        
        # Registramos la decisión en Prometheus
        MODEL_ROUTING.labels(model=selected_model_name).inc()
        
        logger.info("model_selected", model=selected_model_name, query=request.query)

        # Instanciamos el modelo específico que ha decidido el router
        model = RAGModel(model_name=selected_model_name)
        
        result = model.generate_response(
            query=request.query,
            context_chunks=context_chunks,
            run_name=f"api_query_{selected_model_name}"
        )
        
        # 3. Guardar métricas
        track_llm_metrics(
            model=result["metadata"]["model"],
            input_tokens=int(result["metrics"]["tokens"] * 0.7),
            output_tokens=int(result["metrics"]["tokens"] * 0.3),
            cost=result["metrics"]["cost_usd"]
        )
        
        # 4. Guardar en Caché
        response_data = {
            "answer": result["answer"],
            "metrics": result["metrics"],
            "metadata": result["metadata"]
        }
        cache.set(request.query, context_chunks, response_data)
        
        return QueryResponse(**response_data)

    except Exception as e:
        logger.error("query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
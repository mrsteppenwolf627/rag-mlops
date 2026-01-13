import redis
import json
import hashlib
from typing import Optional
from src.sre.config.settings import get_settings

settings = get_settings()

class RedisCache:
    """Caché de respuestas RAG."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )
        self.ttl = 3600  # 1 hora de vida para la caché

    def _generate_key(self, query: str, context_chunks: list) -> str:
        """Genera una clave única (hash) basada en la pregunta y el contexto."""
        # Si cambia el contexto (ej. documentos actualizados), cambia la key
        context_str = json.dumps(context_chunks, sort_keys=True)
        combined = f"{query}:{context_str}"
        return f"rag_cache:{hashlib.md5(combined.encode()).hexdigest()}"

    def get(self, query: str, context_chunks: list) -> Optional[dict]:
        """Intenta recuperar respuesta cacheada."""
        key = self._generate_key(query, context_chunks)
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, query: str, context_chunks: list, response: dict):
        """Guarda respuesta en caché."""
        key = self._generate_key(query, context_chunks)
        self.redis_client.setex(
            name=key,
            time=self.ttl,
            value=json.dumps(response)
        )

    def clear(self):
        """Limpia todo el caché (útil para tests)."""
        for key in self.redis_client.scan_iter("rag_cache:*"):
            self.redis_client.delete(key)

# Singleton
_cache_instance = None
def get_cache() -> RedisCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
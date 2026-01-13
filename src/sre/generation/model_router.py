from typing import Literal

ModelType = Literal["gpt-4", "gpt-3.5-turbo"]

class ModelRouter:
    """Decide qué modelo usar según la query."""
    
    def route(self, query: str, context_chunks: list) -> ModelType:
        """
        Estrategia de Routing:
        - GPT-4: Si hay palabras clave de complejidad o mucho contexto.
        - GPT-3.5: Para todo lo demás (ahorro de costes).
        """
        
        # 1. Palabras clave que requieren razonamiento profundo
        complex_keywords = [
            "compara", "diferencia", "analiza", "evalúa", 
            "razonamiento", "pros y contras", "tabla comparativa",
            "explicación detallada", "resumen ejecutivo"
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in complex_keywords):
            return "gpt-4"

        # 2. Si la pregunta es muy larga, mejor GPT-4 para no perder el hilo
        if len(query) > 250:
            return "gpt-4"
            
        # 3. Si hay MUCHO contexto recuperado, GPT-4 suele manejarlo mejor
        total_context_length = sum(len(chunk) for chunk in context_chunks)
        if total_context_length > 3000:
            return "gpt-4"

        # Default: Ahorrar dinero con el modelo rápido
        return "gpt-3.5-turbo"

# Singleton
_router_instance = None
def get_model_router() -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
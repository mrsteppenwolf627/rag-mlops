import mlflow
import time
from openai import OpenAI
from typing import List, Dict
from src.sre.config.settings import get_settings
from src.sre.monitoring.logger import get_logger
from src.sre.config.prompts import get_prompt_template, get_system_prompt, get_prompt_metadata

settings = get_settings()
logger = get_logger("src.generation.llm_client")

class RAGModel:
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.prompt_metadata = get_prompt_metadata()
        
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)

    def generate_response(self, query: str, context_chunks: List[str], run_name: str = None) -> Dict:
        
        with mlflow.start_run(run_name=run_name) as run:
            start_time = time.time()
            
            # --- Versionado ---
            mlflow.log_param("prompt_version", self.prompt_metadata["version"])
            mlflow.log_param("prompt_updated", self.prompt_metadata["last_updated"])
            
            # --- Construcción del Prompt ---
            context_text = "\n\n".join(context_chunks)
            system_prompt = get_system_prompt("cte_expert")
            prompt_template = get_prompt_template("rag")
            user_prompt = prompt_template.format(context=context_text, query=query)
            
            # --- Logueo de Parámetros ---
            mlflow.log_param("model", self.model_name)
            mlflow.log_param("temperature", self.temperature)
            mlflow.log_param("num_chunks", len(context_chunks))
            
            mlflow.log_text(user_prompt, "final_prompt.txt")
            mlflow.log_text(system_prompt, "system_prompt.txt")

            try:
                # --- Llamada LLM ---
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                
                answer = response.choices[0].message.content
                
                # --- Métricas ---
                latency_ms = (time.time() - start_time) * 1000
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                if "gpt-4" in self.model_name:
                    cost_usd = (input_tokens / 1000 * 0.03) + (output_tokens / 1000 * 0.06)
                else:
                    cost_usd = (input_tokens / 1000 * 0.0005) + (output_tokens / 1000 * 0.0015)

                mlflow.log_metric("latency_ms", latency_ms)
                mlflow.log_metric("total_tokens", total_tokens)
                mlflow.log_metric("cost_usd", cost_usd)
                
                mlflow.log_text(answer, "response.txt")
                
                logger.info(
                    "rag_generation_complete",
                    query=query,
                    prompt_version=self.prompt_metadata["version"],
                    latency_ms=latency_ms,
                    cost_usd=cost_usd
                )
                
                return {
                    "answer": answer,
                    "metrics": {
                        "latency_ms": latency_ms, 
                        "cost_usd": cost_usd, 
                        "tokens": total_tokens
                    },
                    "metadata": {
                        "model": self.model_name, 
                        "prompt_version": self.prompt_metadata["version"],
                        "run_id": run.info.run_id
                    }
                }

            except Exception as e:
                logger.error("rag_generation_failed", error=str(e))
                raise e

# Singleton
_model_instance = None
def get_rag_model() -> RAGModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = RAGModel()
    return _model_instance

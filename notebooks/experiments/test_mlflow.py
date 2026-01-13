import mlflow
import sys
import os

# Asegurar que Python encuentre nuestros modulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.sre.config.settings import get_settings

settings = get_settings()

# Configurar MLflow
mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
mlflow.set_experiment(settings.mlflow_experiment_name)

print(f" Conectando a MLflow en {settings.mlflow_tracking_uri}...")

with mlflow.start_run(run_name="test-setup"):
    mlflow.log_param("model", "gpt-4")
    mlflow.log_param("temperature", 0.3)
    mlflow.log_metric("accuracy", 0.85)
    
    with open("prompt_example.txt", "w", encoding="utf-8") as f:
        f.write("Eres un asistente experto...")
    mlflow.log_artifact("prompt_example.txt")

    print(" Experimento registrado correctamente!")

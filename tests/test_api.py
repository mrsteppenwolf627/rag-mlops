from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.sre.api.main import app

client = TestClient(app)

def test_health_check():
    """Verifica que la API está viva"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# PATCH 1: Calla a MLflow (evita el error de conexión al puerto 5000)
@patch("src.sre.generation.llm_client.mlflow")
# PATCH 2: Calla a Redis (evita el error de caché)
@patch("src.sre.api.routes.cache")
# PATCH 3: Calla a OpenAI (evita gastar dinero)
@patch("src.sre.generation.llm_client.RAGModel.generate_response")
def test_query_endpoint(mock_generate, mock_cache, mock_mlflow):
    """
    Test completo: Mockeamos MLflow, Redis y OpenAI.
    """
    # 1. Configurar Mock Caché (Vacía)
    mock_cache.get.return_value = None 
    
    # 2. Configurar Mock OpenAI (Respuesta Falsa)
    mock_response = {
        "answer": "Respuesta simulada de test",
        "metrics": {
            "latency_ms": 100,
            "cost_usd": 0.0,
            "tokens": 50
        },
        "metadata": {
            "model": "gpt-3.5-turbo",
            "prompt_version": "v1.0",
            "run_id": "test-run-123",
            "source": "mock"
        }
    }
    mock_generate.return_value = mock_response

    # 3. Lanzar petición
    payload = {"query": "Test query", "top_k": 1}
    response = client.post("/query", json=payload)

    # --- CHIVATO DE ERRORES ---
    if response.status_code != 200:
        print("\n" + "="*50)
        print("⚠️  ERROR REAL:")
        print(response.text)
        print("="*50 + "\n")

    # 4. Validar
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Respuesta simulada de test"
    
    # Verificar que el código pasó por el router y llegó a intentar generar
    mock_generate.assert_called_once()
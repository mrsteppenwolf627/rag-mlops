import sys
import os

# Ajustar path para encontrar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.sre.generation.llm_client import get_rag_model

# 1. Instanciar el modelo
print("🚀 Iniciando modelo RAG...")
rag = get_rag_model()

# 2. Datos simulados (como si vinieran de Pinecone)
context_chunks = [
    "DB-SI 4: Los extintores deben colocarse a una altura máxima de 1.20m.",
    "DB-SI 4: La distancia máxima entre extintores será de 15 metros."
]

query = "¿A qué altura se ponen los extintores?"

# 3. Generar respuesta
print(f"❓ Pregunta: {query}")
print("⏳ Generando respuesta (llamando a OpenAI)...")

try:
    result = rag.generate_response(
        query=query, 
        context_chunks=context_chunks,
        run_name="test-manual-extintores"
    )

    print("\n✅ RESPUESTA RECIBIDA:")
    print(result["answer"])
    print("\n📊 MÉTRICAS:")
    print(result["metrics"])
    print(f"\n🔗 MLflow Run ID: {result['metadata']['run_id']}")
    print("👉 Revisa http://localhost:5000 para ver el log completo.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Asegúrate de tener OPENAI_API_KEY correcta en tu .env")
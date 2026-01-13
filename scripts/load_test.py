import requests
import time
import random

# URLs
API_URL = "http://localhost:8000/query"

# Preguntas de prueba para variar el tráfico
queries = [
    "¿Qué dice el CTE sobre extintores?",
    "Requisitos de accesibilidad en rampas",
    "Normativa DB-SI evacuación y puertas",
    "Distancia máxima de recorrido de evacuación",
    "Eficacia mínima de extintores según DB-SI 4",
    "¿Es obligatorio el alumbrado de emergencia?",
    "Ancho mínimo de pasillos en uso hospitalario"
]

print(f"🚀 Iniciando prueba de carga contra {API_URL}...")
print("Presiona CTRL+C para detener.\n")

counter = 0
try:
    while True:
        query = random.choice(queries)
        
        try:
            # Enviamos petición
            response = requests.post(
                API_URL, 
                json={"query": query, "top_k": 3},
                timeout=10
            )
            
            counter += 1
            status = response.status_code
            
            # Imprimimos resultado
            if status == 200:
                data = response.json()
                cost = data["metrics"]["cost_usd"]
                latency = data["metrics"]["latency_ms"]
                print(f"[{counter}] ✅ Status: {status} | Latency: {latency:.0f}ms | Cost: ${cost:.5f}")
            else:
                print(f"[{counter}] ❌ Error Status: {status}")

        except Exception as e:
            print(f"[{counter}] 💥 Error de conexión: {e}")

        # Esperamos un poco (2 peticiones por segundo aprox)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Prueba detenida por el usuario.")

import streamlit as st
import requests
import time

# Configuración de la página
st.set_page_config(
    page_title="Asistente CTE - RAG MLOps",
    page_icon="🏗️",
    layout="centered"
)

# Título
st.title("🏗️ Asistente Normativa CTE")
st.markdown("""
Este asistente responde preguntas sobre el **Código Técnico de la Edificación**.
* 🧠 **Inteligente:** Decide si usar GPT-3.5 o GPT-4.
* ⚡ **Rápido:** Usa caché Redis.
* 📊 **Monitorizado:** Todo queda registrado.
""")

# Sidebar
with st.sidebar:
    st.header("🔧 Estado del Sistema")
    try:
        health = requests.get("http://localhost:8000/health", timeout=2)
        if health.status_code == 200:
            st.success("API Online 🟢")
        else:
            st.error("API Error 🔴")
    except:
        st.error("API Offline 🔴")
        
    st.info("Backend corriendo en: http://localhost:8000")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pregunta sobre extintores, pasillos, rampas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... ⏳")
        
        try:
            start = time.time()
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": prompt, "top_k": 3},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                meta = data["metadata"]
                metrics = data["metrics"]
                
                message_placeholder.markdown(answer)
                
                with st.expander("🔍 Detalles Técnicos (MLOps)"):
                    c1, c2, c3 = st.columns(3)
                    model = meta.get("model", "unknown")
                    if model == "gpt-4":
                        c1.metric("Modelo", model, "🧠 Smart", delta_color="inverse")
                    else:
                        c1.metric("Modelo", model, "⚡ Fast")
                        
                    source = meta.get("source", "live")
                    if source == "cache":
                        c2.metric("Fuente", "Redis Caché", "🚀 Instant", delta_color="normal")
                    else:
                        c2.metric("Fuente", "OpenAI API", "☁️ Live", delta_color="off")
                        
                    cost = metrics.get("cost_usd", 0)
                    c3.metric("Coste", f"${cost:.5f}")

                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            else:
                message_placeholder.error(f"Error {response.status_code}: {response.text}")
                
        except Exception as e:
            message_placeholder.error(f"Error de conexión: {str(e)}")
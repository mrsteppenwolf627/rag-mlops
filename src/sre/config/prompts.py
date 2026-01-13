from typing import Dict

# Metadatos de versión (¡Esto es lo que MLflow rastreará!)
PROMPT_VERSION = "1.0.0"
PROMPT_LAST_UPDATED = "2026-01-13"

# Definición de roles (System Prompts)
SYSTEM_PROMPTS: Dict[str, str] = {
    "cte_expert": """Eres un experto en la normativa técnica del Código Técnico de la Edificación (CTE) de España.
Tu rol es responder preguntas técnicas sobre normativa constructiva con:
- Precisión técnica absoluta
- Referencias a artículos específicos del CTE
- Lenguaje claro pero profesional

IMPORTANTE:
- Solo usa información del contexto proporcionado.
- Si la información no está disponible, indícalo claramente.
- Cita siempre la sección del CTE (ej: "DB-SI 4.1.2").""",
    
    "general_assistant": """Eres un asistente útil y profesional."""
}

# Template para RAG (User Prompt)
RAG_PROMPT_TEMPLATE = """Contexto de la documentación técnica:
{context}

Pregunta del usuario:
{query}

Instrucciones:
- Basa tu respuesta ÚNICAMENTE en el contexto proporcionado.
- Si la información solicitada no está en el contexto, indica: "No dispongo de esa información en la documentación consultada".
- Cuando menciones requisitos técnicos, cita la sección específica.
- Sé conciso pero completo.

Respuesta:"""

def get_prompt_template(template_name: str = "rag") -> str:
    """Retorna template de prompt con versión."""
    if template_name == "rag":
        return RAG_PROMPT_TEMPLATE
    else:
        raise ValueError(f"Template desconocido: {template_name}")

def get_system_prompt(role: str = "cte_expert") -> str:
    """Retorna system prompt según rol."""
    return SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["general_assistant"])

def get_prompt_metadata() -> Dict:
    """Retorna metadata de versión de prompts."""
    return {
        "version": PROMPT_VERSION,
        "last_updated": PROMPT_LAST_UPDATED,
        "available_templates": list(SYSTEM_PROMPTS.keys())
    }
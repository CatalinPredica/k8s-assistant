import os, httpx
from typing import Literal, Optional, Tuple

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ai-agent:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")

SYSTEM_PROMPT = (
    "You are a Kubernetes command planner. Convert user requests into a single, SAFE intent "
    "using kubectl semantics. Only allow read-only operations: get, describe, logs, top. "
    "Never generate create/apply/delete/exec/patch. "
    "Return a compact JSON with fields: action, resource, namespace(optional), extras(optional)."
)

async def plan_intent(user_text: str) -> dict:
    # Ollama /api/chat (works with many models using the Chat endpoint)
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        content = r.json().get("message", {}).get("content", "{}")
    # crude JSON extraction; models often reply with JSON block
    import json, re
    match = re.search(r"\{[\s\S]*\}", content)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    # fallback to a simple heuristic
    return {"action": "get", "resource": "namespaces"}
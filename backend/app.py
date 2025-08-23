from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ai import plan_intent
from k8s import execute

app = FastAPI(title="k8s-assistant API")

class AskIn(BaseModel):
    prompt: str
    namespace: Optional[str] = None

@app.post("/api/ask")
async def ask(body: AskIn) -> Dict[str, Any]:
    try:
        intent = await plan_intent(body.prompt)
        if body.namespace and "namespace" not in intent:
            intent["namespace"] = body.namespace
        result = await execute(intent)
        return {"intent": intent, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
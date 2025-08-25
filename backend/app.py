from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import traceback

from ai import plan_intent_llm
from k8s import execute

# Environment flag to disable/enable LLM usage
USE_LLM = os.getenv("USE_LLM", "true").lower() in ("1", "true", "yes")

app = FastAPI(title="k8s-assistant API")


class AskIn(BaseModel):
    prompt: str
    namespace: Optional[str] = None


@app.post("/api/ask")
async def ask(body: AskIn) -> Dict[str, Any]:
    """
    Main API endpoint: takes a natural language prompt and optional namespace,
    converts it into an intent, and executes the Kubernetes action.
    """
    try:
        # If LLM usage is disabled, reject early
        if not USE_LLM:
            raise HTTPException(status_code=503, detail="LLM functionality is disabled")

        # Plan intent using LLM (returns Pydantic model)
        intent_obj = await plan_intent_llm(body.prompt)

        # Convert to dict for easier manipulation + return
        intent = intent_obj.dict()

        # Inject namespace if provided in request but missing in intent
        if body.namespace and not intent.get("namespace"):
            intent["namespace"] = body.namespace

        # Execute the planned intent
        result = await execute(intent)

        return {"intent": intent, "result": result}

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions directly
        raise

    except Exception as e:
        # Log full traceback for debugging
        error_trace = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "trace": error_trace}
        )
# ------------------------------------------------------------------------------
# app.py - FastAPI Application Entrypoint for Kubernetes Assistant
# ------------------------------------------------------------------------------
# This service exposes an API endpoint where:
#   1. Users provide a natural language request ("intent").
#   2. The AI planner (Gemini) suggests kubectl commands or summaries.
#   3. The backend executes the suggested kubectl commands securely.
#   4. A final, human-readable response is returned to the frontend.
# ------------------------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai import ai_plan, AIResponse, Step
from k8s import run_kubectl
import asyncio

# ------------------------------------------------------------------------------
# FastAPI App Initialization
# ------------------------------------------------------------------------------
# `FastAPI` powers the backend API.
# CORS middleware allows frontend (running in another domain/port) to call backend.
# In production, restrict `allow_origins` to trusted domains instead of `*`.
app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],        # ⚠️ Security note: limit this in production
    allow_methods=["*"], 
    allow_headers=["*"]
)

# ------------------------------------------------------------------------------
# Request Model
# ------------------------------------------------------------------------------
class RequestModel(BaseModel):
    """
    Defines the schema for incoming user requests.

    Attributes:
        user_input (str): The natural language query or command
                          (e.g., "Show me all pods in the cluster").
    """
    user_input: str


# ------------------------------------------------------------------------------
# API Endpoint: Ask Kubernetes Assistant
# ------------------------------------------------------------------------------
@app.post("/api/ask")
async def ask_k8s(request: RequestModel):
    """
    Handles a natural language Kubernetes request by:
    
    1. Initializing the step sequence.
    2. Iteratively asking AI (`ai_plan`) for the next kubectl command
       or a final human-readable output.
    3. Executing suggested kubectl commands via `run_kubectl`.
    4. Returning the structured AIResponse back to the frontend.

    Args:
        request (RequestModel): Incoming request containing user_input.

    Returns:
        AIResponse: The final structured response containing steps and output.
    """

    # Initialize step list with the first placeholder step.
    steps = [Step(step=1, kubectl_command=None, kubectl_output=None)]
    ai_resp = None
    max_steps = 10  # Safety measure: prevents infinite loops if AI fails to converge.

    # Iterative loop until AI provides a final output OR max_steps reached.
    while not (ai_resp and ai_resp.final_output) and len(steps) <= max_steps:
        # ----------------------------------------------------------------------
        # 1️ Ask AI to suggest next kubectl command or generate final output.
        # Convert Pydantic objects to dicts for prompt compatibility.
        # ----------------------------------------------------------------------
        ai_resp: AIResponse = await ai_plan(
            request.user_input,
            {"steps": [s.dict() for s in steps]}
        )

        # ----------------------------------------------------------------------
        # 2️ Execute suggested kubectl commands that have not yet been run.
        # AI provides the command, backend executes securely, and attaches output.
        # ----------------------------------------------------------------------
        for step in ai_resp.steps:
            if step.kubectl_command and not step.kubectl_output:
                step.kubectl_output = run_kubectl(step.kubectl_command)
        
        # ----------------------------------------------------------------------
        # 3️ If AI has returned a final human-readable output, stop the loop.
        # ----------------------------------------------------------------------
        if ai_resp.final_output:
            break
        
        # ----------------------------------------------------------------------
        # 4️ Otherwise, append a new empty step for the AI to fill next iteration.
        # ----------------------------------------------------------------------
        steps = ai_resp.steps
        new_step_number = len(steps) + 1
        steps.append(Step(step=new_step_number, kubectl_command=None, kubectl_output=None))

    # Return final structured AIResponse back to frontend
    return ai_resp
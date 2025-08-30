import os
import json
import re
import traceback
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import logging

# ------------------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------------------
# Setup logging for the entire module. At enterprise level, logs should be 
# centralized (e.g., sent to ELK, Datadog, or Azure Monitor).
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Gemini API Configuration
# ------------------------------------------------------------------------------
# GEMINI_API_KEY is expected to be injected as an environment variable.
# In production, never hardcode API keys; store them in secret managers 
# (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, etc.).
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Configure Gemini SDK with the API key.
genai.configure(api_key=GEMINI_API_KEY)

# Model selection - defaulting to `gemini-1.5-flash` if not overridden.
# This allows flexible upgrades to newer models via environment variable.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# ------------------------------------------------------------------------------
# Data Models (Pydantic for Validation and Type Safety)
# ------------------------------------------------------------------------------

class Step(BaseModel):
    """
    Represents a single step in the AI-assisted execution flow.
    
    Attributes:
        step (int): Step number in the execution sequence.
        kubectl_command (Optional[str]): The kubectl command to execute.
        kubectl_output (Optional[str]): The output returned by the executed command.
    """
    step: int
    kubectl_command: Optional[str] = None
    kubectl_output: Optional[str] = None


class AIResponse(BaseModel):
    """
    Represents the structured response returned from the AI model.
    
    Attributes:
        intent (str): The user’s high-level intent (e.g., "List all pods").
        steps (list[Step]): List of steps taken (commands + outputs).
        final_output (Optional[str]): Human-readable summary of results.
    """
    intent: str
    steps: list[Step]
    final_output: Optional[str] = None

# ------------------------------------------------------------------------------
# Core Function: ai_plan
# ------------------------------------------------------------------------------

async def ai_plan(intent_text: str, steps_yaml: dict) -> AIResponse:
    """
    Given a high-level user intent and previous execution steps,
    request a response plan from Google Gemini to determine next Kubernetes actions.
    
    The function operates in two modes:
    1. Suggests the next `kubectl` command if the intent is not yet fulfilled.
    2. Generates a final, human-readable summary once relevant output is available.

    Args:
        intent_text (str): The high-level user request (e.g., "Check if pods are running").
        steps_yaml (dict): History of previous steps (commands + outputs).

    Returns:
        AIResponse: Structured response with next command(s) or final summary.
    """

    # Construct AI prompt with context, user intent, and prior steps.
    prompt = f"""
You are a Kubernetes assistant. Your task is to help users manage their Kubernetes clusters by executing kubectl commands and providing a clear, human-readable summary of the results.

The user's high-level intent is:
{intent_text}

You have access to the history of previous steps, which includes the command executed and its output. Your job is to analyze this history and determine the next action.

Previous steps:
{json.dumps(steps_yaml, indent=2)}

Your decision should be one of two things:
1.  **If no command has been run yet**, or if the previous command did not achieve the user's intent, generate the next appropriate 'kubectl' command to execute. Place this command in the 'kubectl_command' field of the next step.
2.  **If a command has been successfully executed and its output is available in 'kubectl_output'**, and you believe the user's intent has been fulfilled, generate a comprehensive, human-readable summary of the results based on the 'kubectl_output'. This summary should be placed in the 'final_output' field. The 'steps' array should remain as it is.

Return a JSON object with the following schema. Do NOT include any other text or markdown formatting outside of the JSON block.

{{
  "intent": "string",
  "steps": [
    {{
      "step": "integer",
      "kubectl_command": "string or null",
      "kubectl_output": "string or null"
    }}
  ],
  "final_output": "string or null"
}}

Here is an example of what to return when you have a final output:
{{
  "intent": "{intent_text}",
  "steps": [
    {{
      "step": 1,
      "kubectl_command": "kubectl get pods -A",
      "kubectl_output": "NAMESPACE NAME...\\ndefault nginx-deployment..."
    }}
  ],
  "final_output": "Here are all the pods across all namespaces:\\nNAMESPACE NAME...\\ndefault nginx-deployment..."
}}
"""
    try:
        # Initialize Gemini model instance.
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Send the prompt asynchronously and request deterministic output (temperature=0).
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0)
        )

        # Extract raw text from Gemini response (format may vary depending on SDK version).
        text = response.text if hasattr(response, "text") else response.candidates[0].content.parts[0].text

        # Clean any markdown fences (```json ... ```) to ensure valid JSON.
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"```$", "", text)

        # Parse JSON response and validate against AIResponse schema.
        data = json.loads(text)
        return AIResponse(**data)

    except Exception as e:
        # Log traceback for debugging; return structured error response for frontend.
        traceback.print_exc()
        return AIResponse(
            intent=intent_text,
            steps=steps_yaml["steps"],
            final_output=f"Error: An error occurred while generating the response: {e}"
        )
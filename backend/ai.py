import os
import logging
import json
import traceback
import re

from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gemini configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set. Please set it in your deployment.")
    raise ValueError("GEMINI_API_KEY environment variable not set.")

try:
    logger.debug(f"Attempting to configure Gemini API with key: {GEMINI_API_KEY[:4]}...")
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configuration successful.")
except Exception as e:
    logger.error("FATAL: Error during Gemini startup.")
    logger.error(traceback.format_exc())
    raise RuntimeError(f"Application startup failed: {e}")

# Default model
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

class Intent(BaseModel):
    action: str
    resource: str
    namespace: Optional[str] = None
    all_namespaces: Optional[bool] = False
    name: Optional[str] = None   # allow single resource targeting like "pod mypod"

async def plan_intent_llm(user_text: str) -> Intent:
    """
    Plans an intent based on a human-like text prompt using the Gemini API.
    """
    logger.info("Using Gemini LLM for intent planning")

    prompt_gemini = f"""
    You are a Kubernetes assistant. Your task is to extract the user's intent from a text prompt.
    You must identify the 'action' and 'resource' the user wants to perform.
    If a namespace is specified, you must extract it. 
    If the user asks for all namespaces, set `all_namespaces` to true.
    If the user specifies a particular resource name (like a pod name), include it in "name".

    The 'action' must be one of: "get", "describe", "logs", or "delete".
    The 'resource' must be a valid Kubernetes resource, such as:
      - "pods"
      - "deployments"
      - "services"
      - "ingresses"
      - "nodes"
      - "namespaces"
      - "configmaps"
      - "secrets"
      - "events"

    Special cases:
      - For "logs", the resource is always "pod", and you must include the pod name in "name".
      - For "delete" or "describe", you should include the resource name in "name" if provided.

    The output must be a single JSON object with this schema:
    {{
      "action": "<action>",
      "resource": "<resource>",
      "namespace": "<namespace>",   // Optional
      "all_namespaces": <boolean>,  // Optional
      "name": "<name>"              // Optional, only if user specifies a single resource name
    }}

    Example:
    Prompt: "show pods in operations namespace"
    Output: {{ "action": "get", "resource": "pods", "namespace": "operations" }}

    Example:
    Prompt: "get logs for pod my-app-123 in prod"
    Output: {{ "action": "logs", "resource": "pod", "namespace": "prod", "name": "my-app-123" }}

    ---
    Prompt: "{user_text}"
    Output:
    """

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = await model.generate_content_async(
            prompt_gemini,
            generation_config=genai.GenerationConfig(
                temperature=0.0,
            )
        )

        # Extract text from Gemini response
        intent_json_str = None
        if hasattr(response, "text") and response.text:
            intent_json_str = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                intent_json_str = parts[0].text.strip()

        if not intent_json_str:
            logger.error("No usable text response from Gemini API.")
            raise ValueError("gemini_error: No usable text response from Gemini API.")

        # Clean markdown fences if Gemini wrapped the JSON
        if intent_json_str.startswith("```"):
            intent_json_str = re.sub(r"^```[a-zA-Z]*\n?", "", intent_json_str)
            intent_json_str = re.sub(r"```$", "", intent_json_str).strip()

        logger.info(f"Gemini raw response: {intent_json_str}")

        try:
            intent_data = json.loads(intent_json_str)
            return Intent(**intent_data)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from Gemini response")
            logger.error(f"Raw response: {intent_json_str}")
            raise ValueError(f"gemini_error: Invalid JSON from Gemini. Raw response: {intent_json_str}")

    except Exception as e:
        logger.error("An unexpected error occurred with the Gemini API call.")
        logger.error(traceback.format_exc())
        raise ConnectionError(f"gemini_error: An error occurred with the Gemini API: {e}")
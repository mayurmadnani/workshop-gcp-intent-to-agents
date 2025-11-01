import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import google.auth

# Load environment variables
root_dir = Path(__file__).parent.parent
dotenv_path = root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure Google Cloud
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1")

# Configure model connection
gemma_model_name = os.getenv("GEMMA_MODEL_NAME", "gemma3:270m")
# Location of Ollama server
api_base = os.getenv("OLLAMA_API_BASE", "localhost:11434")

INSTRUCTIONS = """
You are a SQL Agent.

Input: either (a) a natural language request about data, or (b) a SQL query.

Output:
- If input is natural language: return a single SQL query that fulfills the request.
- If input is SQL: return a short explanation of what the query does.

Rules:
- Use ANSI-SQL unless otherwise specified.
- Default to SELECT queries unless user explicitly asks for modification.
- Format SQL with clear indentation and line breaks.
- Explanations must be concise, 2–4 sentences maximum.
- Return only SQL or only explanation, never both.
"""

# Gemma agent as conversational assistant
intent_agent = Agent(
    model=LiteLlm(model=f"ollama_chat/{gemma_model_name}", api_base=api_base),
    name="intent_agent",
    description="natural language intents into functional agent",
    instruction=f"<start_of_turn>user {INSTRUCTIONS}<end_of_turn>\n"
                "<start_of_turn>model",
    tools=[],
)

# Set as root agent
root_agent = intent_agent

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables
load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app_args = {"agents_dir": AGENT_DIR, "web": True}

# Create FastAPI app with ADK integration
app: FastAPI = get_fast_api_app(**app_args)

# Update app metadata
app.title = "Intent to Agent"
app.description = "natural language intents into functional agents"
app.version = "0.0.1"


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "intent_agent"}


@app.get("/")
def root():
    return {
        "service": "Intent to Agent",
        "description": "natural language intents into functional agents",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

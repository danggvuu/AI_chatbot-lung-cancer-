from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import requests
import os
import yaml

router = APIRouter()

config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)
        OLLAMA_API_URL = settings.get("llm", {}).get("ollama_url", "http://localhost:11434")
        OLLAMA_MODEL = settings.get("llm", {}).get("default_model", "qwen2.5:3b")
except Exception:
    OLLAMA_API_URL = "http://localhost:11434"
    OLLAMA_MODEL = "qwen2.5:3b"

@router.get("/health")
async def health():
    """Verify backend health and check connections."""
    ollama_status = "offline"
    available_models = []
    
    try:
        r = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_status = "online"
            models_data = r.json()
            available_models = [m["name"] for m in models_data.get("models", [])]
    except Exception:
        pass
        
    # We will hook this up to the actual retriever later
    kb_loaded = True
    
    return {
        "status": "healthy",
        "database_loaded": kb_loaded,
        "database_records": 0, # Placeholder
        "ollama_connection": ollama_status,
        "ollama_url": OLLAMA_API_URL,
        "ollama_model": OLLAMA_MODEL,
        "ollama_model_available": OLLAMA_MODEL in available_models or f"{OLLAMA_MODEL}:latest" in available_models,
        "available_models": available_models
    }

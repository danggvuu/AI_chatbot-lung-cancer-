import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.chat_service import ChatService
from api.server import create_app
from fastapi.testclient import TestClient

def test_app_creation():
    app = create_app()
    assert app is not None
    
def test_health_endpoint():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

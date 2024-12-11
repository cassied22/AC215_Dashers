from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/app')
from api.service import app

# Create a test client
client = TestClient(app)

def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Daily Meal Assistant"}

def test_llm_chat_route():
    response = client.get("/llm")
    # Assert response status, 404 expected if no endpoint in the router
    assert response.status_code in [200, 404]

def test_llm_rag_chat_route():
    response = client.get("/llm-rag")
    # Assert response status, 404 expected if no endpoint in the router
    assert response.status_code in [200, 404]

def test_llm_detection_chat_route():
    response = client.get("/llm-food-detection")
    # Assert response status, 404 expected if no endpoint in the router
    assert response.status_code in [200, 404]

def test_youtube_route():
    response = client.get("/youtube?recipe_name=Pasta")
    assert response.status_code in [200, 404]

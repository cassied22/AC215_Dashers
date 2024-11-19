import pytest
import time
import subprocess
import os
from pathlib import Path
import http.client
import json
import uuid
import docker

BASE_URL = "localhost"
PORT = 9000
CONTAINER_NAME = "daily-meal-api-service"
TEST_IMAGE_PATH = str(Path(__file__).parent.parent / "image.jpg")
TEST_SESSION_ID = str(uuid.uuid4())

def make_request(method, path, data=None, headers=None):
    conn = http.client.HTTPConnection(BASE_URL, PORT)
    if headers is None:
        headers = {
            'Content-Type': 'application/json',
            'X-Session-ID': TEST_SESSION_ID
        }
    
    conn.request(method, path, body=json.dumps(data) if data else None, headers=headers)
    return conn.getresponse()

@pytest.fixture(scope="session")
def api_service():
    client = docker.from_env()
    try:
        container = client.containers.get(CONTAINER_NAME)
        if container.status != "running":
            container.start()
    except:
        api_service_dir = str(Path(__file__).parent.parent.parent / "api_service")
        subprocess.run(f"cd {api_service_dir} && ./docker-shell.sh", shell=True)
    
    for _ in range(30):
        try:
            conn = http.client.HTTPConnection(BASE_URL, PORT)
            conn.request("GET", "/llm/chats", headers={'X-Session-ID': TEST_SESSION_ID})
            break
        except:
            time.sleep(1)
    
    yield

@pytest.mark.usefixtures("api_service")
class TestAPIService:
    def test_get_chats(self):
        response = make_request("GET", "/llm/chats")
        assert response.status == 200
        data = json.loads(response.read())
        assert isinstance(data, list)

    def test_start_chat(self):
        payload = {
            "content": "What are healthy breakfast options?"
        }
        response = make_request("POST", "/llm/chats", data=payload)
        assert response.status == 200
        data = json.loads(response.read())
        assert "chat_id" in data
        assert "messages" in data
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"
        return data["chat_id"]

    def test_continue_chat(self):
        chat_id = self.test_start_chat()
        payload = {
            "content": "What about lunch options?"
        }
        response = make_request("POST", f"/llm/chats/{chat_id}", data=payload)
        assert response.status == 200
        data = json.loads(response.read())
        assert len(data["messages"]) == 4

    def test_get_specific_chat(self):
        chat_id = self.test_start_chat()
        response = make_request("GET", f"/llm/chats/{chat_id}")
        assert response.status == 200
        data = json.loads(response.read())
        assert data["chat_id"] == chat_id

    def test_invalid_chat_id(self):
        invalid_id = str(uuid.uuid4())
        response = make_request("GET", f"/llm/chats/{invalid_id}")
        assert response.status == 404
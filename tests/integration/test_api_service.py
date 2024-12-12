import pytest
import time
import subprocess
from pathlib import Path
import http.client
import json
import uuid
import docker
import base64

BASE_URL = "localhost"
PORT = 9000
CONTAINER_NAME = "daily-meal-api-service"
TEST_IMAGE_PATH = str(Path(__file__).parent / "food_pic.jpeg")
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
        # List of endpoints to test
        endpoints = ["/llm/chats", "/llm-rag/chats"]

        for endpoint in endpoints:
            response = make_request("GET", endpoint)
            assert response.status == 200, f"Failed at endpoint {endpoint} with status {response.status}"
            data = json.loads(response.read())
            assert isinstance(data, list), f"Expected data to be a list at endpoint {endpoint}"

    def test_start_chat(self):
        endpoints = ["/llm/chats", "/llm-rag/chats", "/llm-food-detection/chats"]
        chat_ids = {}
        for endpoint in endpoints:
            payload = {
                "content": "What are healthy breakfast options?"
            }
            response = make_request("POST", endpoint, data=payload)
            assert response.status == 200, f"Failed at endpoint {endpoint} with status {response.status}"
            data = json.loads(response.read())
            assert "chat_id" in data
            assert "messages" in data
            assert len(data["messages"]) == 2
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][1]["role"] == "assistant"
            chat_ids[endpoint] = data["chat_id"]
        return chat_ids

    def test_continue_chat(self):
        endpoints = ["/llm/chats", "/llm-rag/chats"]
        chat_ids = self.test_start_chat()
        for endpoint in endpoints:
            chat_id = chat_ids[endpoint]
            payload = {
                "content": "What about lunch options?"
            }
            response = make_request("POST", f"{endpoint}/{chat_id}", data=payload)
            assert response.status == 200, f"Failed at endpoint {endpoint} with status {response.status}"
            data = json.loads(response.read())
            assert len(data["messages"]) == 4

    def test_get_specific_chat(self):
        endpoints = ["/llm/chats", "/llm-rag/chats"]
        chat_ids = self.test_start_chat()
        for endpoint in endpoints:
            chat_id = chat_ids[endpoint]
            response = make_request("GET", f"{endpoint}/{chat_id}")
            assert response.status == 200, f"Failed at endpoint {endpoint} with status {response.status}"
            data = json.loads(response.read())
            assert data["chat_id"] == chat_id

    def test_invalid_chat_id(self):
        endpoints = ["/llm/chats", "/llm-rag/chats"]
        for endpoint in endpoints:
            invalid_id = str(uuid.uuid4())
            response = make_request("GET", f"{endpoint}/{invalid_id}")
            assert response.status == 404

    # user input images, llm continues with text chat
    def test_start_chat_with_image(self):
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            image_data = image_file.read()
        
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        payload = {
            "content": "Identify the list of food items shown in this image",
            "image": f"data:image/jpeg;base64,{encoded_image}"
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Session-ID': TEST_SESSION_ID
        }

        response = make_request("POST", "/llm-food-detection/chats", data=payload, headers=headers)
        assert response.status == 200, f"Failed to upload image with status {response.status}"
        
        data = json.loads(response.read())
        assert isinstance(data, dict), "Expected data to be a dictionary"
        assert "messages" in data, "Expected 'messages' field in the response data"
        assert len(data["messages"]) == 2, "Expected two messages in the response (user and gpt)"
        assert data["messages"][1]["role"] == "gpt", "Expected the second message to be from 'gpt'"
        assert "results" in data["messages"][1], "Expected 'results' in the gpt message"
        return data["chat_id"], data["messages"][0]["message_id"]
    
    def test_youtube(recipe_name):
        recipe_name = "chocolate chip cookies"
        payload = {
            "recipe_name": recipe_name
        }
        response = make_request("GET", "/youtube", data=payload)
        assert response.status == 200, f"Failed at endpoint /youtube with status {response.status}"
        
        data = json.loads(response.read())
        assert len(data['videos']) > 0

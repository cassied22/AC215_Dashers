import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys

sys.path.append('/app')
from api.routers.youtube import router

# Create a test client
app = router
client = TestClient(app)

@pytest.fixture
def mock_openai_api_key():
    with patch("os.getenv") as mock_getenv, patch("os.path.isfile") as mock_isfile, patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_getenv.return_value = "path/to/api_key.json"
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = '{"OPENAI_API_KEY": "fake_api_key"}'
        yield

@pytest.fixture
def mock_agent_run():
    with patch("api.routers.youtube.Agent") as mock_agent:
        # Mock response content
        mock_run_response = MagicMock()
        mock_run_response.content = (
            "[Video 1](https://youtube.com/video1)\n"
            "[Video 2](https://youtube.com/video2)"
        )
        
        # Mock the Agent's run method
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = mock_run_response
        mock_agent.return_value = mock_agent_instance

        yield mock_agent

def test_search_youtube(mock_openai_api_key, mock_agent_run):
    # Call the endpoint
    recipe_name = "Pasta"
    response = client.get(f"/?recipe_name={recipe_name}")

    # Assertions
    assert response.status_code == 200
    data = response.json()

    assert "videos" in data
    assert len(data["videos"]) == 2

    assert data["videos"][0]["name"] == "Video 1"
    assert data["videos"][0]["url"] == "https://youtube.com/video1"

    assert data["videos"][1]["name"] == "Video 2"
    assert data["videos"][1]["url"] == "https://youtube.com/video2"



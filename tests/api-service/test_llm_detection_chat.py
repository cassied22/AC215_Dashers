import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
import sys
sys.path.append('/app')
from api.routers.llm_detection_chat import start_chat_with_llm

@pytest.fixture
def mock_chat_manager():
    # Patch the chat_manager instance
    with patch("api.routers.llm_detection_chat.chat_manager") as mock_chat_manager:
        mock_chat_manager.save_chat = MagicMock()
        yield mock_chat_manager

@pytest.fixture
def mock_uuid():
    # Mock uuid.uuid4 to return different values for each call
    with patch("uuid.uuid4", side_effect=["mock-uuid-1", "mock-uuid-2", "mock-uuid-3"]) as mock:
        yield mock

@pytest.fixture
def mock_time():
    with patch("time.time", return_value=1234567890) as mock:
        yield mock

@pytest.fixture
def mock_utils():
    with patch("api.routers.llm_detection_chat.create_chat_session", return_value="mock_session") as mock_create_session, \
         patch("api.routers.llm_detection_chat.generate_chat_response", return_value="Assistant Response") as mock_generate_response, \
         patch("api.routers.llm_detection_chat.identify_food_gpt", return_value="Prediction Results") as mock_identify_food_gpt, \
         patch("api.utils.llm_detection_utils.chat_sessions", {}) as mock_chat_sessions:
        
        yield {
            "create_chat_session": mock_create_session,
            "generate_chat_response": mock_generate_response,
            "identify_food_gpt": mock_identify_food_gpt,
            "chat_sessions": mock_chat_sessions,
        }

@pytest.mark.asyncio
async def test_start_chat_with_image_message(mock_utils, mock_chat_manager, mock_uuid, mock_time):
    base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA"
    message = {"content": "", "image": base64_image}
    x_session_id = "test-session-id"

    # Call the function
    result = await start_chat_with_llm(message=message, x_session_id=x_session_id)

    # Expected response
    expected_response = {
        "chat_id": "mock-uuid-1",
        "title": "Image chat...",
        "dts": 1234567890,
        "messages": [
            {
                "content": "",
                "image": base64_image,
                "message_id": "mock-uuid-2",
                "role": "user",
            },
            {
                "message_id": "mock-uuid-3",
                "role": "gpt",
                "results": "Prediction Results",
            },
        ],
    }

    # Assertions
    assert result == expected_response
    mock_utils["create_chat_session"].assert_called_once()
    mock_utils["identify_food_gpt"].assert_called_once()
    mock_chat_manager.save_chat.assert_called_once_with(expected_response, x_session_id)

@pytest.mark.asyncio
async def test_start_chat_with_text_message(mock_utils, mock_chat_manager, mock_uuid, mock_time):
    message = {"content": "Hello, how are you?"}
    x_session_id = "test-session-id"

    # Call the function
    result = await start_chat_with_llm(message=message, x_session_id=x_session_id)

    # Expected response
    expected_response = {
        "chat_id": "mock-uuid-1",
        "title": "Hello, how are you?...",
        "dts": 1234567890,
        "messages": [
            {
                "content": "Hello, how are you?",
                "message_id": "mock-uuid-2",
                "role": "user",
            },
            {
                "message_id": "mock-uuid-3",
                "role": "assistant",
                "content": "Assistant Response",
            },
        ],
    }

    # Assertions
    assert result == expected_response
    mock_utils["create_chat_session"].assert_called_once()
    mock_utils["generate_chat_response"].assert_called_once_with("mock_session", {
        "content": "Hello, how are you?",
        "message_id": "mock-uuid-2",
        "role": "user",
    })
    mock_chat_manager.save_chat.assert_called_once_with(expected_response, x_session_id)

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
import sys
sys.path.append('/app')
from api.routers.llm_chat import (
    get_chats,
    get_chat,
    start_chat_with_llm,
    continue_chat_with_llm
)

@pytest.fixture
def mock_chat_manager():
    # Patch the chat_manager instance
    with patch("api.routers.llm_chat.chat_manager") as mock_chat_manager:
        mock_chat_manager.save_chat = MagicMock()
        mock_chat_manager.get_chat = MagicMock()
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
    with patch("api.routers.llm_chat.create_chat_session", return_value="mock_session") as mock_create_session, \
         patch("api.routers.llm_chat.generate_chat_response", return_value="Assistant Response") as mock_generate_response, \
         patch("api.routers.llm_chat.extract_title_from_response", return_value="Mock Title") as mock_extract_title, \
         patch("api.routers.llm_chat.rebuild_chat_session", return_value="mock_session") as mock_rebuild_session, \
         patch("api.utils.llm_utils.chat_sessions", {}) as mock_chat_sessions:
        
        yield {
            "create_chat_session": mock_create_session,
            "generate_chat_response": mock_generate_response,
            "extract_title_from_response": mock_extract_title,
            "rebuild_chat_session": mock_rebuild_session,
            "chat_sessions": mock_chat_sessions,
        }

# Testing get_chats in isolation
@pytest.mark.asyncio
async def test_get_chats(mock_chat_manager):
    # Mock the behavior of get_recent_chats
    mock_chat_manager.get_recent_chats.return_value = [
        {"chat_id": "1", "title": "Chat One", "dts": 1234567890},
        {"chat_id": "2", "title": "Chat Two", "dts": 1234567889}
    ]
    
    # Call the function
    result = await get_chats(x_session_id="test-session-id", limit=2)
    print(result)
    # Assertions
    assert result == [
        {"chat_id": "1", "title": "Chat One", "dts": 1234567890},
        {"chat_id": "2", "title": "Chat Two", "dts": 1234567889}
    ]
    mock_chat_manager.get_recent_chats.assert_called_once_with("test-session-id", 2)

# Testing get_chat in isolation
@pytest.mark.asyncio
async def test_get_chat(mock_chat_manager):
    mock_chat_manager.get_chat.return_value = {
        "chat_id": "123",
        "title": "Test Chat",
        "messages": []
    }
    
    # Call the function
    result = await get_chat(chat_id="123", x_session_id="test-session-id")
    
    # Assertions
    assert result == {
        "chat_id": "123",
        "title": "Test Chat",
        "messages": []
    }
    mock_chat_manager.get_chat.assert_called_once_with("123", "test-session-id")

# Testing get_chat with not found
@pytest.mark.asyncio
async def test_get_chat_not_found(mock_chat_manager):
    # Mock the behavior of get_chat to return None (chat not found)
    mock_chat_manager.get_chat.return_value = None
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await get_chat(chat_id="123", x_session_id="test-session-id")
    
    # Assertions
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Chat not found"
    mock_chat_manager.get_chat.assert_called_once_with("123", "test-session-id")

# Testing start_chat_with_llm in isolation
@pytest.mark.asyncio
async def test_start_chat_with_llm_success(mock_chat_manager, mock_utils, mock_uuid, mock_time):
    message = {"content": "Hello, how are you?"}
    x_session_id = "test-session-id"
    
    # Call the function
    result = await start_chat_with_llm(message=message, x_session_id=x_session_id)
    
    # Expected chat response structure
    expected_response = {
        "chat_id": "mock-uuid-1",
        "title": "Mock Title...",
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
        ]
    }
    
    # Assertions
    assert result == expected_response
    mock_utils["create_chat_session"].assert_called_once()
    mock_utils["generate_chat_response"].assert_called_once_with("mock_session", {
        "content": "Hello, how are you?",
        "message_id": "mock-uuid-2",
        "role": "user"
    })
    mock_utils["extract_title_from_response"].assert_called_once_with("Assistant Response")
    mock_chat_manager.save_chat.assert_called_once_with(expected_response, x_session_id)

# Testing continue_chat_with_llm in isolation
@pytest.mark.asyncio
async def test_continue_chat_with_llm_success(mock_utils, mock_chat_manager, mock_uuid, mock_time):
    # Mock existing chat
    mock_chat_manager.get_chat.return_value = {
        "chat_id": "123",
        "title": "Test Chat",
        "messages": []
    }
    mock_utils["chat_sessions"]["123"] = "mock_session"

    message = {"content": "Continue this conversation"}
    x_session_id = "test-session-id"

    # Call the function
    result = await continue_chat_with_llm(chat_id="123", message=message, x_session_id=x_session_id)

    # Expected chat structure after update
    expected_chat = {
        "chat_id": "123",
        "title": "Mock Title",
        "dts": 1234567890,
        "messages": [
            {
                "content": "Continue this conversation",
                "message_id": "mock-uuid-1",
                "role": "user",
            },
            {
                "message_id": "mock-uuid-2",
                "role": "assistant",
                "content": "Assistant Response",
            },
        ],
    }

    # Assertions
    assert result == expected_chat
    mock_chat_manager.get_chat.assert_called_once_with("123", x_session_id)
    mock_utils["generate_chat_response"].assert_called_once_with("mock_session", {
        "content": "Continue this conversation",
        "message_id": "mock-uuid-1",
        "role": "user",
    })
    mock_chat_manager.save_chat.assert_called_once_with(expected_chat, x_session_id)

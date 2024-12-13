import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from api.utils.llm_rag_utils import ModelType
import sys
sys.path.append('/app')
from api.routers.llm_rag_chat import (
    get_chats,
    get_chat,
    start_chat_with_llm,
    continue_chat_with_llm
)

@pytest.fixture
def mock_chat_manager():
    # Patch the chat_manager instance
    with patch("api.routers.llm_rag_chat.chat_manager") as mock_chat_manager:
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
    with patch("api.routers.llm_rag_chat.create_chat_session", return_value="mock_session") as mock_create_session, \
         patch("api.routers.llm_rag_chat.generate_chat_response", return_value="Assistant Response") as mock_generate_response, \
         patch("api.routers.llm_rag_chat.extract_title_from_response", return_value="Mock Title") as mock_extract_title, \
         patch("api.routers.llm_rag_chat.rebuild_chat_session", return_value="mock_session") as mock_rebuild_session, \
         patch("api.utils.llm_rag_utils.chat_sessions", {}) as mock_chat_sessions:
        
        yield {
            "create_chat_session": mock_create_session,
            "generate_chat_response": mock_generate_response,
            "extract_title_from_response": mock_extract_title,
            "rebuild_chat_session": mock_rebuild_session,
            "chat_sessions": mock_chat_sessions,
        }

@pytest.mark.asyncio
async def test_get_chats(mock_chat_manager):
    mock_chat_manager.get_recent_chats.return_value = [
        {"chat_id": "123", "title": "Chat Title"}
    ]
    result = await get_chats(x_session_id="test-session-id", limit=10)
    assert result == [{"chat_id": "123", "title": "Chat Title"}]
    mock_chat_manager.get_recent_chats.assert_called_once_with("test-session-id", 10)

@pytest.mark.asyncio
async def test_get_chat(mock_chat_manager):
    mock_chat_manager.get_chat.return_value = {"chat_id": "123", "title": "Chat Title"}
    result = await get_chat(chat_id="123", x_session_id="test-session-id")
    assert result == {"chat_id": "123", "title": "Chat Title"}
    mock_chat_manager.get_chat.assert_called_once_with("123", "test-session-id")

@pytest.mark.asyncio
async def test_get_chat_not_found(mock_chat_manager):
    mock_chat_manager.get_chat.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await get_chat(chat_id="123", x_session_id="test-session-id")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Chat not found"

@pytest.mark.asyncio
async def test_start_chat_with_llm(mock_utils, mock_chat_manager, mock_uuid, mock_time):
    message = {"content": "Hello, how are you?"}
    x_session_id = "test-session-id"

    result = await start_chat_with_llm(message=message, x_session_id=x_session_id, modeltype=ModelType.RAW)
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
        ],
    }
    print('Result:', result)
    print('Expected_response:', expected_response)
    assert result == expected_response
    mock_utils["create_chat_session"].assert_called_once_with(model=ModelType.RAW)
    mock_utils["generate_chat_response"].assert_called_once()
    mock_chat_manager.save_chat.assert_called_once_with(expected_response, x_session_id)

@pytest.mark.asyncio
async def test_continue_chat_with_llm(mock_utils, mock_chat_manager, mock_uuid, mock_time):
    mock_chat_manager.get_chat.return_value = {
        "chat_id": "123",
        "title": "Test Chat",
        "messages": []
    }
    mock_utils["chat_sessions"]["123"] = "existing_session"
    mock_utils["generate_chat_response"].return_value = "Mock Assistant Response"

    message = {"content": "Continue the chat"}
    x_session_id = "test-session-id"

    result = await continue_chat_with_llm(chat_id="123", message=message, x_session_id=x_session_id, modeltype=ModelType.RAW)
    expected_chat = {
        "chat_id": "123",
        "title": "Mock Title...",
        "messages": [
            {
                "content": "Continue the chat",
                "message_id": "mock-uuid-1",
                "role": "user",
            },
            {
                "message_id": "mock-uuid-2",
                "role": "assistant",
                "content": "Mock Assistant Response",
            },
        ],
        "dts": 1234567890,
    }
    print('Result:', result)
    print('Expected_response:', expected_chat)
    assert result == expected_chat
    mock_chat_manager.get_chat.assert_called_once_with("123", x_session_id)
    mock_utils["generate_chat_response"].assert_called_once()
    mock_chat_manager.save_chat.assert_called_once_with(expected_chat, x_session_id)
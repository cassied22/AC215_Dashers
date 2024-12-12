import pytest
import os
import json
from unittest.mock import patch, mock_open, MagicMock
import sys
sys.path.append('/app')
from api.utils.chat_utils import ChatHistoryManager


@pytest.fixture
def chat_manager():
    """Fixture to initialize ChatHistoryManager with a test directory"""
    return ChatHistoryManager(model="test-model", history_dir="test-history")


@patch("os.makedirs")
def test_ensure_directories(mock_makedirs, chat_manager):
    # Ensure directories are created
    chat_manager._ensure_directories()
    mock_makedirs.assert_any_call("test-history/test-model", exist_ok=True)
    mock_makedirs.assert_any_call("test-history/test-model/images", exist_ok=True)


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_load_image(mock_open, mock_exists, chat_manager):
    # Test loading an image successfully
    result = chat_manager._load_image("relative/path/to/image.png")
    assert result == "ZmFrZV9pbWFnZV9kYXRh"  # Base64 encoded "fake_image_data"
    mock_open.assert_called_once_with("test-history/test-model/relative/path/to/image.png", "rb")


@patch("os.path.exists", return_value=True)
@patch("builtins.open", side_effect=Exception("File error"))
def test_load_image_failure(mock_open, mock_exists, chat_manager):
    # Test failure to load an image
    result = chat_manager._load_image("relative/path/to/image.png")
    assert result is None
    mock_open.assert_called_once()



@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("base64.b64decode", return_value=b"decoded_image_data")
def test_save_image(mock_b64decode, mock_open, mock_makedirs, chat_manager):
    # Test saving an image successfully
    result = chat_manager._save_image("chat-id", "message-id", "data:image/png;base64,ZmFrZV9pbWFnZV9kYXRh")
    assert result == "images/chat-id/message-id.png"
    mock_makedirs.assert_called_once_with("test-history/test-model/images/chat-id", exist_ok=True)
    mock_open.assert_called_once_with("test-history/test-model/images/chat-id/message-id.png", "wb")
    mock_open().write.assert_called_once_with(b"decoded_image_data")


@patch("builtins.open", side_effect=Exception("File error"))
def test_save_image_failure(mock_open, chat_manager):
    # Test failure to save an image
    result = chat_manager._save_image("chat-id", "message-id", "data:image/png;base64,ZmFrZV9pbWFnZV9kYXRh")
    assert result == ""
    mock_open.assert_called_once()


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_save_chat(mock_open, mock_makedirs, chat_manager):
    # Test saving a chat
    chat = {
        "chat_id": "123",
        "messages": [
            {"content": "Hello", "message_id": "1", "image": "base64_image_data"},
            {"content": "Hi", "message_id": "2"}
        ]
    }
    chat_manager.save_chat(chat, "session-1")
    mock_makedirs.assert_any_call("test-history/test-model/session-1", exist_ok=True)
    mock_makedirs.assert_any_call("test-history/test-model/images/123", exist_ok=True)
    mock_open.assert_called_once_with("test-history/test-model/session-1/123.json", "w", encoding="utf-8")

@patch("builtins.open", side_effect=Exception("File write error"))
def test_save_chat_exception(mock_open, chat_manager):
    # Test exception when saving a chat
    chat = {
        "chat_id": "123",
        "messages": [
            {"content": "Hello", "message_id": "1", "image": "base64_image_data"}
        ]
    }
    with pytest.raises(Exception) as exc_info:
        chat_manager.save_chat(chat, "session-1")
    assert str(exc_info.value) == "File write error"
    mock_open.assert_called_once()

@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"chat_id": "123"}))
def test_get_chat(mock_open, chat_manager):
    # Test getting a specific chat
    result = chat_manager.get_chat("123", "session-1")
    assert result == {"chat_id": "123"}
    mock_open.assert_called_once_with("test-history/test-model/session-1/123.json", "r", encoding="utf-8")

@patch("builtins.open", side_effect=Exception("File read error"))
def test_get_chat_exception(mock_open, chat_manager):
    # Test exception when reading a chat
    result = chat_manager.get_chat("123", "session-1")
    assert result == {}  # Empty dict is returned on failure
    mock_open.assert_called_once()

@patch("glob.glob", return_value=["test-history/test-model/session-1/123.json"])
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"chat_id": "123", "dts": 1234567890}))
def test_get_recent_chats(mock_open, mock_glob, chat_manager):
    # Test getting recent chats
    result = chat_manager.get_recent_chats("session-1", limit=1)
    assert result == [{"chat_id": "123", "dts": 1234567890}]
    mock_glob.assert_called_once_with("test-history/test-model/session-1/*.json")
    mock_open.assert_called_once_with("test-history/test-model/session-1/123.json", "r", encoding="utf-8")

@patch("glob.glob", return_value=["test-history/test-model/session-1/123.json"])
@patch("builtins.open", side_effect=Exception("File read error"))
def test_get_recent_chats_exception(mock_open, mock_glob, chat_manager):
    # Test exception when loading recent chats
    result = chat_manager.get_recent_chats("session-1", limit=1)
    assert result == []  # Empty list is returned on failure
    mock_glob.assert_called_once_with("test-history/test-model/session-1/*.json")
    mock_open.assert_called_once_with("test-history/test-model/session-1/123.json", "r", encoding="utf-8")

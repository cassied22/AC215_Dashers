import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import re

import sys
sys.path.append('/app')
from api.utils.llm_utils import (
    create_chat_session,
    generate_chat_response,
    rebuild_chat_session,
    extract_title_from_response
)

generation_config = {
    "max_output_tokens": 3000,
    "temperature": 0.1,
    "top_p": 0.95
}

@pytest.fixture
def mock_generative_model():
    # Mock the generative_model instance
    with patch("api.utils.llm_utils.generative_model") as mock_generative_model:
        mock_session = MagicMock()
        mock_generative_model.start_chat.return_value = mock_session
        yield mock_generative_model

@pytest.fixture
def mock_chat_session():
    # Mock a ChatSession instance
    mock_session = MagicMock()
    yield mock_session

def test_create_chat_session(mock_generative_model):
    # Call the function
    session = create_chat_session()

    # Assertions
    assert session == mock_generative_model.start_chat.return_value  # Ensure the returned session is correct
    mock_generative_model.start_chat.assert_called_once()

@patch("api.utils.llm_utils.generative_model.start_chat") 
def test_generate_chat_response_success(mock_start_chat, mock_chat_session):
    # Set up the mock for start_chat to return the mock_chat_session
    mock_start_chat.return_value = mock_chat_session

    # Set up the mock response for send_message
    mock_response = MagicMock()
    mock_response.text = "Title: Spaghetti Bolognese"
    mock_chat_session.send_message.return_value = mock_response

    # Test input
    message = {"content": "Ingredients: pasta, tomato sauce, ground beef"}

    # Call the function with the mocked chat session
    result = generate_chat_response(mock_chat_session, message)

    # Assertions
    assert result == "Title: Spaghetti Bolognese"
    mock_chat_session.send_message.assert_called_once_with(
        ["Ingredients: pasta, tomato sauce, ground beef"],
        generation_config=generation_config
    )

def test_generate_chat_response_no_content(mock_generative_model):
    message = {}

    with pytest.raises(HTTPException) as excinfo:
        generate_chat_response(mock_generative_model, message)

    assert excinfo.value.status_code == 500
    assert "Message must contain food list" in str(excinfo.value.detail)

@patch("api.utils.llm_utils.create_chat_session")
def test_rebuild_chat_session(mock_create_chat_session):
    mock_session = MagicMock()
    mock_create_chat_session.return_value = mock_session

    chat_history = [
        {"role": "user", "content": "Ingredients: chicken, rice"},
        {"role": "user", "content": "Add some spices"}
    ]

    with patch("api.utils.llm_utils.generate_chat_response") as mock_generate_response:
        rebuild_chat_session(chat_history)

        assert mock_generate_response.call_count == 2
        mock_generate_response.assert_any_call(mock_session, chat_history[0])
        mock_generate_response.assert_any_call(mock_session, chat_history[1])

@patch("re.search")  # Patch the global `re.search` directly
def test_extract_title_from_response(mock_re_search):
    # Mock the regex search to simulate finding a title
    mock_match = MagicMock()
    mock_match.group.return_value = "Spaghetti Bolognese"
    mock_re_search.return_value = mock_match

    response = "Title: Spaghetti Bolognese"
    result = extract_title_from_response(response)

    # Assertions
    assert result == "Spaghetti Bolognese"
    mock_re_search.assert_called_once_with(r"Title:\s*(.*)", response, re.IGNORECASE)



def test_extract_title_from_response_no_match():
    response = "No title here"
    result = extract_title_from_response(response)

    assert result is None

import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/app')
from api.utils.llm_rag_utils import (
    generate_query_embedding,
    create_chat_session,
    generate_chat_response,
    rebuild_chat_session,
    ModelType
)

@pytest.fixture
def mock_embedding_model():
    with patch("api.utils.llm_rag_utils.embedding_model") as mock_embedding_model:
        mock_embedding_model.get_embeddings.return_value = [MagicMock(values=[0.1, 0.2, 0.3])]
        yield mock_embedding_model

@pytest.fixture
def mock_collection():
    with patch("api.utils.llm_rag_utils.collection") as mock_collection:
        mock_collection.query.return_value = {
            "documents": [[
                "Recipe 1: Ingredient list and directions",
                "Recipe 2: Ingredient list and directions",
                "Recipe 3: Ingredient list and directions"
            ]]
        }
        yield mock_collection

@pytest.fixture
def mock_chat_session():
    mock_session = MagicMock()
    yield mock_session


@patch("api.utils.llm_rag_utils.model_mapping", autospec=True) 
def test_create_chat_session(mock_model_mapping):
    # Set up the mock model and session
    mock_session = MagicMock(name="MockSession")  # Consistent return value
    mock_model = MagicMock(name="MockModel")
    mock_model.start_chat.return_value = mock_session
    mock_model_mapping.__getitem__.return_value = mock_model  # Ensure RAW model resolves to mock_model

    # Call the function
    session = create_chat_session(model=ModelType.RAW)

    # Assertions
    assert session is mock_session  # Ensure the session is the mocked session
    mock_model.start_chat.assert_called_once()  # Verify start_chat was called
    mock_model_mapping.__getitem__.assert_called_once_with(ModelType.RAW)  # Verify RAW was accessed


@patch("api.utils.llm_rag_utils.generate_query_embedding")
def test_generate_query_embedding(mock_generate_query_embedding, mock_embedding_model):
    query = "How to cook pasta"
    result = generate_query_embedding(query)

    assert result == [0.1, 0.2, 0.3]
    mock_embedding_model.get_embeddings.assert_called_once()

@patch("api.utils.llm_rag_utils.collection.query")
def test_generate_chat_response_success(mock_collection_query, mock_chat_session, mock_embedding_model):
    mock_collection_query.return_value = {
        "documents": [["Recipe 1", "Recipe 2", "Recipe 3"]]
    }

    mock_chat_session.send_message.return_value = MagicMock(text="Title: Delicious Pasta Recipe")

    message = {"content": "pasta, tomato sauce, cheese"}
    result = generate_chat_response(mock_chat_session, message)

    assert result == "Title: Delicious Pasta Recipe"
    mock_collection_query.assert_called_once()
    mock_chat_session.send_message.assert_called_once()

def test_generate_chat_response_no_content(mock_chat_session):
    message = {}

    with pytest.raises(HTTPException) as excinfo:
        generate_chat_response(mock_chat_session, message)

    assert excinfo.value.status_code == 500
    assert "Message must contain food list from food detection api" in str(excinfo.value.detail)

@patch("api.utils.llm_rag_utils.collection.query")
def test_generate_chat_response_exception(mock_collection_query, mock_chat_session, mock_embedding_model):
    mock_collection_query.side_effect = Exception("Database error")

    message = {"content": "pasta, tomato sauce, cheese"}

    with pytest.raises(HTTPException) as excinfo:
        generate_chat_response(mock_chat_session, message)

    assert excinfo.value.status_code == 500
    assert "Failed to generate response: Database error" in str(excinfo.value.detail)

@patch("api.utils.llm_rag_utils.create_chat_session")
def test_rebuild_chat_session(mock_create_chat_session, mock_chat_session):
    mock_create_chat_session.return_value = mock_chat_session

    chat_history = [
        {"role": "user", "content": "pasta"},
        {"role": "user", "content": "tomato sauce"}
    ]

    with patch("api.utils.llm_rag_utils.generate_chat_response") as mock_generate_response:
        mock_generate_response.side_effect = ["Response 1", "Response 2"]

        session = rebuild_chat_session(chat_history, model=ModelType.RAW)

        assert session == mock_chat_session
        mock_generate_response.assert_any_call(mock_chat_session, chat_history[0])
        mock_generate_response.assert_any_call(mock_chat_session, chat_history[1])

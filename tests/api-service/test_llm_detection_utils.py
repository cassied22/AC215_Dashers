import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
sys.path.append('/app')
from api.utils.llm_detection_utils import create_chat_session, generate_chat_response, encode_image, identify_food_gpt


@pytest.fixture
def mock_generative_model():
    # Mock the generative_model instance
    with patch("api.utils.llm_detection_utils.generative_model") as mock_generative_model:
        mock_session = MagicMock()
        mock_generative_model.start_chat.return_value = mock_session
        yield mock_generative_model


@pytest.fixture
def mock_requests_post():
    with patch("api.utils.llm_detection_utils.requests.post") as mock_post:
        yield mock_post

def test_create_chat_session(mock_generative_model):
    # Call the function
    session = create_chat_session()

    # Assertions
    assert session == mock_generative_model.start_chat.return_value  # Ensure the returned session is correct
    mock_generative_model.start_chat.assert_called_once()


@patch("api.utils.llm_detection_utils.generation_config", {"max_output_tokens": 3000})
def test_generate_chat_response(mock_generative_model):
    message = {"content": "What are the ingredients for pasta?"}
    mock_generative_model.send_message.return_value = MagicMock(text="Pasta Ingredients: ...")
    response = generate_chat_response(mock_generative_model, message)
    assert response == "Pasta Ingredients: ..."
    mock_generative_model.send_message.assert_called_once_with(
        "What are the ingredients for pasta?",
        generation_config={"max_output_tokens": 3000}
    )


@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_encode_image_success(mock_open):
    encoded_image = encode_image("test_image.jpg")
    assert encoded_image == "ZmFrZV9pbWFnZV9kYXRh"  # Base64 encoded "fake_image_data"
    mock_open.assert_called_once_with("test_image.jpg", "rb")


@patch("builtins.open", side_effect=FileNotFoundError)
def test_encode_image_file_not_found(mock_open):
    with pytest.raises(SystemExit) as exc_info:
        encode_image("non_existent_image.jpg")
    assert exc_info.value.code == 1
    mock_open.assert_called_once_with("non_existent_image.jpg", "rb")

@patch("api.utils.llm_detection_utils.encode_image", return_value="fake_base64_image")  # Mock encode_image
def test_identify_food_gpt_success(mock_encode_image, mock_requests_post):
    # Configure the mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "['apple', 'banana']"}}
        ]
    }
    mock_requests_post.return_value = mock_response

    # Call the function
    result = identify_food_gpt("test_image.jpg", "test_api_key")
    print("Result: ", result)

    # Assertions
    assert result == "['apple', 'banana']"
    mock_encode_image.assert_called_once_with("test_image.jpg")  # Verify encode_image is called
    mock_requests_post.assert_called_once_with(  # Verify requests.post is called with correct arguments
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test_api_key"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Identify the list of food items shown in this image. (Example Output1: ['pear','apple','salt', ...]). If no food is found in the image, output ['None']. (Example Output2: ['None'])"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64,fake_base64_image"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
    )

@patch("api.utils.llm_detection_utils.encode_image", return_value="ZmFrZV9pbWFnZV9kYXRh")
def test_identify_food_gpt_image_encoding(mock_encode_image, mock_requests_post):
    mock_requests_post.return_value = MagicMock(
        json=lambda: {
            "choices": [
                {"message": {"content": "['None']"}}
            ]
        }
    )
    result = identify_food_gpt("test_image.jpg", "test_api_key")
    assert result == "['None']"

    mock_encode_image.assert_called_once_with("test_image.jpg")
    mock_requests_post.assert_called_once()

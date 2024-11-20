import sys
sys.path.append('/app')

import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from gemini_object_detection import identify_food_gemini, main

@pytest.fixture
def setup_genai():
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.upload_file', return_value='mock_file') as mock_upload, \
         patch('google.generativeai.GenerativeModel') as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "['apple', 'banana']"
        mock_model_class.return_value = mock_model
        yield mock_configure, mock_upload, mock_model_class, mock_model

def test_identify_food_gemini(setup_genai, tmp_path):
    _, _, _, mock_model = setup_genai
    api_key = "fake_api_key"
    fake_image_path = tmp_path / "fake_image.jpg"
    fake_image_path.write_text('image data')

    result = identify_food_gemini(str(fake_image_path), api_key)

    assert result == "['apple', 'banana']"
    mock_model.generate_content.assert_called_once()

def test_main_usage_error():
    with patch('sys.argv', ['program']), \
         patch('sys.exit') as mock_exit:
        main()
        mock_exit.assert_called_once_with(1)

def test_main_success(setup_genai):
    fake_api_key = {"GOOGLE_API_KEY": "fake_api_key"}
    fake_path = '/fake/path'
    with patch('sys.argv', ['program', 'image.jpg']), \
         patch('os.getenv', return_value=fake_path), \
         patch('json.load', return_value=fake_api_key), \
         patch('builtins.open', mock_open(read_data=json.dumps(fake_api_key))), \
         patch('sys.exit') as mock_exit:
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_called_with("['apple', 'banana']")
            mock_exit.assert_not_called()

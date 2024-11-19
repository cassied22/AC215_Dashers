import sys
sys.path.append('/app')

import pytest
import json
import sys
import base64
from unittest.mock import patch, mock_open

from gpt_object_detection import encode_image, identify_food_gpt, main

def test_encode_image_success():
    # Use patch directly from unittest.mock
    with patch("builtins.open", mock_open(read_data=b"test image data")), \
         patch("os.path.exists", return_value=True):
        # Test encode_image
        result = encode_image("dummy_path.jpg")
        assert result == base64.b64encode(b"test image data").decode('utf-8')

def test_encode_image_failure():
    # Mock FileNotFoundError
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as e:
            encode_image("nonexistent.jpg")
        assert e.type == SystemExit
        assert e.value.code == 1

def test_identify_food_gpt():
    # Mock encode_image and requests.post
    with patch("gpt_object_detection.encode_image", return_value="encoded_string"), \
         patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": ["apple", "banana"]}}]
        }
        # Test identify_food_gpt
        result = identify_food_gpt("dummy_path.jpg", "dummy_api_key")
        assert result == ["apple", "banana"]

def test_main_success():
    # Mock sys.argv, os.getenv, and open file
    with patch("sys.argv", ["script_name", "image_path.jpg"]), \
         patch("os.getenv", return_value="api_key_path.json"), \
         patch("builtins.open", mock_open(read_data=json.dumps({"OPENAI_API_KEY": "test_key"}))), \
         patch("gpt_object_detection.identify_food_gpt", return_value=["apple", "banana"]), \
         patch("builtins.print") as mock_print:
        main()
        mock_print.assert_called_with(["apple", "banana"])

def test_main_failure_no_arg():
    # Test with missing command line argument
    with patch("sys.argv", ["script_name"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.type == SystemExit
        assert e.value.code == 1
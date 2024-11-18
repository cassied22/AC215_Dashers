import pytest
from unittest.mock import patch, MagicMock
import sys
import os

import sys
sys.path.append('/app')

# Import functions from gemini_object_detection.py
from gemini_object_detection import identify_food_gemini, main

# Test the identify_food_gemini function
def test_identify_food_gemini():
    with patch('google.generativeai.configure') as mock_configure:
        with patch('google.generativeai.upload_file') as mock_upload_file:
            with patch('google.generativeai.GenerativeModel') as mock_model:
                # Configure mocks
                mock_instance = mock_model.return_value
                mock_instance.generate_content.return_value.text = "Pizza, Salad"

                # Call the function
                result = identify_food_gemini("path/to/image.jpg", "dummy_api_key")

                # Assertions to check correct behavior
                mock_configure.assert_called_once_with(api_key="dummy_api_key")
                mock_upload_file.assert_called_once_with("path/to/image.jpg")
                mock_model.assert_called_once_with("gemini-1.5-flash")
                assert result == "Pizza, Salad"

# Test the main function
def test_main_valid_args():
    with patch('sys.argv', ["script_name", "path/to/image.jpg"]), \
         patch('os.getenv') as mock_getenv, \
         patch('builtins.print') as mock_print, \
         patch('gemini_object_detection.identify_food_gemini') as mock_identify_food_gemini:
        mock_getenv.return_value = "dummy_api_key"
        mock_identify_food_gemini.return_value = "Detected: Pizza"

        # Call main
        main()

        # Assertions
        mock_getenv.assert_called_once_with("GEMINI_API_KEY")
        mock_identify_food_gemini.assert_called_once_with("path/to/image.jpg", "dummy_api_key")
        mock_print.assert_called_once_with("Detected: Pizza")

def test_main_invalid_args():
    with patch('sys.argv', ["script_name"]), \
         patch('sys.exit') as mock_exit, \
         patch('builtins.print') as mock_print:
        main()

        # Assertions
        mock_print.assert_called_once_with("Usage: python food_item_identifier.py <image_path>")
        mock_exit.assert_called_once_with(1)

        # Ensure no further code is executed after sys.exit call
        assert mock_exit.called


# Run tests
if __name__ == "__main__":
    pytest.main()

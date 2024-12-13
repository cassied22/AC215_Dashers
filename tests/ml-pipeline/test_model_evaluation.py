import pandas as pd
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/app')
from model_evaluation import ( 
    extract_ingredients_corrected,
    calculate_ingredient_match,
    comupute_valid_pair_percentages,
    get_valid_percentages,
    evaluate
)

# Test extract_ingredients_corrected
def test_extract_ingredients_corrected():
    question = "Create a dish using these ingredients: [\"tomato\", \"onion\", \"basil\"]"
    expected_output = ["tomato", "onion", "basil"]
    assert extract_ingredients_corrected(question) == expected_output

    question_no_match = "Create a dish without mentioning ingredients."
    assert extract_ingredients_corrected(question_no_match) == []

# Test calculate_ingredient_match
def test_calculate_ingredient_match():
    question = "Create a dish using these ingredients: [\"tomato\", \"onion\", \"basil\"]"
    answer = "This recipe uses tomato and onion in a delicious sauce."
    assert calculate_ingredient_match(question, answer) == 66.66666666666666

    answer_no_match = "This recipe uses garlic and parsley."
    assert calculate_ingredient_match(question, answer_no_match) == 0

# Test comupute_valid_pair_percentages
def test_comupute_valid_pair_percentages():
    data = pd.DataFrame({
        'match_percentage': [30, 10, 50, 20]
    })
    assert comupute_valid_pair_percentages(data, threshold=25) == 50.0

# Test get_valid_percentages
def test_get_valid_percentages():
    data = pd.DataFrame({
        'question': [
            "Create a dish using these ingredients: [\"tomato\", \"onion\", \"basil\"]",
            "Create a dish using these ingredients: [\"garlic\", \"parsley\"]"
        ],
        'answer': [
            "This recipe uses tomato and onion in a delicious sauce.",
            "This recipe uses garlic and parsley."
        ]
    })
    valid_percentage = get_valid_percentages(data)
    assert valid_percentage == 100.0

# Mock dependencies and test evaluate
def test_evaluate():
    mock_data = pd.DataFrame({
        'question': [
            "Create a dish using these ingredients: [\"tomato\", \"onion\"]"
        ]
    })

    mock_blob = MagicMock()
    mock_blob.download_to_filename = MagicMock()

    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket

    mock_generative_model = MagicMock()
    mock_generative_model.generate_content.return_value.text = "This recipe uses tomato and onion."

    with patch("model_evaluation.storage.Client", return_value=mock_storage_client):
        with patch("model_evaluation.pd.read_csv", return_value=mock_data):
            with patch("model_evaluation.GenerativeModel", return_value=mock_generative_model):
                valid_percentage = evaluate()
                assert valid_percentage == 100.0

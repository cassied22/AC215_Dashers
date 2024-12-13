import pandas as pd
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/app')
from data_process import clean, prepare, upload, main 

@patch("data_process.storage.Client")
@patch("data_process.pd.read_csv")
@patch("data_process.pd.DataFrame.to_csv")
def test_clean(mock_to_csv, mock_read_csv, mock_storage_client):
    # Mock GCP storage
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.return_value.get_bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Mock reading raw CSV
    mock_read_csv.return_value = pd.DataFrame({
        'title': ["Recipe 1", "Recipe 2"],
        'NER': ["[ingredient1, ingredient2]", "[ingredient3, ingredient4]"],
        'directions': ["Step 1, Step 2", "Step 1, Step 2"]
    })

    # Run the function under test
    clean()

    # Verify that the raw data CSV was downloaded
    mock_bucket.blob.assert_any_call("raw_data/recipe_raw.csv")
    mock_blob.download_to_filename.assert_called_once_with(os.path.join("raw_data", "recipe_raw.csv"))

    # Verify saving cleaned data and QA pairs
    assert mock_to_csv.call_count == 3  # recipe_cleaned.csv, preparation_qa.csv, test_qa.csv

    # Verify upload of cleaned data, training data, and test data
    expected_upload_calls = [
        ("clean_data/recipe_cleaned.csv", os.path.join("clean_data", "recipe_cleaned.csv")),
        ("training_data/preparation_qa.csv", os.path.join("training_data", "preparation_qa.csv")),
        ("testing_data/test_qa.csv", os.path.join("testing_data", "test_qa.csv"))
    ]
    actual_upload_calls = [
        call.args for call in mock_blob.upload_from_filename.call_args_list
    ]
    for expected, actual in zip(expected_upload_calls, actual_upload_calls):
        assert expected[1] == actual[0]


@patch("data_process.storage.Client")
@patch("data_process.pd.read_csv")
@patch("data_process.train_test_split")
@patch("data_process.pd.DataFrame.to_json")
def test_prepare(mock_to_json, mock_train_test_split, mock_read_csv, mock_storage_client):
    # Mock GCP storage
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Mock reading preparation QA CSV
    mock_read_csv.return_value = pd.DataFrame({
        'question': ["Can you provide a recipe?", "What can I make with these ingredients?"],
        'answer': ["Here is a recipe for you!", "Try making a simple pasta dish."]
    })

    # Mock train-test split
    mock_train_test_split.return_value = (
        pd.DataFrame({
            'text': ["human: Can you provide a recipe?\nbot: Here is a recipe for you!"],
            'contents': [
                [
                    {"role": "user", "parts": [{"text": "Can you provide a recipe?"}]},
                    {"role": "model", "parts": [{"text": "Here is a recipe for you!"}]}
                ]
            ]
        }),
        pd.DataFrame({
            'text': ["human: What can I make with these ingredients?\nbot: Try making a simple pasta dish."],
            'contents': [
                [
                    {"role": "user", "parts": [{"text": "What can I make with these ingredients?"}]},
                    {"role": "model", "parts": [{"text": "Try making a simple pasta dish."}]}
                ]
            ]
        })
    )

    # Mock the to_json return value
    mock_to_json.side_effect = lambda *args, **kwargs: '{"mocked_key": "mocked_value"}'

    # Run the function under test
    prepare()

    # Check that the preparation QA CSV was read
    mock_read_csv.assert_called_once()
    
    # Ensure train-test split was called
    mock_train_test_split.assert_called_once()

    # Ensure to_json was called twice (once for train.jsonl and once for test.jsonl)
    assert mock_to_json.call_count == 2

    # Verify blob.download_to_filename was called for the input CSV
    mock_blob.download_to_filename.assert_called_once_with(os.path.join("data", "preparation_qa.csv"))


@patch("data_process.storage.Client")
@patch("glob.glob")
def test_upload(mock_glob, mock_storage_client):
    # Mock GCP storage
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.return_value.bucket.return_value = mock_bucket

    # Assign separate blobs for each unique file
    mock_bucket.blob.side_effect = lambda name: MagicMock(name=f"Blob for {name}")

    # Mock finding files
    mock_glob.return_value = ["data/file1.jsonl", "data/file2.csv"]

    # Run the function under test
    upload()

    # Print actual call arguments
    print(mock_bucket.blob.call_args_list)

    # Verify that blob was created for each file
    assert mock_bucket.blob.call_count == len(mock_glob.return_value)


@patch("data_process.clean")
@patch("data_process.prepare")
def test_main(mock_prepare, mock_clean):
    args = MagicMock()
    args.clean = True
    args.prepare = True

    main(args)

    # Ensure the appropriate functions were called
    mock_clean.assert_called_once()
    mock_prepare.assert_called_once()

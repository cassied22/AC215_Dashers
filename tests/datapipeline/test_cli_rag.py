import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os
import argparse
from vertexai.generative_models import (
    HarmBlockThreshold,
    HarmCategory,
)

import sys
sys.path.append('/app')
from cli_rag import generate_query_embedding, generate_text_embeddings, embed, load, query, chat, download, test, main

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Mocked test data
@pytest.fixture
def mock_dataframe():
    return pd.DataFrame({
        "NER": ['["chicken", "broccoli", "cheese"]'],
        "title": ["Test Recipe"],
        "ingredients": ['["chicken", "broccoli", "cheese"]'],
        "directions": ['["Step 1", "Step 2"]'],
        "link": ["http://example.com"]
    })

# Test generate_query_embedding
@patch("cli_rag.embedding_model.get_embeddings")
def test_generate_query_embedding(mock_get_embeddings):
    mock_get_embeddings.return_value = [MagicMock(values=np.random.rand(256))]
    query = "chicken broccoli"
    embedding = generate_query_embedding(query)
    assert len(embedding) == 256  # Check that the embedding has the expected dimension
    mock_get_embeddings.assert_called_once()

# Test generate_text_embeddings
@patch("cli_rag.embedding_model.get_embeddings")
def test_generate_text_embeddings(mock_get_embeddings):
    mock_get_embeddings.return_value = [
        MagicMock(values=np.random.rand(256)) for _ in range(2)
    ]
    text_list = ["text 1", "text 2"]
    embeddings = generate_text_embeddings(text_list)
    assert len(embeddings) == len(text_list)
    assert len(embeddings[0]) == 256
    mock_get_embeddings.assert_called_once()

# Test embed function
@patch("cli_rag.generate_text_embeddings")
@patch("cli_rag.subprocess")
@patch("builtins.open", new_callable=MagicMock)
@patch("os.makedirs")
def test_embed(mock_makedirs, mock_open, mock_subprocess, mock_generate_embeddings, mock_dataframe):
    mock_generate_embeddings.return_value = [np.random.rand(256)]
    mock_subprocess.run.return_value = MagicMock(returncode=0)

    result_df = embed(mock_dataframe)

    assert "NER_embeddings" in result_df.columns
    assert len(result_df["NER_embeddings"]) == len(mock_dataframe)

    mock_makedirs.assert_called_once_with("outputs", exist_ok=True)
    mock_open.assert_called_once_with("outputs/recipe_embeddings.jsonl", "w")
    mock_subprocess.run.assert_called_once()

# Test load function
@patch("cli_rag.chromadb.HttpClient")
@patch("glob.glob")
@patch("pandas.read_json")
def test_load(mock_read_json, mock_glob, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.return_value = mock_client
    mock_glob.return_value = ["outputs/recipe_embeddings.jsonl"]
    mock_read_json.return_value = pd.DataFrame({
        "id": ["0"],
        "title": ["Test Recipe"],
        "ingredients": ["[\"chicken\", \"broccoli\", \"cheese\"]"],
        "directions": ["[\"Step 1\", \"Step 2\"]"],
        "link": ["http://example.com"],
        "NER_embeddings": [np.random.rand(256)]
    })
    
    load()

    mock_client.delete_collection.assert_called_once_with(name="recipe-small-collection")
    mock_client.create_collection.assert_called_once_with(
        name="recipe-small-collection", metadata={"hnsw:space": "cosine"}
    )
    mock_read_json.assert_called_once_with("outputs/recipe_embeddings.jsonl", lines=True)
    mock_glob.assert_called_once_with("outputs/recipe_embeddings.jsonl")

# Test query function
@patch("cli_rag.chromadb.HttpClient")
@patch("cli_rag.generate_query_embedding")
def test_query(mock_generate_embedding, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.return_value = mock_client
    mock_generate_embedding.return_value = np.random.rand(256)

    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["Recipe 1", "Recipe 2"]],
        "metadata": [{"link": "http://example.com"}],
    }
    mock_client.get_collection.return_value = mock_collection

    results = query("chicken broccoli cheese")

    mock_generate_embedding.assert_called_once_with("chicken broccoli cheese")
    mock_client.get_collection.assert_called_once_with(name="recipe-small-collection")
    mock_collection.query.assert_called_once_with(query_embeddings=[mock_generate_embedding.return_value], n_results=10)
    
    assert len(results["documents"][0]) == 2
    assert results["documents"][0][0] == "Recipe 1"
    assert results["documents"][0][1] == "Recipe 2"
    assert results["metadata"][0]["link"] == "http://example.com"

# Test chat function
@patch("builtins.input", side_effect=["[chicken, broccoli, cheese]", "End the conversation", KeyboardInterrupt])  # Mock user input
@patch("cli_rag.query")
@patch("cli_rag.raw_model.generate_content")
def test_chat(mock_generate_content, mock_query, mock_input):
    mock_query.return_value = {
        "documents": [["Recipe 1", "Recipe 2"]],
        "metadata": [{"link": "http://example.com"}],
    }
    mock_generate_content.return_value = MagicMock(text="Generated Recipe")

    try:
        chat(generative_model="raw")
    except KeyboardInterrupt:
        pass

    mock_query.assert_called_once_with("[chicken, broccoli, cheese]")
    mock_generate_content.assert_called()

# Test download function
@patch("os.makedirs")
@patch("os.path.exists", side_effect=lambda x: x == "outputs/recipe_embeddings.jsonl")
@patch("subprocess.run")
def test_download(mock_subprocess_run, mock_path_exists, mock_makedirs):
    download()

    # Assert makedirs was called without exist_ok=True (matches the function implementation)
    mock_makedirs.assert_called_once_with("outputs")

    # Ensure no subprocess call happens if the file exists
    mock_subprocess_run.assert_not_called()

    # Simulate the case where the file does not exist
    mock_path_exists.side_effect = lambda x: False
    download()

    # Assert the subprocess is called with the correct arguments
    mock_subprocess_run.assert_called_once_with(
        [
            "gcloud",
            "storage",
            "cp",
            "-r",
            f"gs://{GCS_BUCKET_NAME}/recipe_embeddings.jsonl",
            "outputs/recipe_embeddings.jsonl",
        ],
        check=True,
    )



# Test test function
@patch("cli_rag.finetuned_model.generate_content")
def test_test(mock_generate_content):
    mock_generate_content.return_value = MagicMock(text="Generated Recipe")

    global generation_config, safety_settings
    generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 0.25,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
    }
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
    }

    test()
    expected_prompt = '''
Sample recipe:
Title: Jewell Ball'S Chicken
Ingredients: ["1 small jar chipped beef, cut up", "4 boned chicken breasts", "1 can cream of mushroom soup", "1 carton sour cream"]
Directions: ["Place chipped beef on bottom of baking dish.", "Place chicken on top of beef.", "Mix soup and cream together; pour over chicken. Bake, uncovered, at 275\u00b0 for 3 hours."]

Input ingredients the user has: [chicken, broccoli, cheese], create a recipe'''
    mock_generate_content.assert_called_once_with(
        [expected_prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )


# Test main function argument parsing
def test_main():
    mock_df = pd.DataFrame({
        "id": [1, 2],
        "title": ["Recipe 1", "Recipe 2"],
        "ingredients": [["chicken", "broccoli"], ["cheese", "tomato"]],
        "directions": [["Step 1", "Step 2"], ["Step 1", "Step 2"]],
        "NER": ['["chicken", "broccoli"]', '["cheese", "tomato"]'],
    })

    with patch("pandas.read_feather", return_value=mock_df) as mock_read_feather, \
         patch("subprocess.run") as mock_subprocess_run:

        # Create mock args for the embed functionality
        mock_args = argparse.Namespace(embed=True, load=False, query=False, chat=None, download=False, test=False)

        # Call main with the mocked arguments
        main(mock_args)

        # Ensure pandas.read_feather was called to read the file
        mock_read_feather.assert_called_once_with("input-datasets/recipe_cookbook.feather")

        # Ensure subprocess.run was invoked to simulate the GCS upload
        mock_subprocess_run.assert_called_once_with(
            ["gcloud", "storage", "cp", "outputs/recipe_embeddings.jsonl", "gs://dasher-recipe/recipe_embeddings.jsonl"],
            check=True
        )

def test_main_load():
    with patch("cli_rag.load") as mock_load:
        mock_args = argparse.Namespace(embed=False, load=True, query=False, chat=None, download=False, test=False)
        main(mock_args)
        # Ensure load function was called
        mock_load.assert_called_once()

def test_main_query():
    with patch("cli_rag.query") as mock_query:
        mock_args = argparse.Namespace(embed=False, load=False, query=True, chat=None, download=False, test=False)
        main(mock_args)
        # Ensure query function was called
        mock_query.assert_called_once()

def test_main_chat():
    with patch("cli_rag.chat") as mock_chat:
        mock_args = argparse.Namespace(embed=False, load=False, query=False, chat=["raw"], download=False, test=False)
        main(mock_args)
        # Ensure chat function was called with correct arguments
        mock_chat.assert_called_once_with(generative_model="raw")

def test_main_download():
    with patch("cli_rag.download") as mock_download:
        mock_args = argparse.Namespace(embed=False, load=False, query=False, chat=None, download=True, test=False)
        main(mock_args)
        # Ensure download function was called
        mock_download.assert_called_once()

def test_main_test():
    with patch("cli_rag.test") as mock_test:
        mock_args = argparse.Namespace(embed=False, load=False, query=False, chat=None, download=False, test=True)
        main(mock_args)
        # Ensure test function was called
        mock_test.assert_called_once()

def test_main_no_args():
    with patch("builtins.print") as mock_print:
        mock_args = argparse.Namespace(embed=False, load=False, query=False, chat=None, download=False, test=False)
        main(mock_args)
        mock_print.assert_any_call("No valid operation selected.")
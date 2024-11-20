import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os

import sys
sys.path.append('/app')
# Import functions from cli_rag.py
from cli_rag import generate_query_embedding, generate_text_embeddings, embed, load, query

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
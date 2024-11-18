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
@patch("os.makedirs")
@patch("builtins.open", new_callable=MagicMock)
def test_embed(mock_open, mock_makedirs, mock_generate_embeddings, mock_dataframe):
    mock_generate_embeddings.return_value = [np.random.rand(256) for _ in range(len(mock_dataframe))]
    output_df = embed(mock_dataframe)
    
    # Check that embeddings were added to the dataframe
    assert "NER_embeddings" in output_df.columns
    assert len(output_df["NER_embeddings"]) == len(mock_dataframe)
    mock_makedirs.assert_called_once_with("outputs", exist_ok=True)
    mock_open.assert_called_once()

# Test load function
@patch("cli_rag.chromadb.HttpClient")
@patch("glob.glob")
@patch("pandas.read_json")
@patch("subprocess.run")
def test_load(mock_subprocess, mock_read_json, mock_glob, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.return_value = mock_client
    mock_glob.return_value = ["test.jsonl"]
    mock_read_json.return_value = pd.DataFrame({
        "title": ["Test Recipe"],
        "ingredients": ["[\"chicken\", \"broccoli\", \"cheese\"]"],
        "directions": ["[\"Step 1\", \"Step 2\"]"],
        "link": ["http://example.com"],
        "NER_embeddings": [np.random.rand(256)]
    })
    
    load()

    # Check ChromaDB operations
    mock_client.create_collection.assert_called_once()
    mock_client.get_collection.assert_not_called()
    mock_subprocess.assert_called_once()

# Test query function
@patch("cli_rag.chromadb.HttpClient")
@patch("cli_rag.generate_query_embedding")
@patch("os.listdir")
@patch("subprocess.run")
def test_query(mock_subprocess, mock_listdir, mock_generate_embedding, mock_chromadb):
    mock_client = MagicMock()
    mock_chromadb.return_value = mock_client
    mock_listdir.return_value = ["chromadb"]
    mock_generate_embedding.return_value = np.random.rand(256)

    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["Recipe 1", "Recipe 2"]],
        "metadata": [{"link": "http://example.com"}],
    }
    mock_client.get_collection.return_value = mock_collection

    results = query("chicken broccoli cheese")

    # Verify results
    assert len(results["documents"]) > 0
    assert "documents" in results
    mock_generate_embedding.assert_called_once()
    mock_collection.query.assert_called_once()


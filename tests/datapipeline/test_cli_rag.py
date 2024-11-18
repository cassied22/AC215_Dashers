import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os
from cli_rag import embed, load, query
from cli_rag import generate_query_embedding, generate_text_embeddings


class TestCliRag(unittest.TestCase):
    def setUp(self):
        # Set environment variables for testing
        os.environ['GCS_BUCKET_NAME'] = 'test-bucket'
        
        # Create test dataframe
        self.test_df = pd.DataFrame({
            'NER': [['chicken', 'broccoli', 'cheese']],
            'title': ['Test Recipe'],
            'ingredients': ['["chicken", "broccoli", "cheese"]'],
            'directions': ['["Step 1", "Step 2"]'],
            'link': ['http://example.com']
        })

    @patch("cli_rag.generate_text_embeddings")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("subprocess.run")
    def test_embed(self, mock_run, mock_open, mock_makedirs, mock_generate_embeddings):
        # Setup
        mock_generate_embeddings.return_value = [np.random.rand(256) for _ in range(len(self.test_df))]
        
        # Execute
        output_df = embed(self.test_df)
        
        # Assert
        mock_makedirs.assert_called_once_with('outputs', exist_ok=True)
        mock_open.assert_called_once()
        mock_run.assert_called_once_with(
            ['gcloud', 'storage', 'cp', 'outputs/recipe_embeddings.jsonl', 'gs://test-bucket/recipe_embeddings.jsonl'],
            check=True
        )
        self.assertIn('NER_embeddings', output_df.columns)

    @patch("cli_rag.chromadb.HttpClient")
    @patch("glob.glob")
    @patch("pandas.read_json")
    def test_load(self, mock_read_json, mock_glob, mock_chromadb):
        # Setup
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.return_value = mock_client
        mock_client.create_collection.return_value = mock_collection
        mock_glob.return_value = ["test.jsonl"]
        
        test_df = pd.DataFrame({
            "title": ["Test Recipe"],
            "ingredients": ["[\"chicken\", \"broccoli\", \"cheese\"]"],
            "directions": ["[\"Step 1\", \"Step 2\"]"],
            "link": ["http://example.com"],
            "NER_embeddings": [np.random.rand(256).tolist()]
        })
        test_df['id'] = test_df.index.astype(str)
        mock_read_json.return_value = test_df

        # Execute
        load()

        # Assert
        mock_client.delete_collection.assert_called_once_with(name="recipe-small-collection")
        mock_client.create_collection.assert_called_once_with(
            name="recipe-small-collection",
            metadata={"hnsw:space": "cosine"}
        )
        mock_collection.add.assert_called_once()

    def test_generate_query_embedding(mock_get_embeddings):
        mock_get_embeddings.return_value = [MagicMock(values=np.random.rand(256))]
        query = "chicken broccoli"
        embedding = generate_query_embedding(query)
        assert len(embedding) == 256  # Check that the embedding has the expected dimension
        mock_get_embeddings.assert_called_once()


    def test_generate_text_embeddings(mock_get_embeddings):
        mock_get_embeddings.return_value = [
            MagicMock(values=np.random.rand(256)) for _ in range(2)
        ]
        text_list = ["text 1", "text 2"]
        embeddings = generate_text_embeddings(text_list)
        assert len(embeddings) == len(text_list)
        assert len(embeddings[0]) == 256
        mock_get_embeddings.assert_called_once()


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


if __name__ == '__main__':
    unittest.main()
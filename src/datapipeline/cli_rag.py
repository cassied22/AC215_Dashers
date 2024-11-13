"""CLI for RAG pipeline."""
import json
import os

import click
import pandas as pd
import vertexai

from google.cloud import storage
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
from vertexai.language_models import TextGenerationModel


def download_data(bucket_name, source_blob_name, destination_file_name):
    """Downloads data from GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def process_results(results):
    """Process query results."""
    if not results or "documents" not in results:
        return None

    doc_count = len(results.get("documents", [])[0]) if results.get("documents") else 0
    print(f"\nCount of queried recipes: {doc_count}")

    retrieved_recipes = []
    if doc_count > 0:
        print("\nRetrieved recipes:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"\nRecipe {i+1}:")
            recipe_dict = json.loads(doc)
            retrieved_recipes.append(recipe_dict)
            print(json.dumps(recipe_dict, indent=2))

    return retrieved_recipes


def process_query(query, vector_db=None):
    """Process a query and return results."""
    try:
        if vector_db is None:
            # Initialize vector database if not provided
            embeddings = OpenAIEmbeddings()
            vector_db = Chroma(
                persist_directory="outputs/chroma_db", embedding_function=embeddings
            )

        # Search for similar documents
        results = vector_db.similarity_search(query, k=5)
        processed_results = []

        for doc in results:
            recipe = json.loads(doc.page_content)
            processed_results.append(
                {
                    "title": recipe.get("title", "Untitled Recipe"),
                    "ingredients": recipe.get("ingredients", []),
                    "directions": recipe.get("directions", []),
                }
            )

        return processed_results

    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return None


@click.group()
def cli():
    """CLI for RAG pipeline."""
    pass


@cli.command()
@click.argument("query", required=True)
def search(query):
    """Search recipes."""
    results = process_query(query)
    if results:
        click.echo("Found recipes:")
        for i, recipe in enumerate(results, 1):
            click.echo(f"\nRecipe {i}:")
            click.echo(f"Title: {recipe['title']}")
            click.echo("Ingredients:")
            for ing in recipe["ingredients"]:
                click.echo(f"- {ing}")
            click.echo("Directions:")
            for j, step in enumerate(recipe["directions"], 1):
                click.echo(f"{j}. {step}")
    else:
        click.echo("No results found.")


if __name__ == "__main__":
    cli()

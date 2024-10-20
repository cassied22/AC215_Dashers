import os
import argparse
import numpy as np
import pandas as pd
import glob
import chromadb

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig,
    Content,
    Part,
    ToolConfig,
)

# # Langchain
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_experimental.text_splitter import SemanticChunker


# ------- optional: params versioning -------------------
# import yaml

# with open('params.yaml', 'r') as file:
#     params = yaml.safe_load(file)

# EMBEDDING_MODEL = params['embedding']['model']
# EMBEDDING_DIMENSION = params['embedding']['dimension']
# GENERATIVE_MODEL = params['generative_model']['name']
# INPUT_FOLDER = params['input_folder']
# OUTPUT_FOLDER = params['output_folder']
# CHROMADB_HOST = params['chromadb']['host']
# CHROMADB_PORT = params['chromadb']['port']
# ----------------------------------------------

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-001"
INPUT_FOLDER = "input-datasets"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = "recipe-rag-chromadb"
CHROMADB_PORT = 8000
# MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/9072590509779714048"
# MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/7256513960042561536"
MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/8362147668562018304"
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 0.25,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}
# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in food recipes knowledge. Your responses are based solely on the information provided in the sample recipes given to you. Do not use any external knowledge or make assumptions beyond what is explicitly stated in these recipes.

When answering a query:
1. Carefully read all the sample recipes provided.
2. Identify the most relevant information from these recipes to create a personalized recipe for the user's ingredients. 
3. You can use the ingredients, directions, and any other relevant details from the sample recipes to craft your response. 
4. Use user provided ingredients as much as possible, but you can also suggest additional ingredients if necessary to create a complete recipe. 
5. Formulate your response using only the information found in the given recipes.
6. If the provided recipes do not contain sufficient information to answer the query, state that you don't have enough information to provide a complete answer.
7. Always maintain a friendly and knowledgeable tone, befitting an expert cook who helps the user to cook.
8. If there are contradictions in the provided recipes, mention this in your response and explain the different viewpoints presented.
9. At the end of the response, ask the user if they need any more help or additional information. Otherwise, wish them a pleasant cooking experience.

Remember:
- You are an expert in making food recipes, but your knowledge is limited to the information in the provided chunks.
- Do not invent information or draw from knowledge outside of the given recipes.
- Identify any additional ingredients in your response other than the user provided ones and highlight these ingredients in your response to notify the user. 
- If asked about topics unrelated to food or recipes, politely redirect the conversation back to food or recipe-related subjects.
- Be concise in your responses while ensuring you cover all relevant information from the recipes.

Your goal is to provide accurate, helpful information about food recipe based solely on the content of the text chunks you receive with each query.
"""
# generative_model = GenerativeModel(
#     GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION]
# )
raw_model = GenerativeModel(
    GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION])

finetuned_model = GenerativeModel(
    MODEL_ENDPOINT, system_instruction=[SYSTEM_INSTRUCTION]
)

def generate_query_embedding(query):
    """
	Function to generate an embedding for a query input

	Args:
		query: str, query input to embed

	Returns:
		embeddings[0].values: np.array, embedding for the query input
	"""
    query_embedding_inputs = [
        TextEmbeddingInput(task_type="RETRIEVAL_DOCUMENT", text=query)
    ]
    kwargs = (
        dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
    )
    embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
    return embeddings[0].values


def generate_text_embeddings(text_list, batch_size=250):
    """
	Function to generate embeddings for a list of text inputs

	Args:
		text_list: list, list of text inputs to embed
		batch_size: int, number of items to embed at a time

	Returns:
		all_embeddings: list, list of embedding arrays for the text inputs
	"""
    # Max batch size is 250 for Vertex AI
    all_embeddings = []
    for i in range(0, len(text_list), batch_size):
        batch = text_list[i : i + batch_size]
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in batch]
        kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
        embeddings = embedding_model.get_embeddings(inputs, **kwargs)
        all_embeddings.extend([embedding.values for embedding in embeddings])

    return all_embeddings


def embed(df):
    """
    Function to embed the NER column and add the embeddings back to the dataframe
    
    Args:
		df: pd.DataFrame, dataframe with NER column to embed
    
	Returns:
		df: pd.DataFrame, dataframe with NER embeddings added
    """
    # Concatenate the list of NER entities in each row into a single string
    df["NER"] = df["NER"].apply(lambda x: eval(x))
    concatenated_column = [", ".join(entities) for entities in df["NER"]]

    ner_embeddings = generate_text_embeddings(concatenated_column, batch_size=100)
    df["NER_embeddings"] = ner_embeddings

    # Save
    print("Shape:", df.shape)
    print(df.head())

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    jsonl_filename = os.path.join(OUTPUT_FOLDER, f"recipe_small.jsonl")
    with open(jsonl_filename, "w") as json_file:
        json_file.write(df.to_json(orient="records", lines=True))

    return df


def load(batch_size=500):
    """
    Function to load the embeddings into ChromaDB
    
    Args:
		batch_size: int, number of items to insert at a time
    """
    # Connect to chroma DB
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

    # Get a collection object from an existing collection, by name. If it doesn't exist, create it.
    collection_name = "recipe-small-collection"
    print("Creating collection:", collection_name)
    try:
        # Clear out any existing items in the collection
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        print(f"Collection '{collection_name}' did not exist. Creating new.")

    collection = client.create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )
    print(f"Created new empty collection '{collection_name}'")
    print("Collection:", collection)
    # Get the list of embedding files
    jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"recipe_small.jsonl"))
    print("Number of files to process:", len(jsonl_files))

    # Process
    for jsonl_file in jsonl_files:
        print("Processing file:", jsonl_file)
        df = pd.read_json(jsonl_file, lines=True)
        print("Shape:", df.shape)
        df["id"] = df.index.astype(str)

        total_inserted = 0
        for i in range(0, df.shape[0], batch_size):
            # Create a copy of the batch and reset the index
            batch = df.iloc[i : i + batch_size].copy().reset_index(drop=True)
            title = batch["title"].tolist()
            ingredients = batch["ingredients"].tolist()
            directions = batch["directions"].tolist()
            documents = [
                f"Title: {t}\nIngredients: {i}\nDirections: {d}"
                for t, i, d in zip(title, ingredients, directions)
            ]

            collection.add(
                ids=batch["id"].tolist(),
                documents=documents,
                metadatas=batch["link"].apply(lambda x: {"link": x}).tolist(),
                embeddings=batch["NER_embeddings"].tolist(),
            )
            total_inserted += len(batch)
            print(f"Inserted {total_inserted} items...")

        print(
            f"Finished inserting {total_inserted} items into collection '{collection.name}'"
        )


def query(query_input):
    """
    Function to query the most relevant recipe samples according to the user input
    
    Args:
		query_input: str, food list from object detection, currently using user input ingredients instead
        
    Returns:
		results: dict, retrieved relevant recipe samples from ChromaDB
    """
    # Connect to chroma DB
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection_name = "recipe-small-collection"
    collection = client.get_collection(name=collection_name)

    query_embedding = generate_query_embedding(query_input)
    print("Embedding values:", query_embedding)

    results = collection.query(query_embeddings=[query_embedding], n_results=10)

    return results


def chat(generative_model = "raw"):
    """
    Function to chat with the model to generate a recipe based on user input
    """
    # Choose the generative model to use
    if generative_model == "finetuned":
        generative_model = finetuned_model
    else:
        generative_model = raw_model

    default_query_input = "[broccoli, chicken, cheese]"
    user_input = input(
        "Enter your ingredients (or press Enter to use the default [broccoli, chicken, cheese]): "
    )
    query_input = user_input if user_input.strip() else default_query_input
    results = query(query_input)
    print(f"\nCount of queried recipes: {len(results["documents"][0])}")

    # Generate initial response based on retrieved recipes
    conversation_history = [f"User input ingredients: {query_input}"]
    INPUT_PROMPT = f"""
Input ingredients the user has: {query_input}
{"\n".join([f'\nSample recipe:\n{recipe}' for recipe in results["documents"][0]])}
"""
    print("\n\nINPUT_PROMPT: ", INPUT_PROMPT)
    conversation_history.append(f"Sample recipes provided:\n{INPUT_PROMPT}")

    response = generative_model.generate_content(
        [INPUT_PROMPT],
        generation_config=generation_config,
        stream=False,
    )
    generated_text = response.text
    conversation_history.append(f"LLM response:\n{generated_text}")
    print("LLM Response:\n", generated_text)

    # Continue the conversation until the user ends it
    try:
        while True:
            feedback = input(
                "\nMessage our Recipe Bot here (or Press "
                "Ctrl+C"
                " to end the conversation): "
            )
            conversation_history.append(f"User feedback: {feedback}")
            # Regenerate response from LLM based on conversation history
            INPUT_PROMPT = f"""
Current conversation history:
{"\n".join(conversation_history)}
User requested changes: {feedback}.
Generate a new recipe based on these changes.
"""
            response = generative_model.generate_content(
                [INPUT_PROMPT], generation_config=generation_config, stream=False
            )
            generated_text = response.text
            conversation_history.append(f"LLM response:\n{generated_text}")
            print("LLM response:\n", generated_text)
    except KeyboardInterrupt:
        print("Conversation ended. Enjoy your meal!")


def main(args=None):
    print("CLI Arguments:", args)

    if args.embed:
        df = pd.read_feather(os.path.join(INPUT_FOLDER, "recipe_cookbook.feather"))
        # Trim the dataframe to the first 100 rows for testing
        df = df.loc[1:100, :]
        df = embed(df)
        print("Embedding complete")
    elif args.load:
        load()
        print("Load complete")
    elif args.query:
        query()
        print("Query complete")
    elif args.chat:
        # Use the first argument after --chat as the model type (finetuned or raw)
        model_type = args.chat[0] if args.chat else "raw"
        chat(generative_model=model_type)
        print("Chat complete")
    else:
        print("No valid operation selected.")
        parser.print_help()


if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description="CLI for recipe RAG")

    parser.add_argument("--embed", action="store_true", help="Generate embeddings")
    parser.add_argument("--load", action="store_true", help="Load embeddings into ChromaDB")
    parser.add_argument("--query", action="store_true", help="Query ChromaDB")
    parser.add_argument(
        "--chat", nargs="*", help="Chat with the model, specify 'finetuned' or 'raw' model (default is raw)"
    )
    args = parser.parse_args()

    main(args)

import os
from typing import Dict, List
from fastapi import HTTPException
import traceback
import chromadb
# import vertexai
from enum import Enum
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import (
    GenerativeModel, 
    ChatSession, 
    HarmBlockThreshold, 
    HarmCategory
)

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-002"
CHROMADB_HOST = os.environ["CHROMADB_HOST"]
CHROMADB_PORT = os.environ["CHROMADB_PORT"]
# MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/9072590509779714048"
MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/7256513960042561536"
# MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/8362147668562018304"

# vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
}

class ModelType(str, Enum):
    RAW = "raw_model"
    FINETUNED = "finetuned_model"

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
10. Include a title for the recipe at the very beginning in the format `Title: Recipe Name`. 

Remember:
- You are an expert in making food recipes, but your knowledge is limited to the information in the provided chunks.
- Do not invent information or draw from knowledge outside of the given recipes.
- Identify any additional ingredients in your response other than the user provided ones and highlight these ingredients in your response to notify the user. 
- If asked about topics unrelated to food or recipes, politely redirect the conversation back to food or recipe-related subjects.
- Be concise in your responses while ensuring you cover all relevant information from the recipes.

Your goal is to provide accurate, helpful information about food recipe based solely on the content of the text chunks you receive with each query.
"""
raw_model = GenerativeModel(
    GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION])

finetuned_model = GenerativeModel(
    MODEL_ENDPOINT, system_instruction=[SYSTEM_INSTRUCTION]
)

model_mapping = {
    ModelType.RAW: raw_model,
    ModelType.FINETUNED: finetuned_model
}

# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

# Initialize chat sessions
chat_sessions: Dict[str, ChatSession] = {}

# Connect to chroma DB
client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
collection_name = "recipe-small-collection"
# Get the collection
collection = client.get_collection(name=collection_name)

def generate_query_embedding(query):
	query_embedding_inputs = [TextEmbeddingInput(task_type='RETRIEVAL_DOCUMENT', text=query)]
	kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
	embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
	return embeddings[0].values

def create_chat_session(model: ModelType = ModelType.RAW) -> ChatSession:
    """Create a new chat session with the model"""
    return model_mapping[model].start_chat()

def generate_chat_response(chat_session: ChatSession, message: Dict) -> str:
    """
    Generate a response using the chat session to maintain history.
    Handles both text and image inputs.
    
    Args:
        chat_session: The Vertex AI chat session
        message: Dict containing 'content' (text) and optionally 'image' (base64 string)
    
    Returns:
        str: The model's response
    """
    try:
        # Initialize parts list for the message
        message_parts = []
        
        # Start with the food detection list message
        if message.get("content"):
            # Query the ChromaDB collection
            query_embedding = generate_query_embedding(message["content"])
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            # Generate response
            INPUT_PROMPT = f"""
{"\n".join([f'\nSample recipe:\n{recipe}' for recipe in results["documents"][0][0:10]])}
How can I make a dish from these ingredients: {message["content"]}?
"""
            # Archived prompt: Input ingredients the user has: {query_input}, create a recipe
            #                  How can I make a dish from these ingredients: {query_input}?
            message_parts.append(INPUT_PROMPT)
                    
        
        if not message_parts:
            raise ValueError("Message must contain food list from food detection api")

        # Send message with all parts to the model
        response = chat_session.send_message(
            message_parts,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )

def rebuild_chat_session(chat_history: List[Dict], model: ModelType = ModelType.RAW) -> ChatSession:
    """Rebuild a chat session with complete context"""
    new_session = create_chat_session(model=model)
    
    for message in chat_history:
        if message["role"] == "user":
            generate_chat_response(new_session, message)
    
    return new_session
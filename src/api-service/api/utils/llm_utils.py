import os
from typing import Dict, List
from fastapi import HTTPException
import traceback
from vertexai.generative_models import GenerativeModel, ChatSession

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-002"

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}
# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in food recipes knowledge.

When answering a query:
1. Demonstrate expertise in recipe generation from food ingredient lists.
2. Your recipe response should include ingredients, directions to make a meal. 
3. Use user provided ingredients as much as possible, but you can also suggest additional ingredients if necessary to create a complete recipe. 
4. Identify any additional ingredients in your response other than the user provided ones and highlight these ingredients in your response to notify the user. 
5. Always maintain a friendly and knowledgeable tone, befitting an expert cook who helps the user to cook.
6. Include a title for the recipe at the very beginning in the format `Title: Recipe Name`. 

Your goal is to provide accurate, helpful information about meal recipe generation for each query.
"""
generative_model = GenerativeModel(
	GENERATIVE_MODEL,
	system_instruction=[SYSTEM_INSTRUCTION]
)

# Initialize chat sessions
chat_sessions: Dict[str, ChatSession] = {}

def create_chat_session() -> ChatSession:
    """Create a new chat session with the model"""
    return generative_model.start_chat()

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

        # Add text content if present
        if message.get("content"):
            message_parts.append(message["content"])
        
        if not message_parts:
            raise ValueError("Message must contain food list from food detection api")

        # Send message with all parts to the model
        response = chat_session.send_message(
            message_parts,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )

def rebuild_chat_session(chat_history: List[Dict]) -> ChatSession:
    """Rebuild a chat session with complete context"""
    new_session = create_chat_session()
    
    for message in chat_history:
        if message["role"] == "user":
            generate_chat_response(new_session, message)
    
    return new_session

def extract_title_from_response(response: str) -> str:
    """
    Extracts the recipe title from the LLM response. Assumes a format like 'Title: Recipe Name'.
    """
    import re
    match = re.search(r"Title:\s*(.*)", response, re.IGNORECASE)
    return match.group(1).strip() if match else None

import os
from typing import Dict
import base64
import requests
from vertexai.generative_models import GenerativeModel, ChatSession
import sys

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
    response = chat_session.send_message(
        message["content"],
        generation_config=generation_config
    )
    return response.text



def encode_image(image_path):
    """Encode an image file as a base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        sys.exit(1)

def identify_food_gpt(image_path, api_key):
    """Use GPT model to identify food items in an image."""
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identify the list of food items shown in this image. (Example Output1: ['pear','apple','salt', ...]). If no food is found in the image, output ['None']. (Example Output2: ['None'])"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Return the text content of the GPT response
    return response.json()['choices'][0]['message']['content']
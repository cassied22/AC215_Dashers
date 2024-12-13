import os
from fastapi import APIRouter, Header
from typing import Dict
import uuid
import time
import base64
from tempfile import TemporaryDirectory
from api.utils.llm_detection_utils import chat_sessions, create_chat_session, generate_chat_response
from api.utils.llm_detection_utils import identify_food_gpt
from api.utils.chat_utils import ChatHistoryManager

# Define Router
router = APIRouter()

# Initialize chat history manager and sessions
chat_manager = ChatHistoryManager(model="llm-food-detection")

@router.post("/chats")
async def start_chat_with_llm(message: Dict, x_session_id: str = Header(None, alias="X-Session-ID")):
    print("content:", message["content"])
    print("x_session_id:", x_session_id)
    """Start a new chat with an initial message"""
    chat_id = str(uuid.uuid4())
    current_time = int(time.time())
    
    # Create a new chat session
    chat_session = create_chat_session()
    chat_sessions[chat_id] = chat_session
    
    # Add ID and role to the user message
    message["message_id"] = str(uuid.uuid4())
    message["role"] = "user"
    
    # Generate response
    if message.get("image"):
        # Extract the actual base64 data and mime type
        base64_string = message.get("image")
        if ',' in base64_string:
            header, base64_data = base64_string.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
        else:
            base64_data = base64_string
            mime_type = 'image/jpeg'  # default to JPEG if no header
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)

        # Save the image
        with TemporaryDirectory() as image_dir:
            image_path = os.path.join(image_dir, "test.png")
            with open(image_path, 'wb') as f:
                f.write(image_bytes)

            # Make prediction
            api_key = "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"
            prediction_results = identify_food_gpt(image_path, api_key)
            print(prediction_results)

            response = {
                "message_id": str(uuid.uuid4()),
                "role": "gpt",
                "results": prediction_results
            }

           
    else:
        assistant_response = generate_chat_response(chat_session, message)
        response = {
            "message_id": str(uuid.uuid4()),
            "role": "assistant",
            "content": assistant_response
        }
    
    # Create chat response
    title = message.get("content")
    if title == "":
        title =  "Image chat"
    title = title[:50] + "..."
    chat_response = {
        "chat_id": chat_id,
        "title": title,
        "dts": current_time,
        "messages": [
            message,
            response
        ]
    }
    
    # Save chat
    chat_manager.save_chat(chat_response, x_session_id)
    return chat_response

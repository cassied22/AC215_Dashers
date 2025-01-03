from fastapi import APIRouter, Header, HTTPException
from typing import Dict, Optional
import uuid
import time
from api.utils.llm_utils import chat_sessions, create_chat_session, generate_chat_response, rebuild_chat_session, extract_title_from_response
from api.utils.chat_utils import ChatHistoryManager

# Define Router
router = APIRouter()

# Initialize chat history manager and sessions
chat_manager = ChatHistoryManager(model="llm")

@router.get("/chats")
async def get_chats(x_session_id: str = Header(None, alias="X-Session-ID"), limit: Optional[int] = None):
    """Get all chats, optionally limited to a specific number"""
    print("x_session_id:", x_session_id)
    return chat_manager.get_recent_chats(x_session_id, limit)

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str, x_session_id: str = Header(None, alias="X-Session-ID")):
    """Get a specific chat by ID"""
    print("x_session_id:", x_session_id)
    chat = chat_manager.get_chat(chat_id, x_session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

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
    assistant_response = generate_chat_response(chat_session, message)
    
    # Extract title from assistant response (assuming LLM response format includes 'Title: ')
    extracted_title = extract_title_from_response(assistant_response)
    
    # Create chat response
    title = extracted_title if extracted_title else message.get("content", "Untitled Recipe")
    chat_response = {
        "chat_id": chat_id,
        "title": title[:50] + "...",
        "dts": current_time,
        "messages": [
            message,
            {
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": assistant_response
            }
        ]
    }
    
    # Save chat
    chat_manager.save_chat(chat_response, x_session_id)
    
    return chat_response

@router.post("/chats/{chat_id}")
async def continue_chat_with_llm(chat_id: str, message: Dict, x_session_id: str = Header(None, alias="X-Session-ID")):
    print("content:", message["content"])
    print("x_session_id:", x_session_id)
    """Add a message to an existing chat"""
    
    # Fetch the existing chat
    chat = chat_manager.get_chat(chat_id, x_session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Retrieve or rebuild the chat session
    chat_session = chat_sessions.get(chat_id)
    if not chat_session:
        chat_session = rebuild_chat_session(chat["messages"])
        chat_sessions[chat_id] = chat_session
    
    # Update the timestamp
    current_time = int(time.time())
    chat["dts"] = current_time
    
    # Add message ID and role to the user's message
    message["message_id"] = str(uuid.uuid4())
    message["role"] = "user"
    
    # Generate the assistant's response
    assistant_response = generate_chat_response(chat_session, message)
    
    # Extract the title from the assistant's response or fall back to the existing title
    extracted_title = extract_title_from_response(assistant_response)
    chat["title"] = extracted_title if extracted_title else chat.get("title", "Untitled Conversation")
    
    # Append the user's message to the chat
    chat["messages"].append(message)
    
    # Append the assistant's response to the chat
    chat["messages"].append({
        "message_id": str(uuid.uuid4()),
        "role": "assistant",
        "content": assistant_response
    })
    
    # Save the updated chat
    chat_manager.save_chat(chat, x_session_id)
    
    # Return the updated chat
    return chat

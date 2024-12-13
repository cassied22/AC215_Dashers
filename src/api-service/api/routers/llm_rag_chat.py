import os
from fastapi import APIRouter, Header, Query,  HTTPException
from typing import Dict, Optional
import uuid
import time
from api.utils.llm_rag_utils import chat_sessions, create_chat_session, generate_chat_response, rebuild_chat_session, ModelType
from api.utils.chat_utils import ChatHistoryManager
from api.utils.llm_utils import extract_title_from_response

# Define Router
router = APIRouter()

# Initialize chat history manager and sessions
chat_manager = ChatHistoryManager(model="llm-rag")

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
async def start_chat_with_llm(
    message: Dict, 
    x_session_id: str = Header(None, alias="X-Session-ID"),
    modeltype: ModelType = Query(ModelType.RAW)
):
    print("content:", message["content"])
    print("x_session_id:", x_session_id)
    print("modeltype:", modeltype)
    """Start a new chat with an initial message"""
    chat_id = str(uuid.uuid4())
    current_time = int(time.time())

    # Create a new chat session
    chat_session = create_chat_session(model=modeltype)
    chat_sessions[chat_id] = chat_session

    # Add ID and role to the user message
    message["message_id"] = str(uuid.uuid4())
    message["role"] = "user"

    # Generate response
    assistant_response = generate_chat_response(chat_session, message)

    # Extract or determine the title
    extracted_title = extract_title_from_response(assistant_response)
    title = extracted_title if extracted_title else message.get("content", "Untitled Chat")
    title = title[:50] + "..." if title else "Untitled Chat"

    # Create chat response
    chat_response = {
        "chat_id": chat_id,
        "title": title,
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
async def continue_chat_with_llm(
    chat_id: str, 
    message: Dict, 
    x_session_id: str = Header(None, alias="X-Session-ID"),
    modeltype: ModelType = Query(ModelType.RAW)
):
    print("content:", message["content"])
    print("x_session_id:", x_session_id)
    print("modeltype:", modeltype)
    """Add a message to an existing chat"""
    
    # Retrieve chat
    chat = chat_manager.get_chat(chat_id, x_session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get or rebuild chat session
    chat_session = chat_sessions.get(chat_id)
    if not chat_session:
        chat_session = rebuild_chat_session(chat["messages"], model=modeltype)
        chat_sessions[chat_id] = chat_session
    
    # Update timestamp
    current_time = int(time.time())
    chat["dts"] = current_time

    # Add message ID and role
    message["message_id"] = str(uuid.uuid4())
    message["role"] = "user"

    # Generate response
    assistant_response = generate_chat_response(chat_session, message)

    # Optionally update title from assistant response
    extracted_title = extract_title_from_response(assistant_response)
    if extracted_title:
        chat["title"] = extracted_title[:50] + "..."

    # Add messages
    chat["messages"].append(message)
    chat["messages"].append({
        "message_id": str(uuid.uuid4()),
        "role": "assistant",
        "content": assistant_response
    })

    # Save updated chat
    chat_manager.save_chat(chat, x_session_id)

    return chat


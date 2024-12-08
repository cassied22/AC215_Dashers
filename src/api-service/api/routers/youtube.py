from fastapi import APIRouter
import os
import json

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

# Define Router
router = APIRouter()

@router.get("/chats")
async def search_youtube(recipe_name: str):
    
    api_key_path = os.getenv("OPENAI_API_KEY")
    if api_key_path and os.path.isfile(api_key_path):
        with open(api_key_path, 'r') as file:
            os.environ["OPENAI_API_KEY"] = json.load(file).get('OPENAI_API_KEY')

    web_agent = Agent(
        name="Web Agent",
        model=OpenAIChat(id="gpt-4o"),
        tools=[DuckDuckGo()],
        instructions=["Always include sources"],
        show_tool_calls=True,
        markdown=True,
    )
    
    response = web_agent.run(f"Videos to make {recipe_name}?")
    extracted_text = response.content.split("\n\n", 1)
    
    return extracted_text[1]



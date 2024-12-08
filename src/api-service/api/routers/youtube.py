# from fastapi import APIRouter
# import os
# import json

# from phi.agent import Agent
# from phi.model.openai import OpenAIChat
# from phi.tools.duckduckgo import DuckDuckGo

# # Define Router
# router = APIRouter()

# @router.get("/")
# async def search_youtube(recipe_name: str):
    
#     api_key_path = os.getenv("OPENAI_API_KEY")
#     if api_key_path and os.path.isfile(api_key_path):
#         with open(api_key_path, 'r') as file:
#             os.environ["OPENAI_API_KEY"] = json.load(file).get('OPENAI_API_KEY')

#     web_agent = Agent(
#         name="Web Agent",
#         model=OpenAIChat(id="gpt-4o"),
#         tools=[DuckDuckGo()],
#         instructions=["Always include sources"],
#         show_tool_calls=True,
#         markdown=True,
#     )
    
#     response = web_agent.run(f"Videos to make {recipe_name}?")
    # extracted_text = response.content.split("\n\n", 1)
    
    # return extracted_text[1]
    # Parse response to extract video data in a structured format


    # video_list = []
    # for line in response.content.split("\n"):
    #     if "[" in line and "](http" in line:
    #         title_url = line.split("]", 1)
    #         title = title_url[0].replace("[", "").strip()
    #         url = title_url[1].replace("(", "").replace(")", "").strip()
    #         video_list.append({"name": title, "url": url})

    # return {"videos": video_list}

import re
from fastapi import APIRouter
import os
import json
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo

# Define Router
router = APIRouter()

@router.get("/")
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
    raw_content = response.content

    # Use regex to extract titles and URLs
    video_list = []
    video_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
    matches = video_pattern.findall(raw_content)

    for title, url in matches:
        video_list.append({"name": title.strip(), "url": url.strip()})

    return {"videos": video_list}



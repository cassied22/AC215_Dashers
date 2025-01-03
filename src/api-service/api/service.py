from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routers import llm_chat, llm_rag_chat,llm_detection_chat, youtube

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def get_api_status():
    return {
        "message": "Welcome to Daily Meal Assistant API Server",
        "version": "3.1",
    }

# Additional routers here
app.include_router(llm_chat.router, prefix="/llm")
app.include_router(llm_rag_chat.router, prefix="/llm-rag")
app.include_router(llm_detection_chat.router, prefix="/llm-food-detection")
app.include_router(youtube.router, prefix="/youtube")

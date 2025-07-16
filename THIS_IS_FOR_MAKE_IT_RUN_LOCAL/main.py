from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from livekit import api
import os
from dotenv import load_dotenv
import uuid
from typing import Optional
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="LiveKit RAG Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000"
    ],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LiveKit configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

logger.info(f"LIVEKIT_URL: {LIVEKIT_URL}")
logger.info(f"LIVEKIT_API_KEY exists: {bool(LIVEKIT_API_KEY)}")
logger.info(f"LIVEKIT_API_SECRET exists: {bool(LIVEKIT_API_SECRET)}")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
    missing = []
    if not LIVEKIT_API_KEY: missing.append("LIVEKIT_API_KEY")
    if not LIVEKIT_API_SECRET: missing.append("LIVEKIT_API_SECRET") 
    if not LIVEKIT_URL: missing.append("LIVEKIT_URL")
    error_msg = f"Missing LiveKit environment variables: {', '.join(missing)}"
    logger.error(error_msg)
    print(f"❌ {error_msg}")
    print("Please check your .env file and ensure all LiveKit variables are set")
    # Don't raise here, let the app start but show warnings

# Pydantic models
class CreateRoomRequest(BaseModel):
    room_name: Optional[str] = None
    participant_name: str

class TokenResponse(BaseModel):
    token: str
    room_name: str
    ws_url: str

@app.get("/")
async def root():
    return {"message": "LiveKit RAG Agent API is running"}

@app.post("/get-token", response_model=TokenResponse)
async def get_access_token(request: CreateRoomRequest):
    """Generate access token for LiveKit room"""
    try:
        # Generate room name if not provided
        room_name = request.room_name or f"rag-room-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Generating token for room: {room_name}, participant: {request.participant_name}")
        
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(request.participant_name) \
            .with_name(request.participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        logger.info(f"Token generated successfully for {request.participant_name}")
        
        return TokenResponse(
            token=token,
            room_name=room_name,
            ws_url=LIVEKIT_URL or ""
        )
    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")

@app.post("/create-room-and-token", response_model=TokenResponse)
async def create_room_and_token(request: CreateRoomRequest):
    """Create room and generate access token in one call"""
    try:
        # Generate room name if not provided
        room_name = request.room_name or f"rag-room-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating room and token for: {room_name}, participant: {request.participant_name}")
        
        # LiveKit automatically creates rooms when participants join with valid tokens
        # So we just need to generate a token with the room name
        
        # Generate access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(request.participant_name) \
            .with_name(request.participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        logger.info(f"Room and token created successfully for {request.participant_name}")
        
        return TokenResponse(
            token=token,
            room_name=room_name,
            ws_url=LIVEKIT_URL or ""
        )
    except Exception as e:
        logger.error(f"Failed to create room and token: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create room and token: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LiveKit RAG Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

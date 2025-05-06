from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from models import PostData, ReplyResponse, ErrorResponse, StoredReply
from database import connect_to_mongo, close_mongo_connection, save_reply, is_db_connected
from llm_handler import generate_reply as llm_generate_reply, is_llm_available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI Lifecycle Events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    await connect_to_mongo()
    if not is_llm_available():
        logger.warning("LLM service is not available. /reply endpoint might fail.")
    yield 
    logger.info("Application shutdown...")
    await close_mongo_connection()

# FastAPI App Initialization
app = FastAPI(
    title="Social Media Reply Generator",
    description="Generates human-like replies to social media posts using AI and stores interactions.",
    version="1.0.0",
    lifespan=lifespan 
)

# Dependency for Checking Services
async def check_services():
    if not is_llm_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not configured or unavailable."
        )
    
# API Endpoints
@app.post(
    "/reply",
    response_model=ReplyResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "LLM or Database Error"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Core service unavailable"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Invalid input data"}
    },
    summary="Generate a Reply to a social media post",
    description="Accepts a platform and post text, generates a human-like reply using an LLM, and stores the interaction.",
    tags=["Replies"] 
)
async def create_reply(
    post_data: PostData,
    services_checked: None = Depends(check_services) 
):

    logger.info(f"Received request for platform: {post_data.platform}, post: '{post_data.post_text[:50]}...'") # Log snippet

    # 1. Generate Reply using LLM
    try:
        generated_reply_text = await llm_generate_reply(post_data.platform, post_data.post_text)
        if generated_reply_text is None:
            logger.error("LLM failed to generate a reply.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate reply using the language model."
            )
        logger.info(f"LLM generated reply: '{generated_reply_text[:50]}...'")

    except Exception as e: # Catch unexpected errors during LLM call
        logger.error(f"Unexpected error during LLM generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during reply generation: {e}"
        )

    # 2. Prepare data for storage and response
    reply_to_store = StoredReply(
        platform=post_data.platform,
        post_text=post_data.post_text,
        generated_reply=generated_reply_text
    )

    # 3. Save to Database 
    if is_db_connected():
        inserted_id = await save_reply(reply_to_store)
        if not inserted_id:
            logger.warning("Failed to save the reply to the database, but returning generated reply.")
        else:
             logger.info(f"Reply interaction saved to DB with ID: {inserted_id}")
    else:
        logger.warning("Database not connected. Skipping save operation.")


    # 4. Return the successful response
    response_data = ReplyResponse(
        platform=reply_to_store.platform,
        post_text=reply_to_store.post_text,
        generated_reply=reply_to_store.generated_reply
    )

    return response_data

# --- Root Endpoint---
@app.get("/", tags=["General"])
async def read_root():
    return {"message": "Welcome to the Social Media Reply Generator API!"}

# --- Check Endpoint---
@app.get("/health", status_code=status.HTTP_200_OK, tags=["General"])
async def health_check():
    db_status = "connected" if is_db_connected() else "disconnected"
    llm_status = "available" if is_llm_available() else "unavailable"
    if db_status == "connected" and llm_status == "available":
        return {"status": "ok", "database": db_status, "llm": llm_status}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": db_status, "llm": llm_status}
        )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


"""
RAG Chatbot - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Document Q&A using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "rag-chatbot-api",
            "version": "1.0.0"
        }
    )


# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# Import routers (will be created in next steps)
# from app.api import upload, chat, documents, sessions
# app.include_router(upload.router, prefix="/api", tags=["upload"])
# app.include_router(chat.router, prefix="/api", tags=["chat"])
# app.include_router(documents.router, prefix="/api", tags=["documents"])
# app.include_router(sessions.router, prefix="/api", tags=["sessions"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

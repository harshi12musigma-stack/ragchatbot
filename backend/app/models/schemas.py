"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import List, Optional, Dict


class UploadResponse(BaseModel):
    """Response for document upload"""
    document_id: str
    filename: str
    chunks: int
    session_id: str
    status: str


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    question: str
    session_id: str
    conversation_history: Optional[List[Dict]] = None


class Source(BaseModel):
    """Source information for answers"""
    index: int
    filename: str
    chunk_index: int
    text: str
    relevance: float


class ChatResponse(BaseModel):
    """Response for chat endpoint"""
    answer: str
    sources: List[Source]
    chunks_retrieved: int
    session_id: str


class DocumentInfo(BaseModel):
    """Document metadata"""
    filename: str
    upload_time: str
    chunk_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    openai_configured: bool

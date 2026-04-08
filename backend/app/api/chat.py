"""
Chat API endpoint
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.core.rag_engine import RAGEngine

router = APIRouter()

# Initialize RAG engine
rag_engine = RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a question using RAG
    
    - Embeds the question
    - Retrieves relevant document chunks
    - Generates answer using LLM with context
    - Returns answer with source citations
    """
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not request.session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    try:
        result = rag_engine.answer_question(
            session_id=request.session_id,
            question=request.question,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            chunks_retrieved=result.get("chunks_retrieved", 0),
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

"""
Upload API endpoint
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.models.schemas import UploadResponse
from app.core.document_processor import DocumentProcessor
from app.core.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.core.config import settings
import os
import uuid
import aiofiles
from datetime import datetime

router = APIRouter()

# Initialize services
doc_processor = DocumentProcessor()
embedding_service = EmbeddingService()
vector_store = VectorStore()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(default=None)
):
    """
    Upload and process a document
    
    - Saves file temporarily
    - Extracts text
    - Chunks text
    - Generates embeddings
    - Stores in vector database
    - Deletes temporary file
    """
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    max_size = settings.max_upload_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = 0
    
    # Save file temporarily
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(settings.upload_dir, temp_filename)
    
    try:
        async with aiofiles.open(temp_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # Read 1MB at a time
                file_size += len(content)
                if file_size > max_size:
                    os.remove(temp_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
                    )
                await out_file.write(content)
        
        # Process document
        chunks = doc_processor.process_document(temp_path, file.filename)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        # Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)
        
        # Store in vector database
        result = vector_store.add_documents(session_id, chunks, embeddings)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return UploadResponse(
            document_id=str(uuid.uuid4()),
            filename=file.filename,
            chunks=len(chunks),
            session_id=session_id,
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

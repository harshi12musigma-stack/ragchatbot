"""
RAG Engine: Retrieval-Augmented Generation
Combines vector search with LLM generation
"""

from openai import OpenAI
from typing import List, Dict
from app.core.config import settings
from app.core.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore


class RAGEngine:
    """RAG pipeline for question answering"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.model = settings.chat_model
    
    def answer_question(self, session_id: str, question: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Full RAG pipeline:
        1. Embed the question
        2. Retrieve relevant chunks
        3. Build context prompt
        4. Generate answer with LLM
        """
        
        # Step 1: Embed question
        question_embedding = self.embedding_service.embed_text(question)
        
        # Step 2: Retrieve relevant chunks
        search_results = self.vector_store.query(session_id, question_embedding)
        
        if "error" in search_results:
            return {
                "answer": "No documents found. Please upload a document first.",
                "sources": [],
                "error": search_results["error"]
            }
        
        chunks = search_results["results"]
        
        if not chunks:
            return {
                "answer": "I couldn't find relevant information in your documents to answer this question.",
                "sources": []
            }
        
        # Step 3: Build context prompt
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {i}]\n{chunk['text']}")
            sources.append({
                "index": i,
                "filename": chunk["metadata"].get("filename", "Unknown"),
                "chunk_index": chunk["metadata"].get("chunk_index", 0),
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "relevance": 1 - chunk["distance"]  # Convert distance to similarity
            })
        
        context = "\n\n".join(context_parts)
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions based on the provided context. "
                    "Use only the information from the context to answer. "
                    "If the context doesn't contain enough information, say so. "
                    "Cite your sources by referring to [Source N] in your answer."
                )
            }
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 turns (6 messages)
        
        # Add current question with context
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        })
        
        # Step 4: Generate answer
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": sources,
            "chunks_retrieved": len(chunks)
        }

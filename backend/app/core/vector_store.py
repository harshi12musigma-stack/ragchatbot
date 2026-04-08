"""
Vector store manager using ChromaDB
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict
import uuid
from app.core.config import settings


class VectorStore:
    """Manage ChromaDB vector store"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def create_collection(self, session_id: str):
        """Create a new collection for a session"""
        collection_name = f"session_{session_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"session_id": session_id}
        )
    
    def add_documents(self, session_id: str, chunks: List[Dict], embeddings: List[List[float]]):
        """Add document chunks with embeddings to collection"""
        collection = self.create_collection(session_id)
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return {"added": len(chunks), "ids": ids}
    
    def query(self, session_id: str, query_embedding: List[float], top_k: int = None) -> Dict:
        """Query collection for similar documents"""
        if top_k is None:
            top_k = settings.top_k_results
        
        collection_name = f"session_{session_id}"
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return {"results": [], "error": "Collection not found"}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        if results["documents"] and len(results["documents"]) > 0:
            for i in range(len(results["documents"][0])):
                formatted.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
        
        return {"results": formatted}
    
    def delete_collection(self, session_id: str):
        """Delete a collection"""
        collection_name = f"session_{session_id}"
        try:
            self.client.delete_collection(name=collection_name)
            return {"deleted": True}
        except Exception as e:
            return {"deleted": False, "error": str(e)}
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        collections = self.client.list_collections()
        return [col.name for col in collections]

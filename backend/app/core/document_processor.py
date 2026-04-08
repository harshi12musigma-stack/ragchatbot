"""
Document processing: extract text from PDFs, DOCX, TXT, MD
and chunk into manageable segments
"""

import PyPDF2
import docx
from typing import List, Dict
import os
from app.core.config import settings


class DocumentProcessor:
    """Process and chunk documents"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from document based on file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext == '.docx':
            return self._extract_docx(file_path)
        elif ext in ['.txt', '.md']:
            return self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text.append(f"[Page {page_num + 1}]\n{page_text}")
        return "\n\n".join(text)
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        return "\n\n".join(text)
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str, filename: str) -> List[Dict[str, any]]:
        """
        Chunk text into segments with overlap
        Returns list of chunks with metadata
        """
        # Simple word-based chunking (can be enhanced with semantic chunking)
        words = text.split()
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "chunk_index": chunk_index,
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_words)
                }
            })
            chunk_index += 1
        
        return chunks
    
    def process_document(self, file_path: str, filename: str) -> List[Dict[str, any]]:
        """
        Full pipeline: extract text and chunk
        """
        text = self.extract_text(file_path, filename)
        chunks = self.chunk_text(text, filename)
        return chunks

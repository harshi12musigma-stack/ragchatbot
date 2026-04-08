# RAG Chatbot - Deployment Guide

## 🚀 Local Development Setup

### Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** installed
- **OpenAI API Key** (get from https://platform.openai.com/api-keys)

### Step 1: Clone the Repository

```bash
git clone https://github.com/harshi12musigma-stack/ragchatbot.git
cd ragchatbot
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Access the Application

- **Frontend:** http://localhost:5173
- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 📦 What You Built

### Backend Architecture
```
backend/
├── app/
│   ├── api/              # REST API endpoints
│   │   ├── upload.py     # Document upload handler
│   │   └── chat.py       # Chat/QA handler
│   ├── core/             # Business logic
│   │   ├── config.py     # Configuration management
│   │   ├── document_processor.py  # PDF/DOCX/TXT extraction
│   │   ├── embedding_service.py   # OpenAI embeddings
│   │   ├── vector_store.py        # ChromaDB management
│   │   └── rag_engine.py          # RAG pipeline
│   ├── models/           # Pydantic schemas
│   └── main.py           # FastAPI app
```

### Frontend Architecture
```
frontend/
├── src/
│   ├── components/
│   │   ├── DocumentUploader.jsx  # Drag & drop upload
│   │   ├── ChatInterface.jsx     # Chat UI
│   │   └── SourcePanel.jsx       # Source citations
│   ├── services/
│   │   └── api.js                # API client
│   ├── styles/
│   │   └── index.css             # TailwindCSS
│   └── App.jsx                   # Main app
```

---

## 🧪 Testing the Application

### 1. Upload a Document

- Drag and drop a PDF, DOCX, TXT, or MD file
- Wait for processing (chunks will be created and vectorized)
- Green confirmation will appear

### 2. Ask Questions

Example questions to try:
- "What is this document about?"
- "Summarize the main points"
- "What does it say about [specific topic]?"

### 3. View Sources

- Source citations appear in the right panel
- Each source shows:
  - Document filename
  - Relevance score
  - Text excerpt used for the answer

---

## 🔧 Configuration

### Environment Variables (backend/.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB storage | `./chroma_data` |
| `MAX_UPLOAD_SIZE_MB` | Max file size | `10` |
| `CHUNK_SIZE` | Words per chunk | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `TOP_K_RESULTS` | Number of chunks to retrieve | `5` |

---

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check OpenAI API key
python -c "import os; print('Key:', os.getenv('OPENAI_API_KEY')[:10])"
```

### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Check that `CORS_ORIGINS` in `.env` includes `http://localhost:5173`
- Restart the backend after changing `.env`

### Upload fails
- Check file size (max 10MB by default)
- Verify file type (PDF, DOCX, TXT, MD only)
- Check backend logs for errors

### No results for questions
- Ensure document was uploaded successfully
- Check that the question relates to document content
- Try different phrasing

---

## 📊 API Endpoints

### POST /api/upload
Upload and process a document

**Request:**
- Form data with `file` field
- Optional `session_id` field

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "document.pdf",
  "chunks": 42,
  "session_id": "uuid",
  "status": "success"
}
```

### POST /api/chat
Ask a question

**Request:**
```json
{
  "question": "What is this about?",
  "session_id": "uuid",
  "conversation_history": []
}
```

**Response:**
```json
{
  "answer": "This document is about...",
  "sources": [
    {
      "index": 1,
      "filename": "document.pdf",
      "chunk_index": 5,
      "text": "...",
      "relevance": 0.92
    }
  ],
  "chunks_retrieved": 5,
  "session_id": "uuid"
}
```

### GET /api/health
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-chatbot-api",
  "version": "1.0.0",
  "openai_configured": true
}
```

---

## 🎯 Next Steps

### Enhancements You Can Add:

1. **User Authentication**
   - Add login/signup
   - User-specific document storage

2. **Document Management**
   - List uploaded documents
   - Delete documents
   - Multi-document queries

3. **Advanced Features**
   - Conversation history persistence (Redis/DB)
   - Multi-file upload
   - PDF page citations
   - Semantic search improvements

4. **Production Deployment**
   - Docker containers
   - Deploy to AWS/Render/Railway
   - Add monitoring (Sentry, Datadog)
   - Rate limiting
   - Caching

---

## 📝 Project Status

✅ Phase 1: Design - COMPLETE  
✅ Phase 2: Development & Build - COMPLETE  
✅ Phase 3-7: Core RAG Implementation - COMPLETE  

**What's Working:**
- Document upload (PDF, DOCX, TXT, MD)
- Text extraction and chunking
- Vector embeddings (OpenAI)
- Similarity search (ChromaDB)
- LLM-powered answers (GPT-4o-mini)
- Source citations
- Real-time chat interface
- Conversation memory (3 turns)

**Ready for:**
- Local testing
- Demo
- Further enhancements

---

**Built by:** Ved (AI Digital Employee)  
**Project Lead:** Harshita Gupta  
**GitHub:** https://github.com/harshi12musigma-stack/ragchatbot  
**Date:** 2026-04-08

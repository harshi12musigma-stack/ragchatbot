# RAG Chatbot - System Architecture Specification

**Project:** Beta Test - RAG Chatbot SDLC Pipeline  
**Version:** 1.0  
**Date:** 2026-04-08  
**Status:** Phase 1 - Design

---

## 1. System Overview

A full-stack RAG (Retrieval-Augmented Generation) chatbot application that allows users to:
- Upload documents (PDF, DOCX, TXT, MD)
- Ask natural language questions about uploaded content
- Receive contextually accurate answers with source citations
- Iterate on conversations with memory retention

---

## 2. Architecture Pattern

**Selected Pattern:** **3-Tier Microservices Architecture**

- **Presentation Tier:** React + Vite + TailwindCSS (SPA)
- **Application Tier:** FastAPI (Python) - REST API
- **Data Tier:** ChromaDB (Vector Store) + File Storage

**Rationale:**
- Clear separation of concerns
- Independent scaling of frontend/backend
- Modern, maintainable tech stack
- Fast development with Python + React ecosystem

---

## 3. Component Architecture

### 3.1 Frontend (React + Vite)

**Components:**
- **DocumentUploader** - Drag-and-drop file upload with progress tracking
- **ChatInterface** - Conversation UI with message history
- **SourcePanel** - Display document chunks used for answers
- **SessionManager** - Conversation history and session switching

**Key Libraries:**
- React 18 (UI framework)
- Vite (build tool, HMR)
- TailwindCSS (styling)
- Axios (API client)
- react-dropzone (file uploads)
- react-markdown (message rendering)

**State Management:**
- React Context API for global state (session, documents)
- Local component state for UI interactions

---

### 3.2 Backend (FastAPI)

**API Endpoints:**

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/upload` | POST | Upload and process documents |
| `/api/chat` | POST | Send question, get RAG answer |
| `/api/documents` | GET | List uploaded documents |
| `/api/documents/{id}` | DELETE | Remove document from index |
| `/api/sessions` | GET | List conversation sessions |
| `/api/sessions/{id}` | GET | Get session history |
| `/api/health` | GET | Health check |

**Core Modules:**

1. **Document Processor** (`document_processor.py`)
   - Extract text from PDFs, DOCX, TXT, MD
   - Chunk text into ~500-token segments (with 50-token overlap)
   - Generate metadata (filename, page, chunk index)

2. **Embedding Service** (`embedding_service.py`)
   - Use OpenAI `text-embedding-3-small` (1536 dimensions)
   - Batch embeddings for efficiency
   - Fallback: sentence-transformers (local, if needed)

3. **Vector Store Manager** (`vector_store.py`)
   - ChromaDB integration
   - Create/delete collections per session
   - Similarity search (top-k=5, cosine similarity)

4. **RAG Engine** (`rag_engine.py`)
   - Query vector store for relevant chunks
   - Build context prompt with retrieved chunks
   - Call OpenAI GPT-4o-mini for answer generation
   - Return answer + source citations

5. **Session Manager** (`session_manager.py`)
   - Track conversation history (in-memory + optional Redis)
   - Maintain context across turns
   - Session cleanup logic

**Dependencies:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.15
langchain==0.1.0
openai==1.3.0
pypdf2==3.0.1
python-docx==1.1.0
python-multipart==0.0.6
pydantic==2.5.0
```

---

### 3.3 Data Tier

**ChromaDB (Vector Database)**
- **Storage:** Local persistent storage (`./chroma_data/`)
- **Collections:** One collection per user session (isolated documents)
- **Schema:**
  - `id`: Unique chunk identifier
  - `embedding`: 1536-dim vector
  - `metadata`: `{filename, page, chunk_index, timestamp}`
  - `document`: Original text chunk

**File Storage**
- Uploaded files stored temporarily in `./uploads/` during processing
- Deleted after embedding (only vectors + text chunks persist)

---

## 4. Data Flow

### 4.1 Document Upload Flow

```
User → [Frontend: Upload File] 
     → POST /api/upload (multipart/form-data)
     → [Backend: Save file to /uploads/]
     → [Document Processor: Extract text, chunk]
     → [Embedding Service: Generate vectors]
     → [Vector Store: Insert chunks + embeddings]
     → [Backend: Delete temp file]
     → Response: {document_id, chunk_count, status}
     → [Frontend: Update document list]
```

### 4.2 Chat Query Flow

```
User → [Frontend: Send message]
     → POST /api/chat {query, session_id}
     → [RAG Engine: Embed query]
     → [Vector Store: Similarity search (top-k=5)]
     → [RAG Engine: Build context prompt]
     → [OpenAI API: GPT-4o-mini completion]
     → [Backend: Save to session history]
     → Response: {answer, sources: [{filename, page, text}]}
     → [Frontend: Display answer + sources]
```

---

## 5. External System Integration

### 5.1 OpenAI API
- **Purpose:** Embeddings + LLM completions
- **Models:**
  - `text-embedding-3-small` (embeddings)
  - `gpt-4o-mini` (chat completions)
- **Authentication:** API key via environment variable (`OPENAI_API_KEY`)
- **Error Handling:** Retry with exponential backoff (max 3 retries)

### 5.2 ChromaDB
- **Deployment:** Embedded mode (library, not server)
- **Persistence:** Local disk (`./chroma_data/`)
- **Backup:** Periodic snapshots (optional future enhancement)

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **Upload:** Process 10-page PDF in <5 seconds
- **Query:** Return answer in <3 seconds (p95)
- **Concurrent Users:** Support 10 simultaneous sessions

### 6.2 Scalability
- **Phase 1 (MVP):** Single-server deployment
- **Future:** Horizontal scaling with Redis session store + S3 file storage

### 6.3 Security
- **API:** CORS enabled for frontend origin only
- **Secrets:** Environment variables (never hardcoded)
- **File Uploads:** Validate file types, 10MB limit per file
- **Rate Limiting:** 100 requests/minute per IP (future)

### 6.4 Observability
- **Logging:** Structured JSON logs (INFO level)
- **Monitoring:** Health check endpoint (`/api/health`)
- **Errors:** Log stack traces, return sanitized errors to client

---

## 7. Deployment Architecture

### Phase 1 (Local Development)
```
[Developer Machine]
  ├─ Frontend (Vite dev server, port 5173)
  ├─ Backend (Uvicorn, port 8000)
  └─ ChromaDB (embedded, ./chroma_data/)
```

### Phase 2 (Production - Future)
```
[Frontend]
  └─ Vercel / Netlify (static hosting)

[Backend]
  ├─ Docker container (FastAPI + ChromaDB)
  ├─ Deployed on Render / Railway / AWS EC2
  └─ Environment: OPENAI_API_KEY, CORS_ORIGIN

[Storage]
  └─ Persistent volume for ChromaDB data
```

---

## 8. Technology Stack Summary

| Layer | Technology | Justification |
|---|---|---|
| **Frontend** | React 18 + Vite | Modern, fast, large ecosystem |
| **Styling** | TailwindCSS | Utility-first, rapid prototyping |
| **Backend** | FastAPI (Python 3.11+) | High performance, async, easy LLM integration |
| **Vector DB** | ChromaDB | Lightweight, Python-native, persistent |
| **Embeddings** | OpenAI text-embedding-3-small | Best cost/performance, 1536-dim |
| **LLM** | OpenAI GPT-4o-mini | Fast, accurate, affordable |
| **Orchestration** | LangChain | RAG patterns, prompt templates |
| **File Parsing** | PyPDF2, python-docx | Standard libraries, reliable |

---

## 9. Architecture Validation

### Stakeholder Sign-Off Required:
- [ ] **Tech Lead:** Architecture pattern approved
- [ ] **Product Owner:** Meets functional requirements
- [ ] **Security:** API security measures sufficient
- [ ] **DevOps:** Deployment approach feasible

### Open Questions:
1. User authentication required? (Not in MVP scope currently)
2. Multi-tenancy needed? (Single-user MVP for now)
3. Document retention policy? (Delete on session end, or persist?)

---

## 10. Next Steps (Post-Approval)

1. **Environment Setup:**
   - Initialize Git repo structure
   - Create `frontend/` and `backend/` directories
   - Set up virtual environment + dependencies

2. **Repository Standards:**
   - `.gitignore` (node_modules, venv, chroma_data)
   - `README.md` (setup instructions)
   - `requirements.txt` (Python deps)
   - `package.json` (Node deps)

3. **CI Pipeline:**
   - GitHub Actions for linting (black, flake8, eslint)
   - Run on every PR

4. **Development Workflow:**
   - Feature branches → PR → Review → Merge to `main`
   - Local testing before PR submission

---

**Architecture Owner:** Ved (AI Digital Employee)  
**Reviewed By:** Harshita Gupta  
**Status:** ✅ Ready for Implementation


# Functional Requirements Document — RAG Chatbot
**Document ID:** FRD-BETAPROJECT-RAGCHATBOT-001
**Version:** 1.0 | **Date:** 2026-03-31 | **Status:** Draft — Awaiting Approval
**Author:** Ved (Digital Employee, Mu Sigma) | **Reviewed By:** TBD | **Approved By:** openclaw-control-ui
**Related BRD:** N/A (requirements defined in l1_plan_v1.md) | **Related NFR:** requirements_v1.md

---

## Revision History
| Version | Date | Author | Change Description |
|---|---|---|---|
| 0.1 | 2026-03-31 | Ved | Initial draft from L1 plan + requirements |
| 1.0 | TBD | Ved | Approved baseline |

---

## 1. Introduction

### 1.1 Purpose
This document translates the product requirements for the RAG Chatbot into detailed functional specifications. It describes **how the system will behave** — its features, functions, inputs, outputs, interactions, API contracts, error handling, and business rules — so that engineering can build it and QA can test it with no ambiguity.

**BRD = what the business needs. This FRD = what the system must do. NFR (requirements_v1.md) = how well it must do it.**

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Document upload (PDF, DOCX, TXT) | User authentication / multi-user sessions |
| Text chunking and embedding via OpenAI | Cloud deployment (AWS / GCP / Azure) |
| Vector storage and retrieval via ChromaDB | Streaming responses |
| Conversational Q&A with chat history | Fine-tuning or custom model training |
| Source attribution per answer | Persistent chat history across server restarts |
| Multi-document support per session | OCR for image-only / scanned PDFs |
| Session clear (docs + chat history) | Document management (list, delete individual docs) |
| React UI — upload panel + chat interface | Mobile / native app |
| Docker + docker-compose deployment | Real-time collaborative sessions |
| REST API with OpenAPI docs | |

### 1.3 Intended Audience
| Audience | How They Use This |
|---|---|
| Developer (Ved / engineer) | Build system features per these specifications |
| QA | Derive test cases from FRs + acceptance criteria |
| Owner (openclaw-control-ui) | Validate that specifications match intended product |

### 1.4 References
| Document | Location |
|---|---|
| L1 Plan (atomic task breakdown) | `docs/l1_plan_v1.md` in ragchatbot repo |
| Requirements (FR/NFR/TR) | `projects/beta-test/delivery/requirements_v1.md` |
| GitHub Repo | https://github.com/harshi12musigma-stack/ragchatbot |

### 1.5 Terminology
| Term | Definition |
|---|---|
| "Shall" | Mandatory — system MUST implement this |
| "Should" | Strongly recommended |
| "May" | Optional / desirable |
| System | The RAG Chatbot application (backend + frontend) |
| User | The single human operator interacting with the app (Phase 1 — no auth) |
| Document | Any uploaded file (PDF, DOCX, or TXT) |
| Chunk | A text segment produced by splitting a document |
| Embedding | A numerical vector representation of a chunk |
| Collection | The ChromaDB container holding all embedded chunks |
| Session | A runtime instance — from app start to `/clear` or server restart |

---

## 2. System Overview

### 2.1 System Description
The RAG Chatbot is a locally-deployed web application that allows a user to upload one or more documents, then ask natural language questions about their content. The system uses retrieval-augmented generation (RAG) to ground answers in the uploaded documents, with source attribution per answer and full conversational context across follow-up questions.

**Stack:** Python 3.11 + FastAPI (backend) · React 18 + Vite + TailwindCSS (frontend) · LangChain (RAG orchestration) · ChromaDB (vector store) · OpenAI GPT-4o (LLM) · OpenAI `text-embedding-3-small` (embeddings) · Docker + docker-compose (deployment)

### 2.2 System Context
| External Entity | Direction | Description |
|---|---|---|
| User (browser) | → Frontend | Uploads files, sends questions, reads answers |
| Frontend (React) | ↔ Backend (FastAPI) | REST API calls: `/upload`, `/ask`, `/clear`, `/health` |
| Backend (FastAPI) | → OpenAI Embeddings API | Sends text chunks, receives embedding vectors |
| Backend (FastAPI) | → OpenAI Chat API | Sends prompt + retrieved context, receives answer |
| Backend (FastAPI) | ↔ ChromaDB | Upserts and queries embedding vectors + metadata |
| ChromaDB | ↔ Local Disk | Persists collection to `./chroma_db/` directory |

### 2.3 User Roles
| Role | Description | Permissions |
|---|---|---|
| Operator (single user, Phase 1) | The person running the app locally | Full access — upload, ask, clear, view all sources |

*(No auth, no role differentiation in Phase 1)*

---

## 3. Functional Decomposition

```
RAG Chatbot
├── Module 1: Document Management
│   ├── F1.1 — File Upload & Validation
│   ├── F1.2 — Document Parsing (text extraction)
│   ├── F1.3 — Text Chunking
│   ├── F1.4 — Embedding & Vector Storage
│   └── F1.5 — Session Clear
│
├── Module 2: Question Answering
│   ├── F2.1 — Question Input & Validation
│   ├── F2.2 — Chat History Management
│   ├── F2.3 — Question Condensation (follow-ups)
│   ├── F2.4 — Vector Retrieval
│   ├── F2.5 — LLM Answer Generation
│   └── F2.6 — Source Attribution
│
├── Module 3: User Interface
│   ├── F3.1 — Upload Panel
│   ├── F3.2 — Chat Window
│   ├── F3.3 — Source Attribution Display
│   └── F3.4 — Session Controls
│
└── Module 4: Infrastructure & Operations
    ├── F4.1 — Health Check
    ├── F4.2 — API Documentation
    ├── F4.3 — Error Handling
    └── F4.4 — Environment Configuration
```

---

## 4. Detailed Functional Requirements

---

### Module 1 — Document Management

#### F1.1 — File Upload & Validation

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.1.1 | The system shall accept file uploads via `POST /upload` as `multipart/form-data` | Must | Endpoint accepts `.pdf`, `.docx`, `.txt` files and returns 200 with upload metadata |
| FR-1.1.2 | The system shall validate file type by extension before processing | Must | `.exe`, `.zip`, `.jpg`, and any unsupported extension returns 400 `{"error": "Unsupported file type", "detail": "Allowed: pdf, docx, txt"}` |
| FR-1.1.3 | The system shall reject files exceeding 50MB | Must | File >50MB returns 413 `{"error": "File too large", "detail": "Max size: 50MB"}` |
| FR-1.1.4 | The system shall assign a unique `doc_id` (UUID4 short hex) to each uploaded document | Must | Response includes `doc_id` field; two uploads of same file produce different `doc_id` values |
| FR-1.1.5 | The system shall return upload metadata in the response | Must | Response body: `{status, doc_id, filename, chunk_count, elapsed_ms}` |
| FR-1.1.6 | The system shall handle duplicate uploads (same file re-uploaded) by replacing existing chunks | Must | Re-uploading same file deletes all existing chunks with matching `doc_id` prefix before inserting new ones |

#### F1.2 — Document Parsing

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.2.1 | The system shall extract text from PDF files using PyMuPDF | Must | PDF with 5 pages → text extracted from all pages with page number metadata preserved |
| FR-1.2.2 | The system shall extract text from DOCX files using python-docx | Must | DOCX with headings, paragraphs, and tables → full text extracted |
| FR-1.2.3 | The system shall extract text from TXT files directly | Must | Plain text file → content read as UTF-8 |
| FR-1.2.4 | The system shall return 400 if no text can be extracted from an uploaded file | Must | Image-only PDF (no text layer) → 400 `{"error": "No text could be extracted from this document"}` |
| FR-1.2.5 | The system shall preserve page number metadata during PDF extraction | Must | Each extracted chunk includes `page` field matching source page number |

#### F1.3 — Text Chunking

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.3.1 | The system shall split extracted text using LangChain RecursiveCharacterTextSplitter | Must | Output is a list of Document objects with text content and metadata |
| FR-1.3.2 | Chunk size shall be 1000 characters | Must | No individual chunk exceeds 1000 characters |
| FR-1.3.3 | Chunk overlap shall be 200 characters | Must | Last 200 characters of chunk N appear at the start of chunk N+1 |
| FR-1.3.4 | Each chunk shall carry metadata: `doc_id`, `filename`, `page`, `chunk_index`, `upload_timestamp` | Must | ChromaDB entry for every chunk has all 5 metadata fields populated |

#### F1.4 — Embedding & Vector Storage

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.4.1 | The system shall embed each chunk using OpenAI `text-embedding-3-small` | Must | Each chunk produces a 1536-dimension vector stored in ChromaDB |
| FR-1.4.2 | The system shall store embeddings in a ChromaDB collection named `ragchatbot_docs` | Must | Collection exists and contains correct number of entries after upload |
| FR-1.4.3 | The system shall use deterministic chunk IDs: `{doc_id}_{chunk_index}` | Must | Re-uploading same content produces same chunk IDs → upsert is idempotent |
| FR-1.4.4 | The ChromaDB collection shall persist to disk at `CHROMA_PERSIST_DIR` | Must | Server restart → collection still contains previously uploaded documents |
| FR-1.4.5 | The system shall log embedding elapsed time per upload | Should | `elapsed_ms` in response reflects actual time from file receipt to ChromaDB confirm |

#### F1.5 — Session Clear

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.5.1 | The system shall delete all chunks from ChromaDB collection on `POST /clear` | Must | After `/clear`, ChromaDB collection is empty |
| FR-1.5.2 | The system shall recreate the empty collection immediately after deletion | Must | Subsequent `/upload` call succeeds without server restart |
| FR-1.5.3 | The system shall return confirmation on successful clear | Must | Response: `{status: "success", message: "All documents cleared"}` |

---

### Module 2 — Question Answering

#### F2.1 — Question Input & Validation

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.1.1 | The system shall accept questions via `POST /ask` with body `{question: str, chat_history: [...]}` | Must | Valid request with non-empty question returns 200 with answer |
| FR-2.1.2 | The system shall reject empty or whitespace-only questions | Must | Blank question returns 400 `{"error": "Question cannot be empty"}` |
| FR-2.1.3 | The system shall return 400 if no documents are uploaded when a question is asked | Must | `/ask` with empty ChromaDB collection returns 400 `{"error": "No documents uploaded yet. Please upload a document first."}` |

#### F2.2 — Chat History Management

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.2.1 | The system shall accept chat history as a list of `{role: "human"\|"assistant", content: str}` objects | Must | Chat history of 10 prior turns is accepted without error |
| FR-2.2.2 | The system shall pass chat history to LangChain in the correct message format | Must | LangChain ConversationBufferMemory receives correctly typed HumanMessage / AIMessage objects |
| FR-2.2.3 | Chat history shall be held client-side (not persisted on the server) | Must | Server restart resets to empty history; frontend maintains history in component state |

#### F2.3 — Question Condensation

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.3.1 | The system shall condense follow-up questions using chat history before retrieval | Must | "Can you elaborate on that?" with prior context → condensed to a self-contained query before vector search |
| FR-2.3.2 | Condensation shall use LangChain's built-in ConversationalRetrievalChain condense step | Must | Chain logs show condensed question used for retrieval (not raw follow-up text) |

#### F2.4 — Vector Retrieval

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.4.1 | The system shall retrieve the top 4 most semantically similar chunks for each question | Must | `sources` list in response contains exactly 4 entries (or fewer if collection has <4 chunks) |
| FR-2.4.2 | Retrieval shall use ChromaDB cosine similarity search | Must | Returned chunks are semantically relevant to the question |
| FR-2.4.3 | Retrieved chunks shall include full metadata: `filename`, `page`, `chunk_index`, `chunk_text` | Must | Every entry in `sources` has all 4 fields populated |

#### F2.5 — LLM Answer Generation

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.5.1 | The system shall generate answers using OpenAI GPT-4o | Must | Non-empty answer string returned for any valid question with relevant context |
| FR-2.5.2 | The system shall ground answers in retrieved chunks only — not general knowledge | Must | Answer does not introduce facts not present in the retrieved chunks (manual review) |
| FR-2.5.3 | The system shall return 502 if OpenAI API is unavailable | Must | Simulated OpenAI failure returns 502 `{"error": "LLM service unavailable", "detail": "OpenAI API error: ..."}` |

#### F2.6 — Source Attribution

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.6.1 | The system shall return source chunks alongside every answer | Must | `sources` field present in every `/ask` 200 response |
| FR-2.6.2 | Each source entry shall include: `filename`, `page`, `chunk_index`, `chunk_text` (first 300 chars) | Must | All 4 fields present and non-null in every source entry |
| FR-2.6.3 | Source `filename` shall match the original uploaded filename exactly | Must | Source filename for a file uploaded as `contract.pdf` is `contract.pdf`, not an ID or path |

---

### Module 3 — User Interface

#### F3.1 — Upload Panel

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-3.1.1 | The system shall provide a drag-and-drop file upload zone | Must | User can drag a file onto the zone and trigger upload without clicking a button |
| FR-3.1.2 | The system shall allow click-to-browse file selection | Must | Clicking the upload zone opens the OS file picker |
| FR-3.1.3 | The system shall display upload status per file: uploading / success / error | Must | File appears in list with a spinner (uploading), green tick (success), or red message (error) |
| FR-3.1.4 | The system shall display the filename and chunk count after successful upload | Must | Uploaded file shows: `contract.pdf — 42 chunks` |
| FR-3.1.5 | The system shall display an inline error message for rejected files | Must | Uploading `.exe` shows: "Unsupported file type. Allowed: PDF, DOCX, TXT" |

#### F3.2 — Chat Window

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-3.2.1 | The system shall display a scrollable conversation thread | Must | Thread auto-scrolls to latest message; older messages remain visible by scrolling up |
| FR-3.2.2 | The system shall provide a text input field and a Send button | Must | User types question and clicks Send (or presses Enter) to submit |
| FR-3.2.3 | The system shall display a loading indicator while awaiting an answer | Must | Spinner or typing indicator shown between question submission and answer arrival |
| FR-3.2.4 | User messages shall be visually distinct from assistant messages | Must | User = right-aligned blue bubble; Assistant = left-aligned grey bubble |
| FR-3.2.5 | The input field shall be disabled while a request is in flight | Must | User cannot submit a second question before the first answer arrives |
| FR-3.2.6 | The system shall display an inline error in the chat if `/ask` returns an error | Must | API error → error message appears in the thread in red, input re-enabled |

#### F3.3 — Source Attribution Display

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-3.3.1 | The system shall display source chunks below each assistant answer | Must | Each answer has a collapsible "Sources" section |
| FR-3.3.2 | Each source entry shall show: filename, page number, and a text excerpt | Must | Source card shows: `📄 contract.pdf — Page 3` + first 300 chars of chunk |
| FR-3.3.3 | The Sources section shall be collapsed by default and expandable on click | Should | Click "Show sources (4)" → expands to show all source cards |

#### F3.4 — Session Controls

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-3.4.1 | The system shall provide a "Clear Session" button in the header | Must | Button visible at all times, not just after upload |
| FR-3.4.2 | Clicking "Clear Session" shall call `/clear`, then reset chat history and uploaded docs list in UI | Must | After clear: chat thread empty, upload list empty, question input disabled until new upload |
| FR-3.4.3 | The system shall ask for confirmation before clearing | Should | Confirmation dialog: "This will remove all uploaded documents and chat history. Continue?" |

---

### Module 4 — Infrastructure & Operations

#### F4.1 — Health Check

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-4.1.1 | The system shall expose `GET /health` returning `{status: "ok"}` | Must | Returns 200 `{"status": "ok"}` with no auth required |

#### F4.2 — API Documentation

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-4.2.1 | The system shall auto-generate OpenAPI docs at `GET /docs` | Must | FastAPI Swagger UI accessible at `http://localhost:8000/docs` |
| FR-4.2.2 | All endpoints shall have description, request schema, and response schema in OpenAPI spec | Must | `/upload`, `/ask`, `/clear`, `/health` all documented with example request/response |

#### F4.3 — Error Handling

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-4.3.1 | All API errors shall return structured JSON: `{error: str, detail: str, status_code: int}` | Must | No bare HTML error pages or unhandled Python tracebacks reach the client |
| FR-4.3.2 | The system shall return 400 for client errors (invalid input, unsupported type, empty question) | Must | All client-caused failures return 4xx, not 500 |
| FR-4.3.3 | The system shall return 500 for unexpected server errors | Must | Uncaught exception → 500 with generic message, full traceback logged server-side only |
| FR-4.3.4 | The system shall return 502 for downstream API failures (OpenAI) | Must | OpenAI timeout / rate limit → 502, not 500 |
| FR-4.3.5 | The system shall return 413 for oversized file uploads | Must | File >50MB → 413 before reading file bytes into memory |

#### F4.4 — Environment Configuration

| Req. ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-4.4.1 | All configuration shall be via environment variables — no hardcoded values | Must | No API keys, URLs, or paths in source code |
| FR-4.4.2 | The system shall fail fast on startup if `OPENAI_API_KEY` is missing | Must | Starting backend without `OPENAI_API_KEY` → clear startup error, not a runtime crash on first request |
| FR-4.4.3 | `.env.example` shall document all required and optional environment variables | Must | File includes: `OPENAI_API_KEY`, `CHROMA_PERSIST_DIR`, `BACKEND_URL`, `VITE_BACKEND_URL` with descriptions |

---

## 5. Workflow & State Transitions

### 5.1 Document Session Lifecycle

| Current State | Event / Trigger | Next State | System Action |
|---|---|---|---|
| Empty (no docs) | User uploads valid file | Processing | Parse → chunk → embed → store |
| Processing | Ingestion complete | Ready (has docs) | Return upload metadata to UI |
| Processing | Ingestion fails | Error | Return 400/500, no partial data stored |
| Ready | User uploads another file | Processing (multi-doc) | Add new doc chunks to collection |
| Ready | User asks question | Answering | Retrieve → generate → return answer |
| Answering | Answer generated | Ready | Append to chat history, re-enable input |
| Answering | API error | Ready (error state) | Show inline error, re-enable input |
| Ready | User clicks Clear | Empty | Delete collection, recreate, reset UI |

### 5.2 Question Flow

| Step | Action | Component |
|---|---|---|
| 1 | User types question + presses Send | Frontend |
| 2 | Frontend appends question to chat thread, disables input | Frontend |
| 3 | `POST /ask` with `{question, chat_history}` | Frontend → Backend |
| 4 | Validate question (non-empty, collection non-empty) | Backend |
| 5 | Condense follow-up question using chat history | LangChain |
| 6 | Similarity search: top 4 chunks from ChromaDB | LangChain → ChromaDB |
| 7 | Build prompt: system instructions + retrieved chunks + condensed question | LangChain |
| 8 | Call GPT-4o with prompt | LangChain → OpenAI |
| 9 | Return `{answer, sources}` | Backend → Frontend |
| 10 | Append answer + sources to chat thread, re-enable input | Frontend |

---

## 6. Business Rules

| Rule ID | Business Rule | Logic | Priority |
|---|---|---|---|
| BRL-01 | No question without documents | If ChromaDB collection is empty → reject `/ask` with 400 | Must |
| BRL-02 | Answers grounded in documents only | LLM prompt instructs: "Answer only from the provided context. If not found, say so." | Must |
| BRL-03 | One active session | No per-user session isolation — all uploads go to the same collection (Phase 1) | Must |
| BRL-04 | Duplicate upload replaces, not appends | Re-uploading same file deletes existing chunks by `doc_id` before inserting new | Must |
| BRL-05 | Clear is irreversible | `/clear` deletes all chunks — no undo, no soft delete | Must |
| BRL-06 | File type by extension only | No MIME type sniffing — validate by file extension | Must |

---

## 7. Error Handling & Validation

### 7.1 Input Validation Rules

| Field | Rule | Error Response |
|---|---|---|
| Upload file extension | Must be `.pdf`, `.docx`, or `.txt` | 400 `{"error": "Unsupported file type", "detail": "Allowed: pdf, docx, txt"}` |
| Upload file size | Must be ≤ 50MB | 413 `{"error": "File too large", "detail": "Max size: 50MB"}` |
| Question string | Must be non-empty, non-whitespace | 400 `{"error": "Question cannot be empty"}` |
| chat_history | Must be a list of `{role, content}` objects | 422 FastAPI validation error |

### 7.2 System Error Handling

| Scenario | Behaviour | User-Facing Message | Logged |
|---|---|---|---|
| No text extractable from PDF | Return 400, no ChromaDB write | "No text could be extracted from this document" | Warning |
| OpenAI API rate limit | Return 502 | "LLM service temporarily unavailable. Try again." | Error |
| OpenAI API invalid key | Return 502 | "LLM service configuration error. Contact admin." | Critical |
| ChromaDB write failure | Return 500, rollback partial insert | "Document storage failed. Please try again." | Error |
| ChromaDB collection not found on query | Return 400 | "No documents uploaded yet." | Info |
| Unexpected server error | Return 500 | "An unexpected error occurred." (no traceback) | Error (full traceback server-side) |

---

## 8. Use Cases

### UC-01 — Upload and Query a Single Document

| Field | Details |
|---|---|
| **Use Case ID** | UC-01 |
| **Name** | Upload and query a single document |
| **Actor** | Operator |
| **Pre-conditions** | App is running; no documents currently uploaded |
| **Trigger** | User drags a PDF onto the upload zone |
| **Main Flow** | 1. User drags PDF onto upload zone → 2. Frontend calls `POST /upload` → 3. System parses, chunks, embeds, stores → 4. UI shows "contract.pdf — 42 chunks" → 5. User types question → 6. System retrieves top 4 chunks → 7. GPT-4o generates answer → 8. UI shows answer + sources |
| **Alternate Flow** | File rejected: step 2 returns 400 → UI shows inline error, no upload recorded |
| **Exception Flow** | OpenAI unavailable at step 7 → UI shows "LLM service unavailable", input re-enabled |
| **Post-conditions** | Document chunks stored in ChromaDB; answer + sources visible in chat thread |
| **Related FRs** | FR-1.1.1–1.5.3, FR-2.1.1–2.6.3, FR-3.1.1–3.3.3 |

### UC-02 — Ask a Follow-Up Question

| Field | Details |
|---|---|
| **Use Case ID** | UC-02 |
| **Name** | Ask a follow-up question using chat history |
| **Actor** | Operator |
| **Pre-conditions** | At least one document uploaded; at least one prior question/answer in chat thread |
| **Trigger** | User types "Can you give me more detail on that?" |
| **Main Flow** | 1. Frontend sends `{question: "Can you give me more detail on that?", chat_history: [...]}` → 2. LangChain condenses to a self-contained query → 3. Condensed query used for ChromaDB retrieval → 4. Answer contextually continues prior conversation |
| **Exception Flow** | Chat history malformed → 422 validation error |
| **Post-conditions** | Answer is contextually coherent with prior conversation |
| **Related FRs** | FR-2.2.1–2.3.2 |

### UC-03 — Upload Multiple Documents and Query Across Them

| Field | Details |
|---|---|
| **Use Case ID** | UC-03 |
| **Name** | Multi-document cross-query |
| **Actor** | Operator |
| **Pre-conditions** | App running with empty collection |
| **Trigger** | User uploads two documents, then asks a question spanning both |
| **Main Flow** | 1. Upload doc A → success → 2. Upload doc B → success → 3. Ask question spanning both → 4. Retrieval returns chunks from both docs → 5. Answer synthesises across both |
| **Exception Flow** | One upload fails → other doc still queryable |
| **Post-conditions** | Sources panel shows chunks from both documents |
| **Related FRs** | FR-1.1.1–1.4.5, FR-2.4.1–2.6.3 |

### UC-04 — Clear Session

| Field | Details |
|---|---|
| **Use Case ID** | UC-04 |
| **Name** | Clear all documents and reset session |
| **Actor** | Operator |
| **Pre-conditions** | One or more documents uploaded; chat history present |
| **Trigger** | User clicks "Clear Session" button |
| **Main Flow** | 1. Confirmation dialog shown → 2. User confirms → 3. Frontend calls `POST /clear` → 4. ChromaDB collection deleted and recreated → 5. UI resets: empty chat thread, empty upload list, input disabled |
| **Alternate Flow** | User cancels confirmation → no action taken |
| **Post-conditions** | ChromaDB empty; UI state reset; new upload will start fresh |
| **Related FRs** | FR-1.5.1–1.5.3, FR-3.4.1–3.4.3 |

---

## 9. User Stories

| Story ID | User Story | Acceptance Criteria | Related FRs | Priority |
|---|---|---|---|---|
| US-001 | As an operator, I want to upload a PDF so that I can ask questions about it | Given a valid PDF ≤50MB, When I drag it to the upload zone, Then I see the filename + chunk count and can start asking questions | FR-1.1.1–1.4.5 | Must |
| US-002 | As an operator, I want to ask a question about my document so that I get a grounded answer with sources | Given a document is uploaded, When I type a question and press Send, Then I see an answer and the source chunks it came from | FR-2.1.1–2.6.3 | Must |
| US-003 | As an operator, I want to ask follow-up questions so that I can explore a topic iteratively | Given a prior Q&A turn, When I ask "Can you elaborate?", Then the answer continues coherently using context from my previous question | FR-2.2.1–2.3.2 | Must |
| US-004 | As an operator, I want to see which part of the document the answer came from so that I can verify it | Given an answer is returned, When I look at the Sources section, Then I see filename, page number, and text excerpt for each source chunk | FR-2.6.1–2.6.3, FR-3.3.1–3.3.3 | Must |
| US-005 | As an operator, I want to upload multiple documents so that I can ask questions across all of them | Given 2+ documents are uploaded, When I ask a cross-document question, Then the answer draws from both and sources show which came from where | FR-1.1.6, FR-2.4.1–2.4.3 | Must |
| US-006 | As an operator, I want to clear my session so that I can start fresh with new documents | Given documents and chat history exist, When I click Clear Session and confirm, Then the collection is empty and the UI is reset | FR-1.5.1–1.5.3, FR-3.4.1–3.4.3 | Must |
| US-007 | As an operator, I want the app to tell me when I try to upload an unsupported file so that I understand why it failed | Given I drag a `.zip` onto the upload zone, When the upload is rejected, Then I see a clear error message with allowed file types | FR-1.1.2, FR-3.1.5 | Must |
| US-008 | As an operator, I want to run the whole app with one command so that setup is frictionless | Given I have Docker and an `.env` file, When I run `docker-compose up --build`, Then both frontend and backend start and the app is usable | FR (deployment) | Must |

---

## 10. Data Requirements

### 10.1 Data Dictionary

| Entity | Attribute | Type | Nullable | Description |
|---|---|---|---|---|
| Document | `doc_id` | string (UUID4 short) | No | Unique identifier assigned at upload |
| Document | `filename` | string | No | Original filename as uploaded |
| Document | `upload_timestamp` | ISO 8601 string | No | UTC timestamp of upload |
| Chunk | `chunk_id` | string (`{doc_id}_{chunk_index}`) | No | Deterministic unique ID per chunk |
| Chunk | `chunk_text` | string (max 1000 chars) | No | Raw text content of the chunk |
| Chunk | `chunk_index` | integer | No | 0-based position of chunk within document |
| Chunk | `page` | integer | No | Source page number (1-based; 1 for TXT/DOCX) |
| Chunk | `embedding` | float[1536] | No | OpenAI text-embedding-3-small vector |
| Message | `role` | enum: "human" \| "assistant" | No | Who sent the message |
| Message | `content` | string | No | Message text |

### 10.2 Data Storage

| Data | Where Stored | Persistence |
|---|---|---|
| Chunk embeddings + metadata | ChromaDB (`CHROMA_PERSIST_DIR/ragchatbot_docs`) | Persists across server restarts |
| Chat history | React component state (client-side) | Resets on page refresh or server restart |
| Uploaded file bytes | Not stored — processed in memory only | Not persisted after ingestion |

### 10.3 Data Retention
| Data | Retention Rule |
|---|---|
| ChromaDB collection | Persists until `/clear` is called |
| Chat history (client-side) | Until page refresh or clear |
| Uploaded file bytes | Never persisted — streamed in memory during ingestion only |

---

## 11. External Interface Requirements

| Interface | System | Direction | Protocol | Auth | Key Operations |
|---|---|---|---|---|---|
| INT-01 | OpenAI Embeddings API | Backend → OpenAI | HTTPS / REST | API Key (`OPENAI_API_KEY`) | Embed text chunks |
| INT-02 | OpenAI Chat API | Backend → OpenAI | HTTPS / REST | API Key (`OPENAI_API_KEY`) | Generate answers |
| INT-03 | ChromaDB | Backend ↔ ChromaDB | In-process (embedded) | None | Upsert, query, delete collection |
| INT-04 | Frontend ↔ Backend | React → FastAPI | HTTP / REST | None (Phase 1) | `/upload`, `/ask`, `/clear`, `/health` |

---

## 12. Traceability Matrix

| User Story | FR(s) | Use Case | Endpoint |
|---|---|---|---|
| US-001 (Upload PDF) | FR-1.1.1–1.4.5 | UC-01 | `POST /upload` |
| US-002 (Ask question) | FR-2.1.1–2.6.3 | UC-01 | `POST /ask` |
| US-003 (Follow-up) | FR-2.2.1–2.3.2 | UC-02 | `POST /ask` |
| US-004 (Source attribution) | FR-2.6.1–2.6.3, FR-3.3.1–3.3.3 | UC-01 | `POST /ask` (response) |
| US-005 (Multi-document) | FR-1.1.6, FR-2.4.1–2.4.3 | UC-03 | `POST /upload` + `POST /ask` |
| US-006 (Clear session) | FR-1.5.1–1.5.3, FR-3.4.1–3.4.3 | UC-04 | `POST /clear` |
| US-007 (File validation) | FR-1.1.2–1.1.3, FR-3.1.5 | UC-01 (alt flow) | `POST /upload` |
| US-008 (Docker deploy) | FR-4.1.1–4.4.3 | — | docker-compose |

---

## 13. Open Issues

| ID | Description | Status | Owner |
|---|---|---|---|
| ISS-01 | Confirm whether GPT-4o is available on the OpenAI account being used — fallback to GPT-4o-mini if quota limited | Open | openclaw-control-ui |
| ISS-02 | CHROMA_PERSIST_DIR absolute vs relative path behaviour in Docker volume mount to be confirmed during Phase 5 | Open | Ved |
| ISS-03 | `page` field for DOCX/TXT: no native page concept — define convention (always `1` or paragraph index) | Open | Ved |
| ISS-04 | Max chunk_count per session not defined — ChromaDB performance at >10K chunks not validated | Open | Ved |

---

## 14. Assumptions & Dependencies

| ID | Assumption / Dependency | Impact if Invalid |
|---|---|---|
| FA-01 | User has a valid OpenAI API key with GPT-4o access | App cannot function — all `/ask` calls fail |
| FA-02 | App runs on a machine with Docker and docker-compose installed | docker-compose startup fails |
| FA-03 | Uploaded documents contain extractable text (not image scans) | System returns 400; user must use OCR tool externally |
| FA-04 | Single user — no concurrent session isolation required | Multi-user access would cause collection contamination |
| FA-05 | Network access to `api.openai.com` from the running machine | Embedding and answering fail at API call step |
| FA-06 | Local disk has sufficient space for ChromaDB (`~1MB per 500 chunks`) | ChromaDB write fails for large document sets |

---

## 15. Approval & Sign-Off

| Name | Role | Status |
|---|---|---|
| openclaw-control-ui | Product Owner / BSH | Pending |
| Ved | Technical Lead / Author | Drafted 2026-03-31 |

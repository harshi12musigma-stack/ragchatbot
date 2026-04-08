# RAG Chatbot - Document Q&A Application

A full-stack RAG (Retrieval-Augmented Generation) chatbot that allows users to upload documents and ask natural language questions about them.

## 🎯 Features

- **Document Upload**: Support for PDF, DOCX, TXT, and Markdown files
- **Intelligent Q&A**: Ask questions about uploaded documents and get contextually accurate answers
- **Source Citations**: See which document chunks were used to generate each answer
- **Conversation Memory**: Maintain context across multiple questions
- **Real-time Chat Interface**: Modern, responsive UI with message history

## 🏗️ Architecture

**3-Tier Microservices Architecture**

- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: FastAPI (Python 3.11+)
- **Vector Store**: ChromaDB with OpenAI embeddings
- **LLM**: OpenAI GPT-4o-mini

## 📁 Project Structure

```
ragchatbot/
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── App.jsx         # Main app
│   ├── package.json
│   └── vite.config.js
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core modules (RAG engine, embeddings)
│   │   ├── models/         # Pydantic models
│   │   └── main.py         # FastAPI app entry
│   ├── requirements.txt
│   └── .env.example
│
├── docs/                   # Architecture & design docs
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
CORS_ORIGINS=http://localhost:5173
CHROMA_PERSIST_DIRECTORY=./chroma_data
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload and process a document |
| `/api/chat` | POST | Send a question and get an answer |
| `/api/documents` | GET | List all uploaded documents |
| `/api/documents/{id}` | DELETE | Remove a document |
| `/api/sessions` | GET | List conversation sessions |
| `/api/health` | GET | Health check |

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🛠️ Development

### Code Quality

We use automated linting and formatting:

**Backend (Python)**
- `black` for code formatting
- `flake8` for linting
- `isort` for import sorting

**Frontend (JavaScript)**
- `eslint` for linting
- `prettier` for formatting

Run checks:
```bash
# Backend
cd backend
black . --check
flake8 .

# Frontend
cd frontend
npm run lint
```

### CI/CD

GitHub Actions runs on every PR:
- Linting (black, flake8, eslint)
- Unit tests
- Build verification

## 📚 Documentation

- [Architecture Specification](docs/architecture_spec.md)
- [API Documentation](http://localhost:8000/docs) (when backend is running)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run linting and tests
4. Commit with clear messages
5. Push and open a PR

## 📝 License

MIT

## 👥 Team

- **Project Lead**: Harshita Gupta
- **Development**: Ved (AI Digital Employee)

---

**Status**: Phase 2 - Development & Build ✅


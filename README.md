# 🏛️ AI Law Assistant - Frontend Setup Guide

## Overview
This project consists of:
- **Flask API Backend** (`api.py`) - Handles legal queries and maintains conversation history
- **Streamlit Frontend** (`app_streamlit.py`) - Web UI for interacting with the assistant
- **CLI Version** (`app.py`) - Original command-line interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup (First Time Only)

Build the FAISS index from your PDF documents:

```bash
python build_index.py
```

This creates the search index from all PDFs in the `data/` folder.

### 3. Run the System

#### Option A: Web Interface (HTML + Flask API) ⭐ **Recommended**

**Single Terminal - Start Flask API:**
```bash
python api.py
```
✅ Open browser: `http://localhost:5000`

The API serves both the web interface and handles all legal queries.

#### Option B: CLI Interface (Original)

```bash
python app.py
```

## 🎨 Features

### Web Frontend (HTML + JavaScript)
- ✨ Modern, responsive interface
- 🔄 Conversation history per session
- 📌 Source document tracking with citations
- 🆕 Clear chat or start new session
- 📊 Real-time session management
- ✅ Live API status indicator
- 🎯 Beautiful gradients and smooth animations
- 📱 Fully scrollable message area

### Flask API
- `POST /api/chat` - Send a question and get an answer
- `GET /api/history/<session_id>` - Get conversation history
- `DELETE /api/history/<session_id>` - Clear conversation history
- `GET /api/health` - Check API status

## 🔧 Architecture

### System Infrastructure
```
┌─────────────────────────────────────────────┐
│     Web Frontend (Port 5000)                │
│  - HTML/CSS/JavaScript UI                   │
│  - Session Management                       │
│  - Display Answers & Sources                │
└────────────────┬────────────────────────────┘
                 │ HTTP Requests
                 │
┌────────────────▼────────────────────────────┐
│     Flask API Backend (Port 5000)           │
│  - Question Processing                      │
│  - RAG Pipeline Orchestration               │
│  - Conversation History Management          │
│  - Gemini API Integration                   │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴─────────┐
         │                 │
┌────────▼───┐    ┌────────▼───┐
│ FAISS      │    │  Gemini    │
│ Vector DB  │    │  API       │
└────────────┘    └────────────┘
```

### RAG (Retrieval Augmented Generation) Pipeline
```
User Question
     ↓
Retriever (get relevant sections)
     ↓
Clean context (remove noise)
     ↓
LLM with strong prompt
     ↓
Formatted Markdown output
     ↓
Styled UI (Rendered to user)
```

**Pipeline Details:**
- **Retriever**: FAISS vector database retrieves k=10 most relevant document chunks
- **Context Cleaning**: Removes duplicates, redundant text, and formats document excerpts
- **LLM Processing**: Google Gemini 2.5 Flash processes cleaned context with specialized legal prompt
- **Markdown Formatting**: LLM returns structured markdown with headings, lists, and citations
- **UI Rendering**: Frontend converts markdown to styled HTML with source attribution

## 📝 Usage Examples

### Through Web Frontend ⭐
1. Start API: `python api.py`
2. Open browser → `http://localhost:5000`
3. Type your legal question
4. Get instant answers with source citations
5. Chat history maintained automatically
6. Use sidebar to clear chat or start new session

### Through API Directly

```bash
# Send a question
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "question": "What is Article 370?"
  }'

# Get conversation history
curl http://localhost:5000/api/history/user123

# Clear history
curl -X DELETE http://localhost:5000/api/history/user123
```

## 🚀 Production Deployment

### For Production, Consider:

1. **Database for Conversations** - Replace in-memory storage with PostgreSQL/MongoDB
2. **Authentication** - Add user authentication and API key management
3. **Rate Limiting** - Prevent API abuse with request throttling
4. **Caching** - Cache frequent queries and their responses
5. **Error Logging** - Implement comprehensive logging with monitoring
6. **Gunicorn** - Use Gunicorn instead of Flask development server
7. **HTTPS** - Enable SSL/TLS encryption for security
8. **Reverse Proxy** - Use Nginx to serve static files and proxy API

### Example Production Setup:

```bash
# Install production server
pip install gunicorn

# Run Flask API with Gunicorn (multiple workers)
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Nginx configuration for reverse proxy would handle:
# - Static file serving (index.html, CSS, JS)
# - SSL/TLS termination
# - Request routing to Gunicorn workers
# - Load balancing
```

## 📂 Project Structure

```
D:\Ai_Law_Assist\
├── app.py                 # CLI version (original)
├── api.py                 # Flask API backend + HTML server ⭐
├── index.html             # Web UI (HTML/CSS/JavaScript) ⭐
├── build_index.py         # Build FAISS index
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .env                   # API keys (create this)
├── data/                  # PDF documents folder
├── faiss_index/           # Vector database
│   └── index.faiss
└── __pycache__/
```

## ⚙️ Configuration

### Environment Variables (.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Tuning Parameters (in api.py and app.py)

```python
# Number of documents to retrieve
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Chunk size for document splitting (in build_index.py)
chunk_size=1000
chunk_overlap=200

# Gemini model (can upgrade to gemini-pro)
model="gemini-2.5-flash"
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Cannot connect to API"** | Make sure `python api.py` is running |
| **"GEMINI_API_KEY not found"** | Create `.env` file with your API key |
| **"FAISS index not found"** | Run `python build_index.py` first |
| **Slow responses** | Reduce `k` in retriever or upgrade API key |
| **Inaccurate answers** | Ensure PDFs are in `data/` folder and rebuild index |

## 📚 Files Explanation

| File | Purpose |
|------|---------|
| `app.py` | CLI chatbot (original version) |
| `api.py` | Flask REST API backend + serves HTML UI |
| `index.html` | Web UI frontend (HTML/CSS/JavaScript) |
| `build_index.py` | FAISS index builder from PDFs |
| `requirements.txt` | Dependencies list |

## 🎯 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Build index: `python build_index.py`
3. ✅ Start API server: `python api.py`
4. ✅ Open browser: `http://localhost:5000`
5. ✅ Start asking legal questions!

## 💡 Tips

- **Session Persistence**: Each browser session gets a unique ID maintained in localStorage
- **History Management**: Clear chat to reset conversation for current session
- **Sources Tracking**: All answers include document citations showing which laws/sections were referenced
- **API Reuse**: Other applications can call the REST API at `http://localhost:5000/api/chat`
- **Scrollability**: Messages area is fully scrollable to read long legal responses
- **Real-time Status**: API connection status visible in sidebar

## 📞 Support

For issues or improvements:
- Check Flask API logs in terminal for backend errors
- Open browser console (F12) for frontend errors
- Verify `.env` file has correct `GEMINI_API_KEY`
- Ensure `faiss_index/` exists (run `build_index.py` if missing)
- Check that PDF documents are in `data/` folder

---

**Enjoy your AI Law Assistant! 🏛️⚖️**

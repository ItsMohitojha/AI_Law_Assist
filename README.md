# 🏛️ AI Law Assistant

An AI-powered legal assistant for Indian law, built with a RAG (Retrieval Augmented Generation) pipeline. Ask questions about the Indian Constitution, IPC, BNS, Contract Act, and more — get accurate, cited answers from actual legal text.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Build the FAISS Index (First Time Only)

```bash
python build_index.py
```

This creates the vector search index from all PDFs in `data/raw/`.

### 4. Run

```bash
python api.py
```

Open browser → `http://localhost:5000`

## 🎨 Features

- ✨ Cinematic hero section with animated scales → morphs into chat interface
- 🔄 Real-time SSE streaming responses
- 📌 Source document tracking with legal citations
- 🌙 Dark/light mode toggle
- 📊 Session-based conversation memory
- ✅ Live API health indicator
- 📱 Responsive design

## 🔧 Architecture

```
┌───────────────────────────────────────────────┐
│     Web Frontend (index.html)                 │
│  - Cinematic hero → chat transition           │
│  - SSE streaming, dark/light mode             │
│  - Served by Flask at http://localhost:5000    │
└────────────────┬──────────────────────────────┘
                 │ HTTP (REST + SSE)
┌────────────────▼──────────────────────────────┐
│     Flask API Backend (api.py)                │
│  - POST /api/chat/stream  → SSE streaming     │
│  - POST /api/chat         → non-streaming     │
│  - GET  /api/health       → status check      │
│  - GET  /api/history/:id  → conversation      │
│  - DELETE /api/history/:id→ clear history      │
└────────┬──────────────────┬───────────────────┘
         │                  │
  ┌──────▼──────┐   ┌──────▼──────┐
  │ FAISS Vector│   │ Google      │
  │ Store       │   │ Gemini API  │
  │ (local)     │   │ (remote)    │
  └─────────────┘   └─────────────┘
```

### RAG Pipeline (per query)
1. User sends question via chat UI
2. FAISS retriever finds top-3 most relevant document chunks
3. Chunks cleaned and truncated (remove markdown noise, page numbers)
4. System prompt + question + context → Gemini 2.5 Flash Lite
5. Response streamed word-by-word via SSE
6. Frontend renders markdown in real-time

## 📂 Project Structure

```
D:\Ai_Law_Assist\
├── api.py                 # Flask API backend + HTML server
├── index.html             # Web UI (HTML/CSS/JavaScript)
├── build_index.py         # Build FAISS index from PDFs
├── requirements.txt       # Python dependencies
├── hero_bg.png            # Hero background image
├── .env                   # API key (create this)
├── data/
│   ├── raw/               # Legal PDFs (9 categories, 14 PDFs)
│   └── processed/         # Extraction pipeline output
├── scripts/
│   └── extract_text.py    # Phase 1: PDF text extraction
├── faiss_index/           # Vector database (rebuild with build_index.py)
├── Frontend/
│   ├── DESIGN.md          # Design system reference
│   ├── theme.css          # Tailwind v4 design tokens
│   ├── variables.css      # CSS custom properties
│   └── tokens.json        # Design tokens (JSON)
└── .agents/               # Agent protocol
```

## 📚 Legal Corpus

14 PDFs across 9 categories:

| Category | Acts |
|----------|------|
| Constitutional | Constitution of India |
| Criminal | BNS 2023, BNSS 2023, BSA 2023, IPC, Prevention of Corruption Act |
| Civil | Code of Civil Procedure, Indian Contract Act |
| Consumer | Consumer Protection Act 2019 |
| Cyber | Information Technology Act 2000 |
| Labor | Industrial Disputes Act |
| Transport | Motor Vehicles Act 1988 |
| Education | UGC Regulations |
| Women Protection | Protection of Women from Domestic Violence Act |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Cannot connect to API"** | Make sure `python api.py` is running |
| **"GEMINI_API_KEY not found"** | Create `.env` file with your API key |
| **"FAISS index not found"** | Run `python build_index.py` first |
| **Slow responses** | Reduce `k` in retriever or check API quota |

## 🚀 Production Deployment

For production, consider:
- **Gunicorn** instead of Flask dev server: `gunicorn -w 4 -b 0.0.0.0:5000 api:app`
- **Nginx** reverse proxy for static files and SSL
- **Database** for conversation persistence (replace in-memory dict)
- **Authentication** and rate limiting

---

**Built with Flask, FAISS, Google Gemini, and ⚖️**

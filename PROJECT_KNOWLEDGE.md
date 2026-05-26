# 🏛️ AI Law Assistant — Project Knowledge Base
> **Last updated:** 2026-05-26  
> **Updated by:** Antigravity Agent  
> **Project root:** `D:\Ai_Law_Assist`

**READ THIS FIRST.** This file is the single source of truth for the entire project. Every agent session should read this before doing anything. Every agent should update the relevant sections after making changes.

---

## 1. Architecture Overview

```
┌───────────────────────────────────────────────────┐
│          Web Frontend (index.html)                │
│   - Cinematic hero with animated scales button    │
│   - Chat UI with sidebar + message feed           │
│   - Dark/light mode toggle                        │
│   - SSE streaming for real-time responses         │
│   - Tailwind CSS CDN + custom CSS tokens          │
│   - Marked.js for markdown → HTML rendering       │
│   - Served by Flask at http://localhost:5000       │
└────────────────────┬──────────────────────────────┘
                     │ HTTP (REST + SSE)
                     │
┌────────────────────▼──────────────────────────────┐
│          Flask API Backend (api.py)               │
│   - POST /api/chat         → non-streaming reply  │
│   - POST /api/chat/stream  → SSE streaming reply  │
│   - GET  /api/health       → {"status": "ok"}     │
│   - GET  /api/history/:id  → conversation history │
│   - DELETE /api/history/:id→ clear history        │
│   - GET  /                 → serves index.html    │
│   - GET  /demo             → transition demo page │
│   - In-memory conversation store (dict)           │
│   - Runs on 0.0.0.0:5000 (threaded, no reloader) │
└──────────┬────────────────────┬───────────────────┘
           │                    │
   ┌───────▼───────┐   ┌───────▼───────┐
   │  FAISS Vector │   │  Google Gemini │
   │  Store        │   │  API           │
   │  (local)      │   │  (remote)      │
   │               │   │                │
   │  Model:       │   │  Model:        │
   │  all-MiniLM   │   │  gemini-2.5    │
   │  -L6-v2       │   │  -flash-lite   │
   └───────────────┘   └────────────────┘
```

### RAG Pipeline (per query)
1. User sends question via chat UI
2. Flask receives POST to `/api/chat/stream`
3. Hybrid retrieval fetches candidates: 15 dense candidates via FAISS, 15 sparse candidates via BM25
4. Candidates are deduplicated by `chunk_id` (fallback to content string).
5. Candidates are reranked using `CrossEncoder` (`ms-marco-MiniLM-L-6-v2`), top-3 selected.
6. Context is built without truncating character limits.
7. System prompt + question + cleaned context → sent to Gemini 2.5 Flash Lite
8. Response streamed word-by-word via SSE (URL-encoded words)
9. Frontend decodes + renders markdown in real-time
10. Conversation stored in-memory per `session_id`

---

## 2. File Semantics

### Root Files

| File | Purpose | Key Details |
|------|---------|-------------|
| `api.py` | **Main Flask backend** (362 lines) | Serves HTML, handles chat (streaming + non-streaming), RAG pipeline, conversation memory. Uses `google-genai` client directly. Model: `gemini-2.5-flash-lite`. Hybrid retrieval ($K_{dense}=15, K_{sparse}=15$) with `CrossEncoder` (`ms-marco-MiniLM-L-6-v2`) reranking to top $k=3$. Features pure-python `BM25Retriever`. |
| `build_index.py` | **FAISS index builder** (77 lines) | Loads JSON chunks from `data/processed/chunks/`, maps metadata including `chunk_id` and `raw_content`, builds FAISS index, saves to `faiss_index/`. |
| `index.html` | **Main web UI** (2068 lines) | Single-file HTML/CSS/JS app. Cinematic hero section with animated scales button → morphs into search dock → transitions to chat view. Full chat UI with sidebar, welcome state, message feed, typing indicators. Dark/light mode. Uses Tailwind CDN + custom CSS variables. |
| `requirements.txt` | **Dependencies** | google-genai, langchain, langchain-community, langchain-text-splitters, langchain-huggingface, sentence-transformers, faiss-cpu, python-dotenv, flask, flask-cors, huggingface-hub |
| `README.md` | **Setup guide** | Installation, architecture diagrams, API reference, troubleshooting |
| `.env` | **API key** | Contains `GEMINI_API_KEY` (Gemini API key) |
| `hero_bg.png` | **Hero background image** | 589KB PNG, also duplicated in `static/` |

### `Frontend/` Directory

| File | Purpose |
|------|---------|
| `DESIGN.md` | **Full design system reference** (382 lines). "General Intelligence Company" style. Defines all color tokens, typography (PPMondwest + af fonts), spacing scale, border radii, shadows, component patterns (Ghost Button, Solid Dark Button, Outlined Action, etc.), do's/don'ts, CSS custom properties, Tailwind v4 theme config. |
| `theme.css` | **Tailwind v4 `@theme` block** with all design tokens |
| `variables.css` | **CSS `:root` custom properties** — same tokens as theme.css but as standard CSS variables |
| `tokens.json` | **Design tokens as JSON** (10.7KB) |
| `CinematicTransition.jsx` | **React component** (13KB) for the hero→chat transition. NOT currently used in production (index.html has its own vanilla JS implementation). Exists as a reference/prototype. |
| `transition_demo.html` | **Standalone demo** of the cinematic transition. Served at `/demo` route. |

### `data/` Directory (Legal PDFs)

| File | Size |
|------|------|
| `Bharatiya_nyay_sanhinta.pdf` | 1.3MB |
| `constitution.pdf` | 2.4MB |
| `ipc.pdf` | 1.1MB |
| `motor_vehicle_act.pdf` | 1.2MB |
| `ugc_regulations.pdf` | 282KB |

### `faiss_index/` Directory

| File | Purpose |
|------|---------|
| `index.faiss` | FAISS vector index (3.3MB) |
| `index.pkl` | Pickled metadata for chunks (2.8MB) |

### `scratch/` Directory (Test Scripts)

| File | Purpose |
|------|---------|
| `test_api.py` | Basic API endpoint test |
| `test_api_mock_streaming.py` | Mock streaming test |
| `test_api_responses.py` | API response format test |
| `test_api_streaming.py` | Real streaming endpoint test |
| `test_faiss.py` | FAISS loading test |
| `test_faiss_retrieval.py` | FAISS retrieval quality test |
| `test_gemini.py` | Direct Gemini API test |
| `test_new_prompt.py` | System prompt testing |
| `test_url_encoding.py` | URL encoding verification |

---

## 3. Design System Summary

**Theme:** "Architectural Night Sky" — sophisticated, minimal, dark hero / light chat UI.

### Color Palette
| Token | Hex | Usage |
|-------|-----|-------|
| `--color-night-sky` | `#1f1f29` | Hero bg, dark elements, user message bubbles |
| `--color-cofounder-blue` | `#0081c0` | Primary accent, send button, links |
| `--color-action-azure` | `#41a1cf` | Interactive borders, focus rings |
| `--color-canvas-white` | `#ffffff` | Main chat bg, input bg |
| `--color-off-white` | `#fefffc` | Bot bubble bg, sidebar bg |
| `--color-ash-gray` | `#f9faf7` | Input area bg, subtle surfaces |
| `--color-steel-gray` | `#dee2de` | Borders, dividers |
| `--color-dark-charcoal` | `#171717` | Primary text |
| `--color-charcoal` | `#2c2c2c` | Secondary text, headings |
| `--color-medium-gray` | `#646464` | Muted/helper text |
| `--color-light-gray` | `#b4b8b4` | Placeholder text |
| Gold (`#e5c158`) | — | Scales icon, cursor glow, hero accents (not in design tokens, added for cinematic effect) |

### Typography
- **Display/Headlines:** Playfair Display (serif), italic variant available
- **Body/UI:** Inter (sans-serif), weights 300–700
- **Note:** DESIGN.md references PPMondwest + af fonts, but index.html actually uses Playfair Display + Inter (Google Fonts). These are the *real* fonts in production.

### Key UI Components
- **Cinematic Hero:** Full-viewport dark section with fog animations, floating scales button, cursor trail
- **Search Dock:** Morphing pill that expands from the scales button
- **Chat Sidebar:** Frosted glass (backdrop-blur), API status indicator, new chat / clear buttons
- **Message Bubbles:** User = dark night-sky bg, Bot = translucent off-white with card shadow
- **Typing Indicator:** Three bouncing dots

---

## 4. API Reference

### `POST /api/chat`
**Non-streaming.** Request: `{ "question": "...", "session_id": "..." }`. Response: `{ "success": true, "answer": "..." }`. Answer truncated at 1200 chars.

### `POST /api/chat/stream`
**SSE streaming.** Same request body. Response: `text/event-stream`. Each word is URL-encoded and sent as `data: <encoded_word>\n\n`. End signal: `data: [DONE]\n\n`. Error signal: `data: [ERROR] <message>\n\n`. Handles 503/429/401/400 errors with user-friendly messages.

### `GET /api/health`
Returns `{ "status": "ok" }`.

### `GET /api/history/<session_id>`
Returns conversation history for session.

### `DELETE /api/history/<session_id>`
Clears conversation history.

### `GET /`
Serves `index.html`.

### `GET /demo`
Serves `Frontend/transition_demo.html`.

---

## 5. System Prompt (Nyaya Persona)

The bot is named **"Nyaya"** — a senior Indian law expert. Key behaviors:
- Authoritative but approachable voice
- Strict markdown response format: `## [Law/Section]` → `**In short:**` → `### What This Means` → `### Key Points` → `### A Real-World Example` → `### Watch Out For` → `*Sourced from:*`
- ONLY uses provided legal context — never invents
- Greetings/identity questions get a warm, short response (under 60 words)
- Legal responses kept under 450 words
- Uses bold for every key legal term on first use

---

## 6. Dependencies & Environment

### Python (venv at `d:\Ai_Law_Assist\venv`)
```
google-genai          # Gemini API client (NOT google-generativeai)
langchain             # Orchestration framework
langchain-community   # FAISS vectorstore loader
langchain-text-splitters  # Document chunking
langchain-huggingface # HuggingFace embeddings integration
sentence-transformers # Embedding model runtime
faiss-cpu             # Vector similarity search
python-dotenv         # .env file loading
flask                 # Web framework
flask-cors            # CORS middleware
huggingface-hub>=0.16.0
```

### Frontend (CDN, no build step)
- Tailwind CSS CDN (`cdn.tailwindcss.com`)
- Marked.js CDN (`cdn.jsdelivr.net/npm/marked/marked.min.js`)
- Google Fonts: Playfair Display, Inter

### Environment Variables
- `GEMINI_API_KEY` — Google Gemini API key (stored in `.env`)

---

## 7. Conventions & Patterns

### Code Style
- Python: Standard PEP 8, no type hints used currently
- HTML: Single-file architecture (all CSS + JS inline in index.html)
- No build pipeline, no bundler, no package.json for frontend
- Flask serves everything — no separate frontend server

### Naming
- Routes: `/api/<resource>` pattern
- Session IDs: UUID strings stored in browser `localStorage`
- CSS tokens: `--color-*`, `--sp-*`, `--r-*`, `--shadow-*`

### Error Handling
- Backend: try/catch with specific HTTP status code detection (503, 429, 401, 400)
- Frontend: SSE `[ERROR]` messages displayed in chat as styled error bubbles
- API health check polled on page load

### Important Quirks
1. **UTF-8 force:** `api.py` wraps stdout/stderr for Windows console compatibility
2. **No persistent storage:** Conversations are in-memory dict, lost on server restart
3. **Hybrid RAG parameters:** API fetches dense/sparse $K=15$ candidates, then reranks to select the top $k=3$ chunks.
4. **Context building:** Full document page_content is used without character truncation, cleaned only via regex (preserving Section titles/headers).
5. **1200-char answer cap:** Non-streaming endpoint truncates answers at 1200 chars
6. **CinematicTransition.jsx exists but is NOT used** — index.html has its own vanilla JS version
7. **`allow_dangerous_deserialization=True`** — Required for FAISS pickle loading, acceptable for local use

---

## 8. Current State

### ✅ Working
- Flask API server starts and serves UI at `http://localhost:5000`
- FAISS index built from 14 acts (12,824 semantic chunks) instead of raw PDFs
- Chat UI with cinematic hero → search dock → chat transition
- SSE streaming responses work
- Dark/light mode toggle
- Session management in localStorage
- Error handling with user-friendly messages
- `/demo` route serves transition demo

### ⚠️ Known Issues
- Conversations lost on server restart (in-memory only)
- No authentication or rate limiting
- No production deployment config (no Gunicorn, no Nginx)

---

## 9. Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-05-26 | Antigravity | Implemented Phase 4 Hybrid Retrieval (FAISS + BM25) and Cross-Encoder Reranking, fixed context truncation and cleaned Gemini API integrations. Removed streamlit and old app.py files. |
| 2026-05-26 | Antigravity | Created PROJECT_KNOWLEDGE.md — initial full project documentation |
| *(prior)* | Various agents | Built cinematic hero UI, SSE streaming, Nyaya persona prompt, FAISS pipeline, dark mode |

---

## 10. Roadmap / Next Steps

### Planned
- [ ] Database persistence for conversations (replace in-memory dict)
- [ ] User authentication & API key management
- [ ] Rate limiting
- [ ] Response caching for frequent queries
- [ ] Production deployment (Gunicorn + Nginx)
- [ ] More legal PDFs in corpus

### Design
- [ ] Mobile responsive refinements
- [ ] Accessibility improvements (ARIA labels, keyboard nav)
- [ ] Loading skeleton states

---

## 11. Jules MCP Integration

Jules is configured as an MCP server with 4 tools:
- `jules_list_sources` — List connected GitHub repos
- `jules_create_session` — Create a coding session (Jules makes code changes)
- `jules_list_sessions` — List past sessions with prompts + diffs
- `jules_approve_plan` — Approve a plan Jules proposed

**Usage:** Jules is a *coding agent*, not a knowledge store. Use it to delegate specific coding tasks (e.g., "add rate limiting to api.py"). For project context, always read THIS file.

### Past Jules Sessions
| Session ID | Status | Task |
|-----------|--------|------|
| `sessions/6635753373501014959` | COMPLETED | Bitcoin trading simulator (test/demo, unrelated to this project) |

---

*This file is maintained by AI agents working on this project. Always update after making changes.*

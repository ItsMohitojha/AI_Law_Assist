# 🏛️ Nyaya: AI-Powered Indian Legal Assistant
> **Academic Project Context & Documentation**  
> **Target Output:** Academic Project Report Context

---

## 1. Project Overview

### Project Title
**Nyaya: AI-Powered Indian Legal Assistant (A Hybrid RAG Approach to Statutory Information Retrieval)**

### One-Paragraph Description
**Nyaya** is an advanced Retrieval-Augmented Generation (RAG) system engineered to make Indian statutory law accessible, clear, and contextually grounded. It utilizes a hierarchical multi-stage extraction pipeline to ingest 14 key Indian acts (amounting to 12,824 semantic chunks) across 9 legal domains. The system implements a two-tier hybrid retrieval architecture combining dense vector search (via HuggingFace sentence embeddings and FAISS) and sparse keyword retrieval (via a custom Okapi BM25 implementation). Retrieved chunks are dynamically reranked using a neural Cross-Encoder before being synthesized by the Google Gemini 2.5 Flash Lite API. Nyaya streams authoritative, formatted, and strictly cited legal explanations to users via Server-Sent Events (SSE) in real-time inside a modern, cinematic web interface.

### The Core Problem It Solves
Indian legal literature—comprising acts, amendments, and notifications—is voluminous, highly dense, and written in complex legalese. Citizens, law students, and legal professionals face significant hurdles in navigating these unstructured documents to extract precise provisions. General-purpose Large Language Models (LLMs) are inadequate for legal counseling because they are prone to hallucinations, generate incorrect statutory citations, and lack structural alignment with specific legal jurisdictions. Nyaya solves this by:
1. Restricting LLM outputs strictly to a verified local legal corpus using high-precision retrieval mechanisms.
2. Paraphrasing complex statutory provisions into plain, user-accessible English.
3. Enforcing structured, formatted explanations containing key legal definitions, real-world examples, and exact source citations to ensure trust and transparency.

---

## 2. Objectives

### Primary Objective
To design, implement, and validate an authoritative, zero-hallucination, interactive AI legal assistant that structures Indian statutory laws into digestible explanations with exact source citations, supported by a low-latency streaming backend and a responsive user interface.

### Specific Sub-Objectives
1. **Multi-Stage Processing Pipeline:** Develop and implement ingestion scripts to parse legal PDFs into structured JSON documents by extracting metadata details (parts, chapters, sections, articles, page numbers) and handling repealed clauses.
2. **Hierarchical Semantic Chunking:** Implement a custom chunking algorithm that splits legal sections into overlapping passages (max 1200 characters with 200-character overlap) while preserving context-rich headers to avoid information loss at block boundaries.
3. **Dense-Sparse Hybrid Retrieval:** Construct a hybrid retrieval engine combining a local FAISS dense vector index (using 384-dimensional `all-MiniLM-L6-v2` embeddings) and a sparse lexical search (using custom `BM25Retriever`) to optimize retrieval across both conceptual queries and exact statutory keywords.
4. **Neural Reranking Optimization:** Integrate a Cross-Encoder reranker (`ms-marco-MiniLM-L-6-v2`) to re-score candidate chunks, filtering retrieval noise to select the top $k=3$ highest-precision blocks and fitting them comfortably within the LLM's attention span.
5. **Deterministic Legal Persona (Nyaya):** Construct a robust system prompt to establish the "Nyaya" persona, enforcing strict formatting constraints (applicable law, brief summaries, implications, scenarios, exceptions, and source citations) and preventing responses based on external web knowledge or hallucinations.
6. **Cinematic & Responsive Interface:** Design a single-page frontend (`index.html`) using Vanilla JS and Tailwind CSS, featuring an animated scales-of-justice landing section, smooth layout transitions, markdown rendering, and real-time SSE stream decoders.
7. **Thread-Safe Resource Protection:** Implement a thread-safe, in-memory sliding-window rate limiter restricting client IPs to 5 queries per minute, protecting backend system resources and third-party APIs from abuse.

---

## 3. Tech Stack

### Programming Language and Version
*   **Python 3.11.x:** The core language for the backend API, document extraction pipelines, database builders, and verification scripts.

### Libraries, Frameworks, and Tools
*   **Flask 3.0.x (with Flask-CORS):** Micro web framework used to expose REST API endpoints and stream token packets using standard HTTP Server-Sent Events (SSE).
*   **google-genai:** The official Google GenAI SDK used to interface with the Gemini 2.5 Flash Lite API.
*   **FAISS (faiss-cpu):** High-performance vector database utilized for index creation, loading, and performing local dense similarity searches.
*   **langchain & langchain-community:** Used for document representation and loading the FAISS vector index database.
*   **langchain-huggingface & sentence-transformers:** Generates dense embeddings locally using the HuggingFace Hub runtime.
*   **PyMuPDF (fitz):** High-performance PDF parser used to extract raw text, verify text viability, and capture page indexes.
*   **python-dotenv:** Simplifies configuration management by loading API keys and options from local `.env` files.
*   **Marked.js (CDN):** Client-side library used to parse markdown responses into clean, styled HTML on-the-fly.

### Database Used
*   **FAISS Local Vector Store:** Persisted locally as `index.faiss` (multidimensional index) and `index.pkl` (pickled metadata map containing document details).
*   **Flask In-Memory Dictionary:** Tracks conversation histories mapped to session IDs during runtime.

### Frontend Tools
*   **HTML5 & Vanilla JavaScript (ES6):** Handles animations, interactive search docks, light/dark styling, state variables, session tracking, and SSE stream decoding.
*   **Tailwind CSS (via CDN):** Directs the responsive layout structure.
*   **Google Fonts:** Playfair Display (Serif) and Inter (Sans-Serif).

---

## 4. System Architecture

### Architectural Overview Diagram
```
 ┌────────────────────────────────────────────────────────┐
 │               Web Frontend (index.html)                │
 │ - Landing Hero (Scales of Justice Animation)           │
 │ - Morphing Search Dock & Responsive Layout             │
 │ - EventSource Client (SSE Stream Decoder)               │
 │ - Marked.js (Markdown-to-HTML Parser)                  │
 └──────────────────────────┬─────────────────────────────┘
                            │
                            │ HTTP POST (Payload: question, session_id)
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │               Flask API Backend (api.py)               │
 │ - RateLimiter (Thread-safe sliding-window validation)   │
 │ - Endpoint Handlers (/api/chat, /api/chat/stream)      │
 │ - In-Memory Session Memory Manager                     │
 └──────────────┬──────────────────────────┬──────────────┘
                │                          │
   Retrieves    │                          │ Queries
   Candidates   ▼                          ▼
 ┌──────────────────────────┐      ┌──────────────────────┐
 │   Local Hybrid Search    │      │ Remote LLM Inference │
 │                          │      │                      │
 │ - FAISS Dense (15 docs)  │      │ - Google Gemini API  │
 │ - BM25 Sparse (15 docs)  │      │ - model: gemini-2.5  │
 │ - CrossEncoder Reranker  │      │   -flash-lite        │
 │   (top-3 reranked)       │      │ - System Prompt      │
 └──────────────────────────┘      └──────────────────────┘
```

### Data Flow Pipeline (Input → Process → Output)
1.  **Request Ingestion:** The user submits a question through the frontend search bar. The client issues an HTTP POST request to `/api/chat/stream`.
2.  **Rate Verification:** The Flask backend catches the request, extracts the client IP address, and verifies it with the thread-safe `RateLimiter`. If the IP has exceeded 5 requests in the last 60 seconds, it immediately returns a `429 Too Many Requests` response.
3.  **Dense Retrieval:** The query is embedded via `all-MiniLM-L6-v2` and FAISS conducts a cosine-similarity search against the local index to retrieve the top 15 dense candidates.
4.  **Sparse Retrieval:** In parallel, the query is tokenized, and the custom `BM25Retriever` computes scores across the legal corpus to retrieve the top 15 sparse candidates.
5.  **Deduplication:** The dense and sparse candidate lists are combined. Chunks are deduplicated using their metadata `chunk_id` (or raw content string).
6.  **Neural Reranking:** The deduplicated candidates are paired with the user's query and processed through the Cross-Encoder model. The candidates are sorted by their predicted relevance scores, and the top 3 are selected.
7.  **Prompt Assembly:** The system extracts the text from the top 3 chunks, runs them through the cleaning regex to remove markdown noise, and injects them into the `SYSTEM_PROMPT` as context alongside the user's question.
8.  **API Streaming & Client Update:** The Flask backend issues a stream response. The Gemini API generates tokens, which are URL-encoded and sent word-by-word via Server-Sent Events (SSE). The browser's EventSource client decodes these words, formats the text using Marked.js, and appends it to the chat feed.

### Major Component Modules
*   **PDF Extraction Pipeline (`extract_text.py`):** Automatically traverses directories, checks text counts per page to filter scanned image sheets, and extracts clean text from raw PDFs.
*   **Structural Syntax Parser (`structure_text.py`):** Uses regex to match chapters, parts, sections, rules, and articles, mapping each statute's hierarchical coordinates.
*   **Hierarchical Semantic Chunking (`chunk_text.py`):** Implements text splits at paragraph, line, and sentence levels, enforcing overlap configurations.
*   **Vector Index Builder (`build_index.py`):** Loads chunk files, generates vector representations, and compiles the local FAISS index database.
*   **In-Memory Sliding-Window Rate Limiter:** Implements thread safety utilizing lock modules (`threading.Lock`) to track timestamps per IP.
*   **BM25 Retriever:** Pre-computes vocabulary document frequency (DF), corpus inverse document frequency (IDF), and average document length (avgdl) to score keyword matches.

---

## 5. Algorithm / Core Logic

### Hybrid Retrieval & Neural Reranking Logic
The core retrieve-and-rerank logic leverages a combination of dense semantic retrieval, sparse lexical retrieval, and neural cross-encoder reranking.

```
                  User Query
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
     Dense Retrieval      Sparse Retrieval
     (FAISS + Embeddings)  (BM25 Retriever)
      Retrieve top-15      Retrieve top-15
           │                     │
           └──────────┬──────────┘
                      ▼
               Deduplication
             (based on Chunk ID)
                      │
                      ▼
               Neural Reranker
           (Cross-Encoder model)
                      │
                      ▼
               Top-3 Selection
                      │
                      ▼
              Context Generation
                      │
                      ▼
               LLM Synthesis
```

### Step-by-Step Explanation
1.  **Dense Retrieval:** The query $Q$ is converted into a 384-dimensional vector $\vec{v}_Q$. FAISS computes the Euclidean distance between $\vec{v}_Q$ and the vector index embeddings representing all $N$ corpus chunks:
    $$\text{dist}(\vec{v}_Q, \vec{v}_D) = \sqrt{\sum_{i=1}^{384} (v_{Q,i} - v_{D,i})^2}$$
    The 15 chunks with the lowest distance are selected.
2.  **Sparse Retrieval:** The query is parsed into a set of lowercased tokens. The BM25 retriever scores document candidates $D$ using:
    $$\text{Score}_{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
    Where:
    *   $\text{IDF}(q) = \ln\left(\frac{N - \text{DF}(q) + 0.5}{\text{DF}(q) + 0.5} + 1.0\right)$
    *   $f(q, D)$ is the frequency of query term $q$ in document chunk $D$.
    *   $|D|$ and $\text{avgdl}$ are the current chunk length and average chunk length (in tokens), respectively.
    *   $k_1$ (term frequency scaling parameter) = 1.5, and $b$ (length normalization parameter) = 0.75.
    The top 15 scoring chunks are returned.
3.  **Deduplication & Union:** Chunks retrieved from both pipelines are merged. Duplicate elements are pruned based on matching `chunk_id` values.
4.  **Neural Reranking:** The remaining candidate chunks are concatenated with the query as pairs $[Q, D]$. A Cross-Encoder Transformer (`cross-encoder/ms-marco-MiniLM-L-6-v2`) processes each pair through its self-attention layers to capture cross-term interactions. The model outputs a logit representing the query-document relevance score:
    $$\text{Score}_{Rerank}(D, Q) = \text{CrossEncoder}(Q, D)$$
    The candidate chunks are sorted in descending order of these scores.
5.  **Context Assembly:** The top 3 chunks are selected, cleaned, and concatenated as the context for the LLM prompt.

---

## 6. Dataset / Data Used

### Dataset Description
The dataset consists of 14 statutory acts and regulations containing Indian laws. The corpus covers a wide range of legal domains to test the system's accuracy and coverage.

| Filename | Domain/Category | Number of Raw Pages | Encoded Chunk JSON Size | Key Subject Areas |
| :--- | :--- | :---: | :---: | :--- |
| `constitution_of_india.json` | Constitutional | ~400 | 5.68 MB | Fundamental rights, duties, state directives, judicial appointments. |
| `indian_panel_code.json` | Criminal | ~250 | 2.44 MB | Substantive penal code definitions, offenses, and punishments (IPC). |
| `bharatiya_nyaya_sanhita_2023.json` | Criminal | ~150 | 2.25 MB | Enacted modern replacement for the substantive Indian Penal Code. |
| `bharatiya_nagarik_suraksha_sanhita_2023.json` | Criminal | ~250 | 3.38 MB | Code of Criminal Procedure (CrPC) modern replacement. |
| `bharatiya_sakshya_adhiniyam_2023.json` | Criminal | ~80 | 741 KB | Modern Indian Evidence Act replacement. |
| `prevention_of_corruption_act_1988.json` | Criminal | ~30 | 286 KB | Bribery, public servant liabilities, investigative structures. |
| `code_of_civil_procedure_1908.json` | Civil | ~350 | 7.30 MB | Legal processes governing civil trials, lawsuits, and decrees. |
| `indian_contract_act_1872.json` | Civil | ~80 | 932 KB | Agreements, contract breaches, damages, indemnity, and guarantees. |
| `consumer_protection_act_2019.json` | Consumer | ~40 | 450 KB | E-commerce guidelines, consumer forums, product liability. |
| `information_technology_act_2000.json` | Cyber | ~60 | 598 KB | Cybercrimes, digital signatures, electronic document rules. |
| `industrial_disputes_act.json` | Labor | ~70 | 1.05 MB | Labor disputes, strikes, lockouts, layoffs, trade union issues. |
| `motor_vehicles_act_1988.json` | Transport | ~180 | 1.54 MB | Traffic offences, licenses, insurance, state transport guidelines. |
| `ugc_regulations.json` | Education | ~20 | 148 KB | Academic standards, faculty requirements, higher education rules. |
| `protection_of_women_from_domestic_violence_act_2005.json` | Women Protection| ~25 | 171 KB | Shared household rights, protection orders, domestic abuse. |

### Chunk Data Schema
Each generated chunk file conforms to the following JSON structure:

```json
{
  "chunk_id": "indian_contract_act_1872_sec_73_chunk_0",
  "metadata": {
    "act_name": "Indian Contract Act",
    "year": 1872,
    "category": "civil",
    "type": "statute",
    "source_file": "indian_contract_act_1872.txt",
    "structure_level": "chapter",
    "structure_number": "VI",
    "structure_title": "OF THE CONSEQUENCES OF BREACH OF CONTRACT",
    "section_number": "73",
    "section_title": "Compensation for loss or damage caused by breach of contract.",
    "page_numbers": [34, 35],
    "is_repealed": false
  },
  "chunk_index": 0,
  "total_chunks_in_section": 2,
  "raw_content": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby...",
  "content": "Act: Indian Contract Act 1872\nchapter VI: OF THE CONSEQUENCES OF BREACH OF CONTRACT\nSection 73: Compensation for loss or damage caused by breach of contract.\nContent:\nWhen a contract has been broken, the party who suffers by such breach is entitled to receive..."
}
```

---

## 7. Features

### User-Facing Features
*   **Interactive Animated Landing Interface:** The user is greeted by a cinematic dark sky interface containing floating nebulae, a custom canvas-fog background, and an interactive Scales of Justice SVG that pulses on hover and responds to pointer coordinates with a golden glow.
*   **Seamless Interface Transitions:** Clicking the Scales of Justice triggers a smooth CSS transition where the scales morph into an input field, sliding the landing content away to reveal the chat dashboard.
*   **Real-Time Token Streaming:** Response delivery is handled using Server-Sent Events (SSE). Instead of waiting for the full response to load, legal text streams in word-by-word with active cursor indicators.
*   **Structured "Nyaya" Format:** Answers are formatted into distinct, readable cards:
    *   *Header Banner:* Outlines the relevant Act, Section, or Article.
    *   *In Short:* A single-sentence summary of the rule.
    *   *What This Means:* A plain-English explanation, highlighting key terms in **bold**.
    *   *Key Points:* An easy-to-read list of conditions, exemptions, and criteria.
    *   *Real-World Example:* A hypothetical scenario illustrating how the law is applied.
    *   *Watch Out For:* Potential exceptions, caveats, or common pitfalls.
    *   *Sourced From:* Detailed metadata citation links displaying exact origin details.
*   **Conversation History Drawer:** A sliding sidebar that tracks past conversations, allows starting a new session, clearing history, and displays a live indicator checking backend API health.
*   **Informational Showcases:** Responsive homepage grids that showcase Nyaya's legal categories, operational guides, and contact/feedback forms.
*   **High-Contrast Theme Toggle:** A button to switch between the dark hero landing page and a clean, high-contrast light theme for the chat interface.

### Administrator Features
*   **Thread-Safe In-Memory Rate Limiting:** Exposes rate limits to protect endpoints (`/api/chat` and `/api/chat/stream`) from automated scraping.
*   **CORS Configuration:** Enables cross-origin requests for approved hostnames.
*   **Rebuild Script CLI:** Standardized CLI tooling to rebuild the FAISS database index when new acts are added.

---

## 8. Testing Done

### Automated Integration and Component Testing
*   **Retrieval Engine Validation (`test_hybrid_retrieval.py`):** Verified the hybrid candidate selection process. Tested query `"What is the compensation for breach of contract?"` and verified that FAISS retrieved concepts related to "breach and liability," while the BM25 model matched exact keywords from "Section 73".
*   **Reranking Assessment (`test_reranker.py`):** Tested the Cross-Encoder model's capacity to bubble relevant chunks to the top 3 slots. Verified that chunks containing exact statutory provisions scored significantly higher than contextual filler chunks.
*   **SSE Pipeline Tests (`test_api_streaming.py`, `test_api_mock_streaming.py`):** Simulated network streams to verify that token generator iterations yielded URL-encoded outputs and terminated correctly using `[DONE]`.
*   **System Prompt & Formatting Verification (`test_gemini_system_instruction.py`, `test_new_prompt.py`):** Evaluated LLM adherence to formatting constraints. Confirmed that queries on general topics or greetings bypassed the structured layout and received warm, concise responses (under 60 words). Verified that legal questions strictly followed the structured "Nyaya" layout.
*   **Rate Limiter Validation (`test_rate_limit.py`, `test_rate_limit_rapid.py`):** Fired concurrent mock requests from a single client IP. Confirmed that the first 5 requests returned valid 200/400 codes, and requests 6 through 8 were blocked with a 429 status code and the correct rate-limit JSON error payload.

### Manual Verification Matrix
| Test Scenario / Input | Expected Output / Behavior | Actual Output / Behavior | Pass/Fail |
| :--- | :--- | :--- | :---: |
| Click "Scales of Justice" icon on the homepage. | Smooth morphing animation; search input appears, and chat interface loads. | Morphing animation played seamlessly; search input appeared, and page shifted to chat view. | **PASS** |
| Query: `"Hi, who are you?"` (Greeting) | Bypasses the structured legal format; returns a warm greeting under 60 words introducing "Nyaya". | Returned: *"Hello! I am Nyaya, your friendly AI assistant for Indian law..."* (43 words). | **PASS** |
| Query: `"What is the punishment for theft under BNS?"` | Structured response detailing Bharatiya Nyaya Sanhita, Section 303, Theft penalties, and a real-world example. | Returned structured sections detailing BNS Theft provisions, complete with a scenario, caveats, and citations. | **PASS** |
| Query: `"Tell me about the US Constitution."` | LLM returns the fallback message: *"Nyaya does not have enough information on this specific question..."* | Returned the correct fallback message, refusing to reference non-Indian legal databases. | **PASS** |
| Submit empty query string to `/api/chat/stream`. | Server rejects the request with HTTP Status 400 (`{"error": "Empty question"}`). | Server returned HTTP Status 400 and the correct JSON payload. | **PASS** |
| Trigger more than 5 requests inside 60 seconds. | Server blocks the 6th request with HTTP 429 (`{"error": "Too many requests..."}`). | Server blocked the 6th request with a 429 status code and displayed the rate-limit warning banner. | **PASS** |

---

## 9. Limitations

### Architectural & Functional Limitations
*   **Volatile Conversation State:** The Flask server uses an in-memory dictionary to store conversation history. Restarting the server clears all active chat histories.
*   **In-Memory Rate Limiting Scope:** The rate limiter tracks requests per IP using local server memory. Under load-balanced deployments with multiple worker processes, rate limiting data is isolated per worker and memory usage scales with active traffic.
*   **Static Search Index:** The FAISS index is built offline from static chunk files. Adding new acts or documents requires manual execution of the build script; they cannot be added dynamically at runtime.
*   **Lack of User Authentication:** The application uses locally generated session IDs in the browser's `localStorage` and lacks user authentication, user profiles, or role-based access controls.
*   **Context Token Footprint:** Using the top 3 chunks without character truncation can consume significant input tokens during long conversations, resulting in higher API costs.

---

## 10. Future Enhancements

### Planned Improvements
1.  **Persistent Conversation Store:** Integrate a lightweight relational database (e.g., SQLite or PostgreSQL) with Flask to persist user chats across server restarts.
2.  **Distributed Rate Limiting and Caching:** Use Redis to handle distributed sliding-window rate limiting across multiple server processes and cache responses to frequent user queries to reduce API costs.
3.  **User Authentication Framework:** Implement an authentication system (e.g., OAuth2 or JWT tokens) to secure user profiles and conversation histories.
4.  **Admin Ingestion Dashboard:** Develop a secure administrative dashboard to upload legal PDFs, automatically trigger text extraction, chunking, and index updates, and append new vectors to FAISS at runtime.
5.  **Interactive Citation Mappings:** Add clickable citation links in the UI that retrieve and highlight the exact source page from the original PDF document.

---

## 11. References

### Libraries, Tools, and Documentation References
*   **Facebook AI Similarity Search (FAISS):** https://github.com/facebookresearch/faiss
*   **Google Gemini API & `google-genai` Python SDK:** https://github.com/google/generative-ai-python
*   **Sentence Transformers (HuggingFace):** https://www.sbert.net/
*   **Okapi BM25 Retrieval Algorithm:** Stephen Robertson, Hugo Zaragoza, et al. *The Probabilistic Relevance Framework: BM25 and Beyond* (2009).
*   **Flask Web Framework:** https://flask.palletsprojects.com/
*   **Marked.js Markdown Parser:** https://marked.js.org/
*   **PyMuPDF (fitz) Documentation:** https://pymupdf.readthedocs.io/

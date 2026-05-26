import os
import re
import sys
import io
from dotenv import load_dotenv

# Force UTF-8 output so Windows console encoding never crashes the server
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from google import genai
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------- INIT --------------------
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)

# -------------------- VECTOR DB --------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

# 🔥 IMPORTANT FIX (less context = better answers)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -------------------- CLEAN CONTEXT --------------------
def clean_context(text):
    text = re.sub(r'#{2,}', '', text)
    text = re.sub(r'\*{2,}', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'Page \d+', '', text)
    text = re.sub(r'Section \d+.*', '', text)
    return text.strip()

# -------------------- SYSTEM PROMPT --------------------
SYSTEM_PROMPT = """You are Nyaya, a senior Indian law expert who explains complex legal concepts the way a brilliant, empathetic lawyer would explain them to a smart client — clearly, directly, and with genuine insight.

YOUR VOICE:
- Authoritative but approachable — like a trusted legal advisor, not a textbook
- Direct: answer the question immediately, no filler phrases
- Use plain English to explain legal jargon, then define the term in bold
- Show genuine insight about the nuances of the law

EXCEPTION FOR GREETINGS AND GENERAL/IDENTITY QUESTIONS:
- If the user's question is a simple greeting (e.g., "hello", "hi", "hey", "good morning"), a casual conversation opener, or asking who/what you are (e.g., "who are you", "what is your name", "what do you do"), do NOT follow the legal RAG response structure or the absolute rules below.
- Instead, respond warmly, introduce yourself as Nyaya (your friendly AI legal assistant for Indian law), and ask how you can help them with their legal queries. Keep it to a few friendly, concise sentences (under 60 words).

STRICT FORMATTING FOR LEGAL QUERIES — follow this structure every single time for legal questions, no exceptions:

## [The Applicable Law / Section / Article]
One sentence placing this in context — which Act, when it applies

**In short:** One crisp sentence that directly answers the question

---

### What This Means
2-3 sentences in plain English. Use **bold** for every key legal term the first time it appears. Explain the "why" behind the law, not just the "what".

### Key Points
- **[Legal Term or Right]** — clear, specific explanation
- **[Another Point]** — what it means practically
- **[Exception or Condition]** — when it does or does not apply
(3 to 5 bullet points, each starting with a bolded term)

### A Real-World Example
> **Scenario:** A relatable, specific scenario with a name and situation
> **What happens:** What the law says in that situation, step by step

### Watch Out For
- [Important caveat, exception, or common misconception]
- [Another nuance worth knowing]

---
*Sourced from: [Exact Act name, Section number, Article number from the provided context]*

ABSOLUTE RULES FOR LEGAL QUERIES:
1. ONLY use the provided legal context — never invent, assume, or extrapolate
2. If the answer to the legal query is not in the context, say: Nyaya does not have enough information on this specific question in its legal database. Please consult a qualified lawyer.
3. NEVER write raw legal text — always paraphrase and explain in your own words
4. NEVER write walls of text or skip the structure above
5. Bold every important legal term on first use
6. Keep the entire response under 450 words
"""

# -------------------- MEMORY --------------------
conversations = {}

from flask import Flask, request, jsonify, Response, send_file

# -------------------- ROOT --------------------
@app.route("/")
def home():
    return send_file("index.html")

@app.route("/demo")
def demo():
    return send_file("Frontend/transition_demo.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# -------------------- CHAT --------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        question = data.get("question", "").strip()
        session_id = data.get("session_id", "default")

        if not question:
            return jsonify({"error": "Empty question"}), 400

        if session_id not in conversations:
            conversations[session_id] = []

        # 🔥 RETRIEVE
        docs = retriever.invoke(question)

        context = "\n".join([doc.page_content[:500] for doc in docs])
        context = clean_context(context)

        # 🔥 PROMPT
        final_prompt = f"""{SYSTEM_PROMPT}

Question:
{question}

Context:
{context}

Answer:
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=final_prompt
        )

        answer = response.text.strip()

        # 🔥 LIMIT SIZE
        if len(answer) > 1200:
            answer = answer[:1200] + "..."

        conversations[session_id].append((question, answer))

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- SSE STREAM --------------------
@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    try:
        data = request.json
        question = data.get("question", "").strip()
        session_id = data.get("session_id", "default")

        if not question:
            return jsonify({"error": "Empty question"}), 400

        if session_id not in conversations:
            conversations[session_id] = []

        docs = retriever.invoke(question)

        context = "\n".join([doc.page_content[:500] for doc in docs])
        context = clean_context(context)

        final_prompt = f"""{SYSTEM_PROMPT}

Question:
{question}

Context:
{context}

Answer:
"""

        def generate():
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=final_prompt
                )

                import urllib.parse
                answer = response.text.strip()
                words = answer.split(" ")

                for word in words:
                    if word:
                        yield f"data: {urllib.parse.quote(word)}\n\n"

                yield "data: [DONE]\n\n"

                conversations[session_id].append((question, answer))

            except Exception as e:
                err_str = str(e)
                if '503' in err_str or 'UNAVAILABLE' in err_str:
                    msg = 'Nyaya\'s AI engine is under high demand right now. Please wait a moment and try your legal question again.'
                elif '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                    msg = 'Nyaya has received too many questions at once. Please wait a moment before asking again.'
                elif '401' in err_str or 'API_KEY' in err_str:
                    msg = 'Nyaya could not authenticate with the AI service. Please check your GEMINI_API_KEY in the .env file.'
                elif '400' in err_str:
                    msg = 'Nyaya could not process this question. Please try rephrasing it.'
                else:
                    msg = f'Nyaya encountered an unexpected error. Please try again. ({err_str[:80]})'
                yield f"data: [ERROR] {msg}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------- RUN --------------------
if __name__ == "__main__":
    print("Nyaya API running on http://localhost:5000")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,   # Prevents port conflicts on Windows
        threaded=True
    )
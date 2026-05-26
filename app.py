import os
from dotenv import load_dotenv
from google import genai
import warnings

# Suppress huggingface_hub resume_download deprecation FutureWarning
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message="`resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`."
)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)

# -----------------------------
# Load Embedding Model
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Load FAISS Index
# -----------------------------
vectorstore = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

# Retrieve more documents for better accuracy with similarity threshold
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 10, "fetch_k": 20}  # Fetch more, return top 10
)

print("✅ AI Law Assistant Ready!")

# -----------------------------
# Conversation Memory
# -----------------------------
conversation_history = []

# System prompt with enhanced legal guidance
system_prompt = """You are an expert Indian Law Assistant. Your role is to provide accurate, legally sound answers based on the provided context.

CRITICAL RULES:
1. Answer ONLY what is asked - do not add unnecessary information.
2. Use ONLY the provided legal context - never use external knowledge or assumptions.
3. Cite specific sections, articles, and clause numbers from the context.
4. If multiple provisions apply, explain how they interact.
5. If the answer is NOT in the provided context, explicitly state:
   "I don't have sufficient information in the provided legal context to answer this accurately."
6. When referring to previous discussion, use it only to clarify or expand, not to contradict the legal context.
7. Structure answers with sections/articles, key points, and practical implications.
8. Highlight any conditions, exceptions, or limitations found in the context.
9. Do NOT interpret, extrapolate, or add legal opinions beyond what the text provides.

Formatting:
- Start answers with the most relevant section/article
- Use bullet points for provisions and conditions
- Always mention the source law/act for each provision
"""

# -----------------------------
# Ask Loop
# -----------------------------
while True:
    query = input("\nAsk your legal question (or type 'exit'): ")

    if query.lower() == "exit":
        break

    # Retrieve relevant documents
    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    # Extract source file names
    sources = list(set(
        [doc.metadata.get("source_file", "Unknown") for doc in docs]
    ))

    # Build conversation with history
    messages = [
        {"role": "user", "parts": [system_prompt]},
        {"role": "model", "parts": ["Understood. I will follow these rules and maintain context from previous discussion."]}
    ]
    
    # Add conversation history
    for past_query, past_response in conversation_history:
        messages.append({"role": "user", "parts": [past_query]})
        messages.append({"role": "model", "parts": [past_response]})
    
    # Add current query with context
    current_prompt = f"""LEGAL CONTEXT (from Indian law documents):
{context}

USER QUESTION:
{query}

Please provide an accurate answer based ONLY on the legal context above. If the information is not in the context, state that clearly."""
    
    messages.append({"role": "user", "parts": [current_prompt]})

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages,
    )

    assistant_response = response.text
    
    # Store in conversation history
    conversation_history.append((query, assistant_response))

    print("\n📚 AI Law Assistant:\n")
    print(assistant_response)

    print("\n📌 Retrieved from:")
    for src in sources:
        print(f"  • {src}")
    print(f"\n(Answers are based on {len(docs)} retrieved document(s) with k=5 search)")
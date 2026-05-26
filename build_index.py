import os
import json
import warnings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Suppress huggingface_hub resume_download deprecation FutureWarning
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message="`resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`."
)

DATA_PATH = "data/processed/chunks"
INDEX_PATH = "faiss_index"

def load_all_chunks(data_path):
    all_documents = []

    if not os.path.exists(data_path):
        print(f"Directory {data_path} not found.")
        return all_documents

    for file in os.listdir(data_path):
        if file.endswith(".json"):
            print(f"📄 Loading {file}...")
            filepath = os.path.join(data_path, file)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    chunks = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error loading {file}. Invalid JSON.")
                    continue

            for chunk in chunks:
                metadata = chunk.get("metadata", {})

                # Add specific metadata fields to ensure they are accessible
                if "chunk_id" in chunk:
                    metadata["chunk_id"] = chunk["chunk_id"]
                if "raw_content" in chunk:
                    metadata["raw_content"] = chunk["raw_content"]
                if "chunk_index" in chunk:
                    metadata["chunk_index"] = chunk["chunk_index"]
                if "total_chunks_in_section" in chunk:
                    metadata["total_chunks_in_section"] = chunk["total_chunks_in_section"]

                doc = Document(
                    page_content=chunk.get("content", ""),
                    metadata=metadata
                )
                all_documents.append(doc)

    return all_documents


def main():
    print("🚀 Building FAISS Index from JSON chunks...\n")

    docs = load_all_chunks(DATA_PATH)

    print(f"🧩 Total chunks loaded: {len(docs)}")
    if docs:
        avg_words = sum(len(doc.page_content.split()) for doc in docs) // max(1, len(docs))
        print(f"📏 Average chunk size: {avg_words} words")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(docs, embedding_model)

    # Overwrite existing index
    vectorstore.save_local(INDEX_PATH)

    print("\n✅ FAISS index rebuilt successfully with ALL laws!")


if __name__ == "__main__":
    main()
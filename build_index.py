import os
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Suppress huggingface_hub resume_download deprecation FutureWarning
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message="`resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`."
)

DATA_PATH = "data"
INDEX_PATH = "faiss_index"

def load_all_pdfs(data_path):
    all_documents = []

    for file in os.listdir(data_path):
        if file.endswith(".pdf"):
            print(f"📄 Loading {file}...")
            loader = PyPDFLoader(os.path.join(data_path, file))
            documents = loader.load()

            # Add metadata for source tracking
            for doc in documents:
                doc.metadata["source_file"] = file

            all_documents.extend(documents)

    return all_documents


def main():
    print("🚀 Building FAISS Index from all PDFs...\n")

    documents = load_all_pdfs(DATA_PATH)

    print(f"\n📚 Total pages loaded: {len(documents)}")

    # Improved chunk settings for legal documents
    # Larger chunks to keep sections intact, with more overlap for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Larger chunks to keep complete sections
        chunk_overlap=300,  # Significant overlap to capture context
        separators=[
            "\n\n\n",      # Triple newline (major section break)
            "\n\n",        # Double newline (paragraph break)
            "\n",          # Single newline
            ". ",          # Sentence period
            " ",           # Word break
            ""             # Character break
        ]
    )

    docs = text_splitter.split_documents(documents)

    print(f"🧩 Total chunks created: {len(docs)}")
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
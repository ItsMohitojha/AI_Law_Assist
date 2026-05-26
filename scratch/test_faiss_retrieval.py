from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

query = "What is Article 21 of the Indian Constitution?"
docs = retriever.invoke(query)

print(f"=== Query: {query} ===")
print(f"Retrieved {len(docs)} documents:")
for i, doc in enumerate(docs):
    print(f"\nDocument {i+1}:")
    print("Content preview:", doc.page_content[:400])
    print("Metadata:", doc.metadata)

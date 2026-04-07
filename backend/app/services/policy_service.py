import os
import chromadb
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
POLICY_PATH = os.path.join(BASE_DIR, "data", "policy", "company_policy.pdf")

chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="company_policy")

def build_vector_db():
    print("Checking database status...")
    
    if collection.count() > 0:
        print(f"Database already populated with {collection.count()} policy chunks.")
        return

    print(f"Reading corporate policy PDF from {POLICY_PATH}...")
    try:
        reader = PdfReader(POLICY_PATH)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return

    # --- THE UPGRADE: Advanced Chunking ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # We use split_text because raw_text is a giant string
    chunks = text_splitter.split_text(raw_text)
    
    print(f"✅ Split 40-page policy into {len(chunks)} optimized chunks.")

    # 4. Load into ChromaDB
    # Note: Chroma handles the embeddings automatically using its default model
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"policy_chunk_{i}"]
        )
    
    print("🚀 Vector Database successfully built with 40-page context!")

def search_policy(query: str, n_results: int = 5) -> list:
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0]

if __name__ == "__main__":
    build_vector_db()
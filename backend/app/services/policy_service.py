import os
import chromadb
from pypdf import PdfReader

# 1. Define where the database and the PDF live
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
POLICY_PATH = os.path.join(BASE_DIR, "data", "policy", "corporate_policy.pdf")

# 2. Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# Get or create a "collection" (like a table in a normal database)
collection = chroma_client.get_or_create_collection(name="corporate_policy")

def build_vector_db():
    """Reads the PDF, chunks the text, and stores it in the vector database."""
    print("Checking database status...")
    
    # If we already have data, we don't need to rebuild it
    if collection.count() > 0:
        print(f"Database already populated with {collection.count()} policy chunks.")
        return

    print("Reading corporate policy PDF...")
    try:
        reader = PdfReader(POLICY_PATH)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF. Make sure it is saved at {POLICY_PATH}")
        print(f"Exact error: {e}")
        return

    # 3. Chunking: Split the text by double newlines to separate paragraphs
    chunks = [chunk.strip() for chunk in raw_text.split('\n\n') if len(chunk.strip()) > 10]
    
    print(f"Split policy into {len(chunks)} chunks. Generating embeddings...")

    # 4. Load into ChromaDB
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"policy_chunk_{i}"]
        )
    
    print("✅ Vector Database successfully built!")

def search_policy(query: str, n_results: int = 2) -> list:
    """Searches the database for the most relevant policy rules based on the user's query."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    # Return the actual text of the matching paragraphs
    return results['documents'][0]

# If we run this file directly, build the database!
if __name__ == "__main__":
    build_vector_db()
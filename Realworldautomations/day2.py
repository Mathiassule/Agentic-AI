import os
import numpy as np
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. CORE RAG FUNCTIONS
# ==========================================
def chunk_text(filepath, chunk_size=300):
    """Reads a file and chops it into smaller chunks of text."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Simple splitting by character count (in production, use sentence splitters)
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        print(Fore.CYAN + f"📄 Split document into {len(chunks)} chunks.")
        return chunks
    except FileNotFoundError:
        print(Fore.RED + f"Error: Could not find {filepath}")
        return []

def get_embedding(text):
    """Converts text into a list of floating-point numbers (a Vector)."""
    # We use a specific, lightweight model just for embeddings
    response = client.models.embed_content(
        model='gemini-embedding-001',
        contents=text
    )
    return response.embeddings[0].values

def cosine_similarity(vec1, vec2):
    """Mathematical formula to check how 'close' two vectors are."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# ==========================================
# 2. THE RAG AGENT
# ==========================================
def document_qa_agent(filepath, user_query):
    print(Fore.WHITE + Style.BRIGHT + f"\n🚀 STARTING RAG PIPELINE FOR: '{user_query}'")
    
    # STEP 1: CHUNK
    chunks = chunk_text(filepath)
    if not chunks: return
    
    # STEP 2: EMBED ALL CHUNKS (Creating our "Vector Database" in memory)
    print(Fore.YELLOW + "🧠 Converting chunks to embeddings (numbers)...")
    chunk_embeddings = [get_embedding(chunk) for chunk in chunks]
    
    # STEP 3: EMBED THE QUERY
    query_embedding = get_embedding(user_query)
    
    # STEP 4: SEARCH (Find the most relevant chunk)
    print(Fore.YELLOW + "🔎 Searching for the most relevant context...")
    best_score = -1
    best_chunk = ""
    
    for i, chunk_emb in enumerate(chunk_embeddings):
        score = cosine_similarity(query_embedding, chunk_emb)
        if score > best_score:
            best_score = score
            best_chunk = chunks[i]
            
    print(Fore.MAGENTA + f"   -> Found relevant chunk! (Match Score: {best_score:.4f})")
    print(Style.DIM + f"   -> Context snippet: {best_chunk[:100]}...")

    # STEP 5: GENERATE (Pass the found context to Flash Lite)
    print(Fore.GREEN + "\n✍️  Generating final answer...")
    prompt = f"""
    You are a helpful assistant. Answer the user's query using ONLY the provided context.
    If the answer is not in the context, say "I don't know."
    
    CONTEXT: {best_chunk}
    
    USER QUERY: {user_query}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    
    print(Fore.WHITE + Style.BRIGHT + f"\n✅ FINAL ANSWER:\n{response.text}")
    print(Style.DIM + "-" * 50)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # Create a quick dummy file if it doesn't exist
    test_file = "company_policy.txt"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("Welcome to the company. The Wi-Fi password is 'BlueOcean2026'. " * 10)
            f.write("Lunch is served at 12:30 PM in the main cafeteria. " * 10)
            f.write("The CEO's dog is named Barnaby. " * 10)
            
    query = "What is the Wi-Fi password?"
    document_qa_agent(test_file, query)
"""
Hellobooks - AI-Powered Bookkeeping Assistant
RAG (Retrieval-Augmented Generation) System
Uses: sentence-transformers (embeddings) + FAISS (vector store) + Google Gemini Flash (LLM)
"""

from dotenv import load_dotenv
load_dotenv()

import os
import glob
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from google import genai

# Configuration
KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # overlap between chunks
TOP_K = 3               # number of chunks to retrieve
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # fast, small, efficient (22MB)
LLM_MODEL = "gemini-3-flash-preview"      # latest fast free-tier model


# Document Loading & Chunking
def load_documents(kb_dir: Path) -> list[dict]:
    """Load all markdown files from knowledge base directory."""
    docs = []
    for filepath in glob.glob(str(kb_dir / "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        filename = Path(filepath).stem.replace("_", " ").title()
        docs.append({"source": filename, "content": content, "filepath": filepath})
    print(f"📚 Loaded {len(docs)} documents from knowledge base.")
    return docs


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_newline = chunk.rfind("\n")
            if last_newline > chunk_size // 2:
                chunk = chunk[:last_newline]
                end = start + last_newline
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]


def prepare_chunks(docs: list[dict]) -> list[dict]:
    """Chunk all documents and attach metadata."""
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": i,
                "text": chunk
            })
    print(f"✂️  Created {len(all_chunks)} chunks from documents.")
    return all_chunks


# Embedding & FAISS Index
def build_index(chunks: list[dict], model: SentenceTransformer):
    """Generate embeddings and build FAISS index."""
    print("🔢 Generating embeddings...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    embeddings = np.array(embeddings, dtype="float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print(f"✅ FAISS index built with {index.ntotal} vectors (dim={dimension}).")
    return index, embeddings


def retrieve(query: str, model: SentenceTransformer, index, chunks: list[dict], top_k: int = TOP_K) -> list[dict]:
    """Retrieve top_k most relevant chunks for a query."""
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(chunks):
            results.append({**chunks[idx], "score": float(dist)})
    return results


# LLM Answer Generation (Google Gemini)
def generate_answer(query: str, retrieved_chunks: list[dict], client: genai.Client) -> str:
    """Send query + retrieved context to Gemini and get an answer."""
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(f"[Source {i}: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are Hellobooks AI, a friendly and knowledgeable accounting assistant for small businesses.
Your role is to answer accounting and bookkeeping questions clearly and accurately.
Use the provided context to answer the question. If the context doesn't fully cover the question,
use your accounting knowledge to supplement — but always stay factual and practical.
Keep answers concise but complete. Use bullet points or numbered lists where helpful.
Always be encouraging and supportive for business owners who may not have accounting backgrounds.

Context from Hellobooks Knowledge Base:
{context}

---

User Question: {query}

Please provide a clear, helpful answer based on the context above."""

    response = client.models.generate_content(model=LLM_MODEL, contents=prompt)
    return response.text


# RAG Pipeline
class HellobooksRAG:
    def __init__(self):
        print("\n🚀 Initializing Hellobooks RAG System...")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not set! Add it to your .env file.")

        self.client = genai.Client()
        print(f"✅ Connected to Google Gemini ({LLM_MODEL})")

        print(f"📦 Loading embedding model: {EMBEDDING_MODEL}")
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)

        docs = load_documents(KNOWLEDGE_BASE_DIR)
        self.chunks = prepare_chunks(docs)
        self.index, self.embeddings = build_index(self.chunks, self.embed_model)
        print("✅ Hellobooks RAG is ready!\n")

    def ask(self, question: str) -> dict:
        """Full RAG pipeline: retrieve → augment → generate."""
        print(f"\n🔍 Retrieving relevant documents for: '{question}'")
        retrieved = retrieve(question, self.embed_model, self.index, self.chunks)

        sources = list(set([r["source"] for r in retrieved]))
        print(f"📄 Retrieved from: {', '.join(sources)}")

        print("🤖 Generating answer with Gemini Flash...")
        answer = generate_answer(question, retrieved, self.client)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": [{"source": r["source"], "preview": r["text"][:100] + "..."} for r in retrieved]
        }


# CLI Interface
def main():
    rag = HellobooksRAG()

    print("=" * 60)
    print("  📒 Welcome to Hellobooks AI Accounting Assistant")
    print("  Ask any accounting or bookkeeping question!")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    while True:
        print()
        question = input("You: ").strip()

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("👋 Goodbye! Keep your books balanced!")
            break

        result = rag.ask(question)

        print("\n" + "─" * 60)
        print(f"🤖 Hellobooks AI:\n{result['answer']}")
        print(f"\n📚 Sources used: {', '.join(result['sources'])}")
        print("─" * 60)


if __name__ == "__main__":
    main()
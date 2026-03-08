"""
Hellobooks - FastAPI Web Server
Exposes the RAG system as a REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn

from rag import HellobooksRAG

# Global RAG instance
rag_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG system on startup."""
    global rag_system
    rag_system = HellobooksRAG()
    yield


app = FastAPI(
    title="Hellobooks AI",
    description="AI-Powered Bookkeeping Assistant using RAG + Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    retrieved_chunks: list[dict]


@app.get("/")
def root():
    return {
        "message": "Welcome to Hellobooks AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "rag_ready": rag_system is not None}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask the Hellobooks AI a bookkeeping/accounting question."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized.")

    result = rag_system.ask(request.question)
    return result


@app.get("/topics")
def list_topics():
    """List available knowledge base topics."""
    return {
        "topics": [
            "Bookkeeping",
            "Invoices",
            "Profit & Loss",
            "Balance Sheet",
            "Cash Flow",
            "Accounts Payable & Receivable",
            "Taxes"
        ]
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)

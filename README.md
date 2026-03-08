# 📒 Hellobooks AI — Accounting Assistant

> An AI-powered bookkeeping assistant built with RAG (Retrieval-Augmented Generation).  
> Ask any accounting question and get accurate, context-grounded answers instantly.

---

## 🏗️ Architecture

```
User Question
     │
     ▼
[Sentence Transformer]  ← all-MiniLM-L6-v2 (22MB, fast)
     │  (embed query)
     ▼
[FAISS Vector Store]    ← L2 similarity search
     │  (retrieve top-3 chunks)
     ▼
[Google Gemini 2.0 Flash] ← free tier, fast
     │  (generate grounded answer)
     ▼
Answer + Sources
```

### Components
| Layer | Tool | Why |
|---|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Tiny (22MB), fast, high quality |
| Vector Store | `FAISS` (CPU) | Lightweight, no server needed |
| LLM | `Google Gemini 2.0 Flash` | Free tier, fast, smart |
| API Server | `FastAPI` | Modern, async, auto-docs |

---

## 📚 Knowledge Base Topics

| File | Topics Covered |
|---|---|
| `bookkeeping.md` | Double-entry, chart of accounts, general ledger |
| `invoices.md` | Invoice types, components, payment terms |
| `profit_and_loss.md` | P&L structure, gross/net profit, margins |
| `balance_sheet.md` | Assets, liabilities, equity, key ratios |
| `cash_flow.md` | Operating/investing/financing activities, FCF |
| `accounts_payable_receivable.md` | AR/AP processes, aging reports |
| `taxes.md` | GST/VAT, income tax, deductible expenses |

---

## ⚙️ Prerequisites

- Python **3.10+**
- A **Google Gemini API Key** (free) → [Get one here](https://aistudio.google.com/app/apikey)
- Docker + Docker Desktop (optional, for containerized deployment)

---

## 🚀 Quick Start

### Option 1: Run Locally (CLI)

```bash
# 1. Clone the repository
git clone https://github.com/Luvyansh/Hellobooks-AI.git
cd Hellobooks-AI

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the project root and add your key:
# GEMINI_API_KEY=your-api-key-here

# 5. Run the CLI assistant
python rag.py
```

**Example session:**
```
You: What is the difference between accounts payable and accounts receivable?

🤖 Hellobooks AI:
Accounts Receivable (AR) is money owed TO your business by customers...
Accounts Payable (AP) is money your business OWES to suppliers...

📚 Sources used: Accounts Payable Receivable
```

---

### Option 2: Run as API Server

```bash
# After completing steps 1-4 above:
python server.py

# API is now running at http://localhost:8000
# Interactive Swagger docs at http://localhost:8000/docs
```

**Example API call:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a balance sheet?"}'
```

**Response:**
```json
{
  "question": "What is a balance sheet?",
  "answer": "A balance sheet is a financial statement...",
  "sources": ["Balance Sheet"],
  "retrieved_chunks": [...]
}
```

---

### Option 3: Run with Docker

```bash
# 1. Make sure your .env file exists with your key:
# GEMINI_API_KEY=your-api-key-here

# 2. Build and run with Docker Compose
docker-compose up --build

# API available at http://localhost:8000
```

```bash
# Or with plain Docker:
docker build -t hellobooks-ai .
docker run -p 8000:8000 --env-file .env hellobooks-ai
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check |
| `POST` | `/ask` | Ask a question |
| `GET` | `/topics` | List knowledge base topics |
| `GET` | `/docs` | Interactive Swagger UI |

---

## 🗂️ Project Structure

```
Hellobooks-AI/
├── knowledge_base/               # Task 1: Knowledge base documents
│   ├── bookkeeping.md
│   ├── invoices.md
│   ├── profit_and_loss.md
│   ├── balance_sheet.md
│   ├── cash_flow.md
│   ├── accounts_payable_receivable.md
│   └── taxes.md
├── rag.py                        # Task 2: Core RAG pipeline (CLI)
├── server.py                     # Task 2: FastAPI web server
├── Dockerfile                    # Task 3: Container config
├── docker-compose.yml            # Task 3: Multi-container orchestration
├── requirements.txt
├── .env                          # Your API keys (never commit this!)
└── README.md
```

---

## 🧩 How RAG Works Here

1. **Indexing (startup)**:
   - Load all `.md` files from `knowledge_base/`
   - Split into overlapping 500-character chunks
   - Generate vector embeddings using `all-MiniLM-L6-v2`
   - Store in FAISS in-memory index

2. **Querying (per request)**:
   - Embed the user's question
   - Find top-3 most similar chunks via FAISS L2 search
   - Inject chunks as context into Gemini Flash prompt
   - Return grounded answer + source attribution

---

## 💡 Sample Questions to Try

- "What is double-entry bookkeeping?"
- "How do I calculate gross profit margin?"
- "What's the difference between cash flow and profit?"
- "What are current assets on a balance sheet?"
- "How should I number my invoices?"
- "What expenses can I deduct for tax purposes?"
- "What is accounts receivable aging?"

---

## 🔧 Configuration

Edit constants at the top of `rag.py`:

```python
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 100     # Overlap between chunks
TOP_K = 3               # Number of chunks to retrieve
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gemini-2.0-flash"
```

---

## 📦 Dependencies

```
google-genai            - Gemini 2.0 Flash LLM API (free tier)
sentence-transformers   - Embedding model
faiss-cpu               - Vector similarity search
fastapi                 - REST API framework
uvicorn                 - ASGI server
numpy                   - Numerical operations
pydantic                - Data validation
python-dotenv           - Load .env API keys
```

---

## 🛡️ Notes

- The FAISS index is **in-memory** and rebuilt on each startup (fast enough for this scale)
- The embedding model downloads once (~22MB) and is cached locally
- All 7 knowledge base documents are chunked into ~41 segments total
- **Never commit your `.env` file** — it's already in `.gitignore`
- Gemini 2.0 Flash free tier allows **1,500 requests/day**

---

## 📸 Screenshots

### 🖥️ CLI Mode

> Running the assistant directly from the terminal using `python rag.py`

<p align="center">
  <img width="80%" alt="CLI startup - RAG system initializing" src="https://github.com/user-attachments/assets/196383ef-7a89-420f-83c4-b97ebc29b79b" />
  <br/>
  <em>RAG system initializing — loading documents, generating embeddings, building FAISS index</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="CLI question and answer" src="https://github.com/user-attachments/assets/02255aee-311f-4c60-a966-4cfe68c1c0b9" />
  <br/>
  <em>Asking an accounting question and receiving a grounded answer with sources</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="CLI follow-up question" src="https://github.com/user-attachments/assets/ebdd16f5-eb0a-40b5-85e3-dc8afaaf53a2" />
  <br/>
  <em>Follow-up question demonstrating multi-topic retrieval</em>
</p>

---

### 🐳 Docker Mode

> Running the API server via `docker-compose up --build` and interacting through Swagger UI at `localhost:8000/docs`

<p align="center">
  <img width="80%" alt="Docker Desktop - container running" src="https://github.com/user-attachments/assets/8c30aa9e-eb20-4b6c-8235-a7cd3807ed15" />
  <br/>
  <em>Docker Desktop showing the hellobooks-ai container running on port 8000</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="Swagger UI - API docs" src="https://github.com/user-attachments/assets/084c1abb-6432-4925-9a68-e6f5b787d2c1" />
  <br/>
  <em>Auto-generated Swagger UI at <code>localhost:8000/docs</code> — interactive API documentation</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="POST /ask endpoint" src="https://github.com/user-attachments/assets/9013c970-caf2-4876-95d4-aa8f80df7474" />
  <br/>
  <em>Testing the <code>POST /ask</code> endpoint with a bookkeeping question</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="API response with answer and sources" src="https://github.com/user-attachments/assets/f31afd56-449d-45a0-b5aa-832ca51e31f3" />
  <br/>
  <em>API response showing the generated answer, sources used, and retrieved chunks</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="GET /topics endpoint" src="https://github.com/user-attachments/assets/e298ae8d-c25d-4808-94de-30062fc52a25" />
  <br/>
  <em><code>GET /topics</code> endpoint listing all available knowledge base topics</em>
</p>

<br/>

<p align="center">
  <img width="80%" alt="GET /health endpoint" src="https://github.com/user-attachments/assets/55eb9bda-a351-400c-99d3-973b31220811" />
  <br/>
  <em><code>GET /health</code> endpoint confirming the RAG system is initialized and ready</em>
</p>

---

*Built for Hellobooks Internship Assignment — Python + Generative AI Mini Project*

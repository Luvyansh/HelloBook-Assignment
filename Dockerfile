# ─────────────────────────────────────────────
# Hellobooks AI - Dockerfile
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Step 1: Install lightweight CPU-only PyTorch FIRST (avoids downloading 915MB GPU version)
RUN pip install --no-cache-dir --timeout=120 \
    torch --index-url https://download.pytorch.org/whl/cpu

# Step 2: Install remaining dependencies
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

# Step 3: Pre-download the embedding model during build (avoids cold-start delay at runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the project
COPY . .

EXPOSE 8000

# Gemini API key — pass at runtime via --env-file .env
ENV GEMINI_API_KEY=""

CMD ["python", "server.py"]
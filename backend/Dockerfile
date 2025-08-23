# Hierarchical Chat Research Backend - Production Dockerfile
# 
# This Dockerfile creates a production-ready container for the research backend
# preserving all notebook innovations while enabling scalable deployment.

FROM python:3.11-slim

# Set environment variables for Python and research optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    # Research environment optimizations
    TOKENIZERS_PARALLELISM=false \
    HF_HOME="/app/.cache/huggingface" \
    TRANSFORMERS_CACHE="/app/.cache/transformers"

# Set working directory
WORKDIR /app

# Install system dependencies for research libraries
RUN apt-get update && apt-get install -y \
    # Build essentials for compiled Python packages
    gcc \
    g++ \
    make \
    # For ChromaDB and vector operations
    sqlite3 \
    # For sentence-transformers and ML libraries
    libopenblas-dev \
    liblapack-dev \
    # For potential PDF processing
    poppler-utils \
    # For data export capabilities
    libpq-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create directories for research data persistence
RUN mkdir -p /app/data/chromadb \
    /app/data/exports \
    /app/data/analytics \
    /app/data/backups \
    /app/logs \
    /app/.cache/huggingface \
    /app/.cache/transformers

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with research optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download sentence-transformers model for faster startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY app/ ./app/

# Create non-root user for security (research data protection)
RUN groupadd -r research && useradd -r -g research -u 1000 researcher
RUN chown -R researcher:research /app
USER researcher

# Expose port for FastAPI application
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Command to run the research backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Production optimization labels
LABEL maintainer="Hierarchical Chat Research Team" \
      version="1.0.0" \
      description="Production FastAPI backend preserving notebook research innovations" \
      research.innovations="LocalBuffer,ContextAssembly,ForestManagement,VectorMemory,LLMIntegration"

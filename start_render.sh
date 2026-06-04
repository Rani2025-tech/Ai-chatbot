#!/bin/bash
# Build FAISS index if it doesn't exist
if [ ! -d "faiss_index" ] || [ ! -f "faiss_index/index.faiss" ]; then
    echo "Building FAISS index..."
    python rebuild_index.py
fi

# Start FastAPI
exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT

#!/bin/bash
# faiss_index/ is committed to the repo — no rebuild needed at startup.
# If you add new PDFs, rebuild locally with: python rebuild_index.py
# then commit the updated faiss_index/ folder before redeploying.

exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT

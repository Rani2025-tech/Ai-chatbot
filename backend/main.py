import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router
from backend.utils import ensure_folders
from backend.database import init_db
from dotenv import load_dotenv

load_dotenv()

# ── Validate required secrets on startup ──────────────────────────
_REQUIRED = ["GROQ_API_KEY", "JWT_SECRET", "ADMIN_PASSWORD"]
_missing = [k for k in _REQUIRED if not os.getenv(k)]
if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        f"Copy .env.example to .env and fill in the values."
    )

app = FastAPI(
    title="AI University Helpdesk",
    description="RAG-based chatbot for university queries",
    version="2.0.0"
)

# FRONTEND_URL should be set to your Streamlit service URL in production.
# Falls back to "*" for local development only.
_frontend_url = os.getenv("FRONTEND_URL", "*")
_origins = [_frontend_url] if _frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_frontend_url != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_folders()
init_db()

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to AI University Helpdesk", "docs": "/docs"}

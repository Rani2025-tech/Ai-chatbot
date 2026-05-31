from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil, os, json
from backend.rag_pipeline import ingest_pdf, get_answer_stream, get_answer
from backend.utils import get_all_pdfs, faiss_index_exists, ensure_folders
from backend import database as db

router = APIRouter()

# ── Models ────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class QuestionRequest(BaseModel):
    question: str
    language: str = "auto"
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class AnswerResponse(BaseModel):
    answer: str
    source: str = "university documents"

class TicketRequest(BaseModel):
    user_id: str
    user_name: str
    session_id: str
    issue: str

class TicketStatusRequest(BaseModel):
    status: str

# ── Auth ──────────────────────────────────────────────────────────
@router.post("/auth/signup")
def signup(req: SignupRequest):
    user = db.create_user(req.name, req.email, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user

@router.post("/auth/login")
def login(req: LoginRequest):
    user = db.login_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

# ── Chat Sessions ─────────────────────────────────────────────────
@router.post("/sessions")
def create_session(data: dict):
    session_id = db.create_session(data["user_id"], data.get("title", "New Chat"))
    return {"session_id": session_id}

@router.get("/sessions/{user_id}")
def get_sessions(user_id: str):
    return db.get_sessions(user_id)

@router.get("/messages/{session_id}")
def get_messages(session_id: str):
    return db.get_messages(session_id)

# ── Ask ───────────────────────────────────────────────────────────
@router.get("/health")
def health_check():
    return {"status": "ok", "message": "AI University Helpdesk is running"}

@router.post("/ask-sync", response_model=AnswerResponse)
def ask_question_sync(request: QuestionRequest):
    if not faiss_index_exists():
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload a university PDF first.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = get_answer(request.question, request.language)
        if request.session_id and request.user_id and request.user_id != "guest":
            try:
                db.save_message(request.session_id, "user", request.question)
                db.save_message(request.session_id, "assistant", answer)
                sessions = db.get_sessions(request.user_id)
                for s in sessions:
                    if s["id"] == request.session_id and s["title"] == "New Chat":
                        db.update_session_title(request.session_id, request.question[:50])
            except Exception as db_err:
                print(f"DB save error (non-fatal): {db_err}")
        return AnswerResponse(answer=answer)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

# ── Tickets ───────────────────────────────────────────────────────
@router.post("/tickets")
def create_ticket(req: TicketRequest):
    ticket_id = db.create_ticket(req.user_id, req.user_name, req.session_id, req.issue)
    return {"ticket_id": ticket_id}

@router.get("/tickets")
def get_tickets():
    return db.get_all_tickets()

@router.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, req: TicketStatusRequest):
    db.update_ticket_status(ticket_id, req.status)
    return {"message": "Updated"}

# ── Upload & Documents ────────────────────────────────────────────
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    ensure_folders()
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    save_path = os.path.join("data", file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        chunks = ingest_pdf(save_path)
        return {"message": f"Uploaded '{file.filename}'", "chunks_created": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/documents")
def list_documents():
    pdfs = get_all_pdfs()
    return {"total": len(pdfs), "documents": [os.path.basename(p) for p in pdfs]}

@router.get("/stats")
def get_stats():
    return db.get_stats()

from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import shutil, os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from backend.rag_pipeline import ingest_pdf, get_answer_stream, get_answer
from backend.utils import get_all_pdfs, faiss_index_exists, ensure_folders
from backend import database as db

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)

def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": payload["sub"], "role": payload["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

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

class FeedbackRequest(BaseModel):
    message_id: str
    session_id: str
    user_id: str
    rating: int  # 1 = thumbs up, 0 = thumbs down

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
    token = create_token(user["id"], user["role"])
    return {**user, "token": token}

# ── Chat Sessions ─────────────────────────────────────────────────
@router.post("/sessions")
def create_session(data: dict, current_user: dict = Depends(get_current_user)):
    session_id = db.create_session(current_user["user_id"], data.get("title", "New Chat"))
    return {"session_id": session_id}

@router.get("/sessions/{user_id}")
def get_sessions(user_id: str, current_user: dict = Depends(get_current_user)):
    return db.get_sessions(user_id)

@router.get("/messages/{session_id}")
def get_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    return db.get_messages(session_id)

class SaveMessageRequest(BaseModel):
    session_id: str
    user_id: str
    question: str
    answer: str

# ── Ask ───────────────────────────────────────────────────────────
@router.get("/health")
def health_check():
    return {"status": "ok", "message": "AI University Helpdesk is running"}

@router.post("/save-message")
def save_message(req: SaveMessageRequest, current_user: dict = Depends(get_current_user)):
    try:
        db.save_message(req.session_id, "user", req.question)
        db.save_message(req.session_id, "assistant", req.answer)
        sessions = db.get_sessions(req.user_id)
        for s in sessions:
            if s["id"] == req.session_id and s["title"] == "New Chat":
                db.update_session_title(req.session_id, req.question[:50])
    except Exception as e:
        print(f"Save message error: {e}")
    return {"status": "saved"}

@router.post("/ask-stream")
def ask_question_stream(request: QuestionRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        try:
            jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not faiss_index_exists():
        raise HTTPException(status_code=400, detail="No documents uploaded yet.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        return StreamingResponse(get_answer_stream(request.question, request.language), media_type="text/plain")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

import time

@router.post("/ask-sync", response_model=AnswerResponse)
def ask_question_sync(request: QuestionRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        try:
            jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not faiss_index_exists():
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload a university PDF first.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        start = time.time()
        answer = get_answer(request.question, request.language)
        response_time_ms = int((time.time() - start) * 1000)
        if request.session_id and request.user_id and request.user_id != "guest":
            try:
                db.save_message(request.session_id, "user", request.question)
                db.save_message(request.session_id, "assistant", answer)
                db.log_query(request.user_id, request.session_id, request.question, request.language, response_time_ms)
                sessions = db.get_sessions(request.user_id)
                for s in sessions:
                    if s["id"] == request.session_id and s["title"] == "New Chat":
                        db.update_session_title(request.session_id, request.question[:50])
            except Exception as db_err:
                print(f"DB save error (non-fatal): {db_err}")
        return AnswerResponse(answer=answer)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

# ── Tickets ───────────────────────────────────────────────────────
@router.post("/tickets")
def create_ticket(req: TicketRequest, current_user: dict = Depends(get_current_user)):
    ticket_id = db.create_ticket(req.user_id, req.user_name, req.session_id, req.issue)
    return {"ticket_id": ticket_id}

@router.get("/tickets")
def get_tickets(current_user: dict = Depends(get_admin_user)):
    return db.get_all_tickets()

@router.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, req: TicketStatusRequest, current_user: dict = Depends(get_admin_user)):
    db.update_ticket_status(ticket_id, req.status)
    return {"message": "Updated"}

# ── Upload & Documents ────────────────────────────────────────────
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), current_user: dict = Depends(get_admin_user)):
    ensure_folders()
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    save_path = os.path.join("data", file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        chunks = ingest_pdf(save_path)
        db.log_document_upload(file.filename, current_user["user_id"], chunks)
        return {"message": f"Uploaded '{file.filename}'", "chunks_created": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/documents")
def list_documents(current_user: dict = Depends(get_current_user)):
    pdfs = get_all_pdfs()
    return {"total": len(pdfs), "documents": [os.path.basename(p) for p in pdfs]}

@router.get("/document-logs")
def get_document_logs(current_user: dict = Depends(get_admin_user)):
    return db.get_document_uploads()

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    if req.rating not in (0, 1):
        raise HTTPException(status_code=400, detail="Rating must be 0 or 1")
    db.save_feedback(req.message_id, req.session_id, req.user_id, req.rating)
    return {"status": "saved"}

@router.get("/stats")
def get_stats(current_user: dict = Depends(get_current_user)):
    return db.get_stats()

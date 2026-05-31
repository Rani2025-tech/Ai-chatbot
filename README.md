# 🎓 AI-Powered University Helpdesk — NIST University

An intelligent RAG-based chatbot that answers student queries about NIST University Berhampur using university documents. Supports English, Hindi, and Odia languages.

## 🚀 Demo
![Helpdesk Demo](docs/architecture.png)

## 🛠️ Tech Stack
- **LLM** — Ollama (llama3.2:1b) — runs fully offline
- **RAG Framework** — LangChain
- **Vector Database** — FAISS
- **Embeddings** — HuggingFace (all-MiniLM-L6-v2)
- **Backend** — FastAPI + Uvicorn
- **Frontend** — Streamlit
- **Language Detection** — langdetect

## 💡 Features
- Ask questions about admissions, fees, hostel, placements, exams
- Upload any university PDF and get instant answers
- Multilingual support — English, Hindi, Odia
- Auto language detection
- REST API backend with Swagger docs at /docs
- Fully offline — no API keys needed

## 🏗️ Architecture
```
Student Question → Streamlit UI → FastAPI → RAG Pipeline → FAISS Search → Ollama LLM → Answer
```

## ⚙️ How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-university-helpdesk.git
cd ai-university-helpdesk
```

### 2. Create virtual environment
```bash
python -m venv rag_env
rag_env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama
Download Ollama from https://ollama.com
```bash
ollama pull llama3.2:1b
ollama serve
```

### 5. Create .env file
```env
OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434
DATA_PATH=data/
FAISS_INDEX_PATH=faiss_index/
```

### 6. Start FastAPI backend
```bash
python -m uvicorn backend.main:app --reload
```

### 7. Start Streamlit frontend
```bash
streamlit run frontend/app.py
```

### 8. Open browser
```
http://localhost:8501
```

## 📁 Project Structure
```
ai-university-helpdesk/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── routes.py        # API endpoints
│   ├── rag_pipeline.py  # RAG logic
│   └── utils.py         # Helper functions
├── frontend/
│   └── app.py           # Streamlit UI
├── data/                # University PDFs
├── docs/                # Architecture diagram
├── .env                 # Config (not uploaded)
├── requirements.txt
└── README.md
```

## 🎯 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Check server status |
| POST | /api/upload | Upload university PDF |
| POST | /api/ask | Ask a question |
| GET | /api/documents | List uploaded PDFs |

## 👨‍💻 Built By
RANI NAYAK — NIST University Berhampur
```

Press `Ctrl + S`.

---

**Step 3 — update `requirements.txt`** — open it and replace with:
```
fastapi
uvicorn
streamlit
langchain
langchain-community
langchain-ollama
langchain-huggingface
faiss-cpu
pypdf
python-dotenv
requests
python-multipart
sentence-transformers
langdetect
reportlab
beautifulsoup4
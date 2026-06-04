import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")

# ── Global Cache ─────────────────────────────────────────────────
_embeddings_cache  = None
_vectorstore_cache = None
_llm_cache         = None

def get_embeddings():
    global _embeddings_cache
    if _embeddings_cache is None:
        print("Loading embeddings model (first time only)...")
        _embeddings_cache = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings_cache

def load_vectorstore() -> FAISS:
    global _vectorstore_cache
    if _vectorstore_cache is None:
        print("Loading FAISS index (first time only)...")
        try:
            # allow_dangerous_deserialization=True is safe here because the
            # FAISS index is generated internally by this app (rebuild_index.py)
            # and never loaded from untrusted external sources.
            _vectorstore_cache = FAISS.load_local(
                FAISS_INDEX_PATH,
                get_embeddings(),
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"FAISS load error: {e}")
            raise RuntimeError(
                f"Failed to load FAISS index from '{FAISS_INDEX_PATH}'. "
                f"Run 'python rebuild_index.py' to rebuild it. Error: {e}"
            )
    return _vectorstore_cache

def get_llm():
    global _llm_cache
    if _llm_cache is None:
        print("Initializing LLM (first time only)...")
        _llm_cache = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
    return _llm_cache

# ── Shared Prompt ─────────────────────────────────────────────────
PROMPT = PromptTemplate.from_template("""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a friendly and helpful AI assistant for NIST University Berhampur Odisha. Your name is NIST Bot.
Be warm, polite and conversational. For greetings like "hi", "hello", "hey" — respond warmly and introduce yourself.
When answering university questions, use ONLY the exact facts, numbers, and names from the context below.
Do NOT invent, guess, or add any information that is not explicitly written in the context.
If a specific number or detail is in the context, use it exactly as written.
Do NOT make up branch-wise fees, company names, or any figures not present in the context.
If the context is empty or irrelevant to the question, respond naturally as a friendly assistant.
{lang_instruction}
<|eot_id|><|start_header_id|>user<|end_header_id|>
Context:
{context}

Question: {question}

Remember: Be friendly and helpful. For university questions, use ONLY the information from the context above.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>""")

# ── Hindi/Odia keyword translations ──────────────────────────────
HINDI_TRANSLATIONS = {
    "फीस": "fees", "शुल्क": "fees", "कीमत": "cost",
    "एडमिशन": "admission", "प्रवेश": "admission",
    "हॉस्टल": "hostel", "छात्रावास": "hostel",
    "कंपनी": "company", "कंपनियां": "companies",
    "प्लेसमेंट": "placement", "नौकरी": "job",
    "कोर्स": "course", "पाठ्यक्रम": "course",
    "कैंपस": "campus", "परिसर": "campus"
}

ODIA_TRANSLATIONS = {
    "ଫି": "fees", "ଶୁଳ୍କ": "fees",
    "ଆଡମିଶନ": "admission", "ପ୍ରବେଶ": "admission",
    "ହଷ୍ଟେଲ": "hostel", "ଛାତ୍ରାବାସ": "hostel",
    "କମ୍ପାନୀ": "company", "କମ୍ପାନୀମାନେ": "companies",
    "ପ୍ଲେସମେଣ୍ଟ": "placement", "ଚାକିରି": "job",
    "କୋର୍ସ": "course", "ପାଠ୍ୟକ୍ରମ": "course",
    "କ୍ୟାମ୍ପସ": "campus", "ପରିସର": "campus"
}

LANGUAGE_INSTRUCTIONS = {
    "en": "Answer in English with complete details.",
    "hi": "Answer in Hindi language only. Use Devanagari script. Provide complete details with specific numbers, amounts, and names. Do not use any English words.",
    "or": "Answer in Odia language only. Use Odia script (ଓଡ଼ିଆ ଲିପି). Provide complete details with specific numbers, amounts, and names. Do not use any English words. Write everything in Odia."
}

# ── Shared helper functions ───────────────────────────────────────
def translate_for_search(question: str, lang: str) -> str:
    search_question = question
    if lang == "hi":
        for hindi, english in HINDI_TRANSLATIONS.items():
            search_question = search_question.replace(hindi, english)
    elif lang == "or":
        for odia, english in ODIA_TRANSLATIONS.items():
            search_question = search_question.replace(odia, english)
    return search_question

def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)

def prepare_prompt(question: str, language: str):
    from backend.utils import detect_language
    lang = detect_language(question) if language == "auto" else language
    search_question = translate_for_search(question, lang)
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, "Answer in English.")

    vectorstore = load_vectorstore()
    retriever   = vectorstore.as_retriever(search_kwargs={"k": 10})
    docs        = retriever.invoke(search_question)
    context     = format_docs(docs)

    final_prompt = PROMPT.format(
        context=context,
        question=question,
        lang_instruction=lang_instruction
    )
    return final_prompt

# ── PDF Ingestion ─────────────────────────────────────────────────
def ingest_pdf(pdf_path: str):
    loader   = PyPDFLoader(pdf_path)
    docs     = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks   = splitter.split_documents(docs)

    embeddings = get_embeddings()

    if os.path.exists(FAISS_INDEX_PATH):
        try:
            existing = FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            existing.add_documents(chunks)
            existing.save_local(FAISS_INDEX_PATH)
        except Exception as e:
            print(f"Existing index corrupted, rebuilding from scratch: {e}")
            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(FAISS_INDEX_PATH)
        # Reset cache so new docs are picked up
        global _vectorstore_cache
        _vectorstore_cache = None
        print(f"Merged {len(chunks)} chunks into existing FAISS index")
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)
        print(f"Created new FAISS index with {len(chunks)} chunks")

    return len(chunks)

# ── Answer functions ──────────────────────────────────────────────
def get_answer(question: str, language: str = "auto") -> str:
    try:
        import html as _html
        final_prompt = prepare_prompt(question, language)
        result = get_llm().invoke(final_prompt)
        content = result.content if hasattr(result, 'content') else str(result)
        return _html.unescape(content)
    except Exception as e:
        print(f"Error in get_answer: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def get_answer_stream(question: str, language: str = "auto"):
    try:
        import html as _html
        final_prompt = prepare_prompt(question, language)
        for token in get_llm().stream(final_prompt):
            content = token.content if hasattr(token, 'content') else str(token)
            yield _html.unescape(content)
    except Exception as e:
        print(f"Error in get_answer_stream: {str(e)}")
        import traceback
        traceback.print_exc()
        yield f"Error: {str(e)}"
